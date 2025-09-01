#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Use the existing Landsat fractional cover model to calculate
fractional cover for Sentinel-2 imagery.

"""
import logging

import click
import coloredlogs
import numpy as np
from scipy.ndimage import median_filter
try:
    from rss_da import qvf
    from rsc.utils import DNscaling, history, spectra
except ImportError:
    _has_rsc = False
else:
    _has_rsc = True

import sys
import tflite_runtime.interpreter as tflite
from fractionalcover3 import unmixcover
from fractionalcover3.data import get_model
from osgeo import gdal, gdal_array
from rios import applier

from fractionalcover3 import __version__
gdal.UseExceptions()

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.WARNING)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--inimage",
    "-i",
    "sfcref10",
    help="Name of input surface reflectance file (10m bands)",
)
@click.option(
    "--outfile",
    "-o",
    help="Name of output fractional cover image (default is deduced from input)",
)
@click.option(
    "--sharpenswir/--no-sharpenswir",
    help="Use LTSE sharpening instead of relying on cubic convolution resample to get the 20m SWIR to 10m",
    default=False,
)
@click.option(
    "--fc_model",
    "-f",
    help="""Supply the name of the tensor flow model. \
If not supplied, the default version of the model distributed \
with the package will be used. If an integer 'n' is supplied it will use the nth
model distributed with the package. If a filename is supplied it will use the
model from the given path.""",
)
@click.option("-v", "--verbose", "verbosity", count=True, default=0)
@click.option('--allow-missing-metadata', is_flag=True)
@click.version_option(version=__version__)
def unmix_sentinel(sfcref10, outfile, sharpenswir, fc_model, verbosity,
    allow_missing_metadata):
    """Generate fractional cover image from a Sentinel2 surface reflectance image.

    Assume that the input is scaled surface reflectance, and is stage aba.
    Also assumes that 20m image (stage abb) is in the same path as the aba
    image.\f

    Args:
        sfcref10 (str): Path to the input surface reflectance image
        outfile (str): Filename of the output image. If not provided, will be based on the input filename.
        sharpenswir (bool): Use LTSE sharpening instead of relying on cubic convolution
            resample to get the 20m SWIR to 10m. Default is False.
        fc_model (integer|string): The desired inbuilt tensorflow model (integer 1-4), or the
          filename of a  model from the given path. If an integer 'n' is supplied it will use the nth
          model distributed with the package. If a filename is supplied it will use the
          model from the given path.
    """
    # setup logger
    for i in range(verbosity):
        coloredlogs.increase_verbosity()
    if not _has_rsc:
        logger.error(f"This script assumes module rsc is available.")
        sys.exit(1)

    # check valid inputs
    if qvf.stage(sfcref10) != "aba":
        logger.error(f"Input stage must be aba ({qvf.stage(sfcref10)} supplied)")
    sfcref20 = qvf.changestage(sfcref10, "abb")
    if not outfile:
        outfile = qvf.changestage(sfcref10, "aj0")
    logger.info(f"outfile={outfile}")
    sfcref20 = qvf.changestage(sfcref10, "abb")

    # select the fc model
    if not fc_model:
        # then we use the default one
        fc_tfmodel = get_model()
    else:
        # argument supplied so work out what it is
        try:
            nmodel = int(fc_model)
            fc_tfmodel = get_model(n=nmodel)
            logger.info(f"using package model no {nmodel}")
        except ValueError:
            fc_model_path = fc_model
            # now instantiate it
            try:
                fc_tfmodel = tflite.Interpreter(model_path=fc_model_path)
                logger.info(f"using model from file  {fc_model_path}")
            except ValueError:
                logger.error(f"Could not open path to model file {fc_model_path}")

    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    controls = applier.ApplierControls()

    infiles.sfcref10 = sfcref10
    infiles.sfcref20 = sfcref20
    outfiles.outimg = outfile

    otherargs.sfcRef10scaleStack = DNscaling.getDNscaleStackFromFile(sfcref10)
    otherargs.sfcRef20scaleStack = DNscaling.getDNscaleStackFromFile(sfcref20)
    otherargs.outNull = 255
    # Currently the input sensor is assumed to be S2A, because we do not have
    # any fudge for later S2. However, if we do fit such fudges, we need to
    # change this.
    otherargs.sen2sat = "A"
    otherargs.fc_model = fc_tfmodel
    fracScale = DNscaling.DNscale(
        gain=0.01,
        offset=0.0,
        units="fraction",
        nullValDN=otherargs.outNull,
        nullValUnits=-1.0,
    )
    otherargs.outDNscaleStack = DNscaling.DNscaleStack(
        [fracScale, fracScale, fracScale]
    )

    controls.setStatsIgnore(otherargs.outNull)
    controls.setReferenceImage(sfcref10)
    controls.setResampleMethod("cubic")
    # don't output any information
    null_log = open('/dev/null', 'w')
    controls.setLoggingStream(null_log)

    otherargs.sharpenswir = sharpenswir

    if sharpenswir:
        otherargs.windowsize = 7
        controls.setOverlap(otherargs.windowsize // 2)

    applier.apply(unmixSen2sfcRef, infiles, outfiles, otherargs, controls=controls)
    DNscaling.writeDNscaleStackToFile(outfile, otherargs.outDNscaleStack)
    # allow_missing_metadata = True implies strict = False
    addHistory(outfile, sfcref10, sfcref20, (not allow_missing_metadata))


def unmixSen2sfcRef(info, inputs, outputs, otherargs):
    """
    Called from RIOS

    Unmixes Sentinel-2 surface reflectance image to fractional cover, using
    the Landsat ETM+ model.

    I copied this function straight out of the unmixlandsat module, and it is
    possible it should be merged back in there eventually. Not sure...

    The inputs have separate arrays for the 10m and 20m bands, since the 20m
    bands are in a separate file. They are being resampled on-the-fly.

    The output array contains one layer for the fraction of
    each endmembers.

    Scaling is applied as per the otherargs.outDNscaleStack object.

    otherargs contains the following members:
      - sfcRef10scaleStack - the DNscaleStack object for the 10m bands.
      - sfcRef20scaleStack - the DNscaleStack object for the 20m bands.
      - outDNscaleStack - DNscaleStack object for scaling output image.
      - fc_model - The tensorflow model to be used.

    """
    # convert to reflectance and synthesise
    ref10 = otherargs.sfcRef10scaleStack.DNtoUnits(inputs.sfcref10)
    ref20 = otherargs.sfcRef20scaleStack.DNtoUnits(inputs.sfcref20)

    inNullVal = otherargs.sfcRef10scaleStack.scaleList[0].nullValUnits

    # Make a stack of the selected bands to correspond to ETM+ bands.
    # The selection of Sentinel-2 bands to match Landsat bands is fairly
    # obvious, except for the NIR band. There are two of these on
    # Sentinel-2, 8 and 8a. I have chosen the wide band 8 to match the
    # Landsat NIR band, because it is fairly close in width to the ETM+
    # NIR band, and is at 10m resolution. Sadly, it has a fairly different
    # response profile, especially on the right hand side of the curve.
    # The narrow band 8a is very close in response to the narrow Landsat-8
    # OLI NIR band, and less affected by water vapour as it avoids the
    # water vapour absorption band, but:
    #    (a) the current fractional cover model was fitted on ETM+; and
    #    (b) the narrow band 8a is at 20m resolution.
    # So, we have a trade-off between radiometrics and resolution,
    # and for the moment, I have chosen to go with resolution.
    swir = ref20[-2:]
    if otherargs.sharpenswir:
        nullmask = swir == inNullVal
        swir = sharpen(swir, ref10[2], otherargs.windowsize)
        swir[nullmask] = inNullVal
    ref = np.vstack((ref10, swir))

    # Fudge the Sentinel-2 reflectances to match Landsat-7, which is what
    # Peter actually used to fit the fractional cover model.
    ref = spectra.fudgeSen2toLandsat_sfcRef(
        ref, 7, inNullVal, inputSensor=otherargs.sen2sat
    )

    # Call the unmixing code.
    outUnmixNullVal = -10  # Fill output image with this value on errors.
    # use tensorflow
    logger.debug(f"unmixing block ({info.xblock}, {info.yblock})")
    tffractions = unmixcover.unmix_fractional_cover(
        ref, otherargs.fc_model, inNullVal, outUnmixNullVal
    )
    nOutputBands = 3
    # the tensorflow doesn't implicitly deal with null input
    # values, so we set them here
    badinputvalues = np.any(ref == inNullVal, axis=0)
    badoutputvalues = np.any(tffractions == outUnmixNullVal, axis=0)

    for i in range(3):
        tffractions[i] = np.where(badinputvalues, outUnmixNullVal, tffractions[i])
    # and pop the last entry off the scalestack if needed
    if len(otherargs.outDNscaleStack.scaleList) == 4:
        _ = otherargs.outDNscaleStack.scaleList.pop(3)
    fcLayers = np.clip(tffractions, 0, 2)
    fcLayerSum = fcLayers.sum(axis=0) + np.finfo("float32").eps
    fractions = fcLayers / fcLayerSum

    # clamp output values. Pixels that are poorly modelled, e.g. water,
    # can cause large values to be predicted. These need to be clamped
    # or they causes problems when scaled and converted to Byte.
    # I use 254 here, because 255 is interpreted as a null value
    # and gets mapped to -1.0
    maxVals = otherargs.outDNscaleStack.DNtoUnits(np.array([254] * nOutputBands))
    maxVals.shape = (nOutputBands, 1, 1)
    maxVals = np.ones(fractions.shape) * maxVals
    clampArea = fractions > maxVals
    fractions[clampArea] = maxVals[clampArea]

    # Data is only valid if a fraction exists for all values in the pixels.
    badFractionImage = np.logical_or(badinputvalues, badoutputvalues)
    for idx, scaleStack in enumerate(otherargs.outDNscaleStack.scaleList):
        dnScale = otherargs.outDNscaleStack.scaleList[idx]
        fractions[idx][badFractionImage] = dnScale.nullValUnits

    # Apply scaling and convert array to the correct type.
    outArray = otherargs.outDNscaleStack.unitsToDN(fractions)
    outDType = gdal_array.GDALTypeCodeToNumericTypeCode(gdal.GDT_Byte)
    outArray = outArray.astype(outDType)

    # Set the output
    outputs.outimg = outArray


def sharpen(swir, red, windowsize):
    """
    Sharpen the given swir against the given red, using LTSE algorithm, with
    the given window size. The swir argument is of shape (2, nRows, nCols),
    being both swir bands, while the red is of shape (nRows, nCols).
    """
    ratio = swir / red
    windowRatio = np.array([median_filter(ratio[i], size=windowsize) for i in [0, 1]])
    swirSharpened = windowRatio * red
    # Anywhere that red is zero, just use the unsharpened swir
    nanmask = np.isnan(swirSharpened)
    swirSharpened[nanmask] = swir[nanmask]
    return swirSharpened


def addHistory(outfile, sfcref10, sfcref20, strict):
    """
    Add processing history
    """
    opt = {}
    opt[
        "DESCRIPTION"
    ] = """
        Fractional vegetation cover v3.0 for Sentinel-2. This implementation is
        just the existing Landsat model applied directly to the corresponding
        bands of Sentinel-2, after fudging them to look like Landsat using
        the adjustments published in Flood (2017).

	    Output is a 3 band image, with bands bare, green and Non-Green. Each
        pixel represesents percentage cover of each component (scaled between
        0 and 100).
    """
    parents = [sfcref10, sfcref20]
    history.insertMetadataFilename(outfile, parents, opt, strict=strict)


if __name__ == "__main__":
    unmix_sentinel()
