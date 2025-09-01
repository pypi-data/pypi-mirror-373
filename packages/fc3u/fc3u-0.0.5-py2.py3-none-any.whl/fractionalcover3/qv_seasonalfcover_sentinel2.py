# -*- coding: utf-8 -*-
"""
Use the existing Landsat fractional cover model to calculate
fractional cover for Sentinel-2 imagery from seasonal surface
reflectance.

Requires watermasking.

"""
import logging
import click
import coloredlogs
import numpy as np
from rss_da import qv
from rss_da import qvf
import tflite_runtime.interpreter as tflite
from fractionalcover3 import __version__
from fractionalcover3 import unmixcover
from fractionalcover3 import compute_seasonalfcover as csf
from fractionalcover3.data import get_model
from osgeo import gdal, gdal_array
from rios import applier
from rsc.utils import DNscaling, history, masks
from rsc.utils import spectra
gdal.UseExceptions()


logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.WARNING)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--inimage",
    "-i",
    "seassfc",
    help="Name of input seasonal surface reflectance",
)
@click.option(
    "--outfile",
    "-o",
    help="Name of output fractional cover image (default is deduced from input)",
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
@click.version_option(version=__version__)
def unmix_sentinel(seassfc, outfile, fc_model, verbosity):
    """Generate fractional cover image from a Sentinel2 surface reflectance image.

    Assume that the input is a seasonal scaled surface reflectance, and is stage 
    abm, and assumes that code layer (stage abn) is in the same path as the abm
    image.\f

    Args:
        seassfc (str): Path to the input seasonal surface reflectance image
        outfile (str): Filename of the output image. If not provided, will be based on the input filename.
       fc_model (integer|string): The desired inbuilt tensorflow model (integer 1-4), or the
          filename of a  model from the given path. If an integer 'n' is supplied it will use the nth
          model distributed with the package. If a filename is supplied it will use the
          model from the given path.
    """
    # setup logger
    for i in range(verbosity):
        coloredlogs.increase_verbosity()

    # check valid inputs
    if qvf.stage(seassfc) != "abm":
        logger.error(f"Input stage must be abm ({qvf.stage(seassfc)} supplied)")
    seas_codelayer = qvf.changestage(seassfc, "abn")
    if not outfile:
        outfile = qvf.changestage(seassfc, "aj1")
    intermediate_outfile = qvf.changestage(outfile, 'intermediateaj1')
    logger.info(f"outfile={outfile}")

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

    infiles.seassfc = seassfc
    outfiles.outimg = intermediate_outfile

    otherargs.seassfcscaleStack = DNscaling.getDNscaleStackFromFile(seassfc)
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
    controls.setReferenceImage(seassfc)
    # don't output any information
    null_log = open('/dev/null', 'w')
    controls.setLoggingStream(null_log)
    logger.info("unmixing image")
    applier.apply(unmixSen2sfcRef, infiles, outfiles, otherargs, controls=controls)
    logger.info("done")
    # now do the masking:

    logger.info("preparing water masks")
    watermasks = csf.get_watermasks(seas_codelayer)
    logger.info(f"recalling {len(watermasks)} mask files")
    qv.recallToHere(watermasks)
    maskerList = [masks.Masker(maskfile) for maskfile in watermasks]
    
    inFiles = applier.FilenameAssociations()
    outFiles = applier.FilenameAssociations()
    otherArgs = applier.OtherInputs()
    inFiles.inimage = intermediate_outfile
    inFiles.codeimage = seas_codelayer
    inFiles.watermasks = watermasks
    outFiles.outimage = outfile
    otherArgs.maskerList = maskerList
    otherArgs.null_vals = [255, 255, 255]

    logger.info("applying masks")
    applier.apply(csf.multimask, inFiles, outFiles, otherArgs)
    logger.info("done")

    logger.info("Adding metadata")
    DNscaling.writeDNscaleStackToFile(outfile, otherargs.outDNscaleStack)
    addHistory(outfile, seassfc, seas_codelayer)



def unmixSen2sfcRef(info, inputs, outputs, otherargs):
    """
    Called from RIOS

    Unmixes Sentinel-2 seasonal surface reflectance image to fractional cover, using
    the Landsat ETM+ model.

    This is the same function as the one in qv_fractionalcover_sentinel2.py
    but with references to the 20m SWIR band removed. Its assumed that the 
    seasonal surface reflectance has done this already.

    """
    # convert to reflectance and synthesise
    ref10 = otherargs.seassfcscaleStack.DNtoUnits(inputs.seassfc)
    inNullVal = otherargs.seassfcscaleStack.scaleList[0].nullValUnits

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

    # Fudge the Sentinel-2 reflectances to match Landsat-7, which is what
    # Peter actually used to fit the fractional cover model.
    ref = spectra.fudgeSen2toLandsat_sfcRef(
        ref10, 7, inNullVal, inputSensor=otherargs.sen2sat
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


def addHistory(outfile, seassfc, seas_codelayer):
    """
    Add processing history
    """
    opt = {}
    opt[
        "DESCRIPTION"
    ] = """
        Fractional vegetation cover for Sentinel-2. This implementation is
        just the existing Landsat model applied directly to the corresponding
        bands of Sentinel-2, after fudging them to look like Landsat using
        the adjustments published in Flood (2017).
    """
    parents = [seassfc, seas_codelayer]
    history.insertMetadataFilename(outfile, parents, opt)




if __name__ == "__main__":
    unmix_sentinel()
