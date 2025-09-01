#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import click
import coloredlogs
import numpy as np
try:
    from rss_da import qvf
    from rsc.utils import DNscaling, history, spectra
except ImportError:
    _has_rsc = False
else:
    _has_rsc = True

import sys
import platform

IS_SILICON_MAC = (sys.platform == "darwin" and platform.machine() == "arm64")

if IS_SILICON_MAC:
    # on macOS-ARM (M1/M2/...): use full TF-Lite
    import tensorflow.lite as tflite
else:
    # on other platforms: use tflite_runtime package
    import tflite_runtime.interpreter as tflite

from fractionalcover3 import unmixcover
from fractionalcover3.data import get_model
from osgeo import gdal, gdal_array
from rios import applier

from fractionalcover3 import __version__

gdal.UseExceptions()

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.WARNING)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--inimage", "-i", help="Input image (stage dbg).")
@click.option(
    "--outimage", "-o", help="Output image. If specified the stage must be stage dp0"
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
@click.option("-v", "--verbose", "verbosity", count=True)
@click.option('--allow-missing-metadata', is_flag=True)
@click.version_option(version=__version__)
def fractional_cover_surface_reflectance(
    inimage, allow_missing_metadata, outimage=None, fc_model=None, verbosity=0,
    
):
    """Generate fractional cover imager from a surface reflectance image.

    Assume that the input is scaled surface reflectance, and is stage
    dbg or dbk under the JRSRP stage name guidelines.\f

    Args:
        inimage (str): Filename for the input image
        outimage (str): Filename of the output image. If not provided, will be based on the input filename.
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
    # check valid input file
    if qvf.stage(inimage) != "dbg":
        logger.error(f"Input stage must be dbg ({qvf.stage(inimage)} supplied)")

    # fix up the default values
    if not outimage:
        outimage = qvf.changestage(inimage, "dp0")
    logger.info(f"outimage={outimage}")

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

    # so we have everything we need. Now do the processing
    inFiles = applier.FilenameAssociations()
    outFiles = applier.FilenameAssociations()
    otherArgs = applier.OtherInputs()
    otherArgs.outNull = 255
    otherArgs.fc_model = fc_tfmodel
    otherArgs.inDNscaleStack = DNscaling.getDNscaleStackFromFile(inimage)

    fracScale = DNscaling.DNscale(
        gain=0.01,
        offset=0.0,
        units="fraction",
        nullValDN=otherArgs.outNull,
        nullValUnits=-1.0,
    )
    otherArgs.outDNscaleStack = DNscaling.DNscaleStack(
            [fracScale, fracScale, fracScale]
        )
    otherArgs.isOLI = qvf.isLandsatOLI(inimage)
    otherArgs.stage = qvf.stage(inimage)
    inFiles.inimage = inimage
    outFiles.outimage = outimage
    logger.info("Predicting cover")
    applier.apply(unmixTMSurf, inFiles, outFiles, otherArgs)
    logger.info(f"Adding metadata to {outimage}")
    # strict is True or False
    # allow_missing_metadata implies strict is False
    insertHistoryMeta(inimage, outimage, (not allow_missing_metadata))
    # insert scaling
    DNscaling.writeDNscaleStackToFile(outimage, otherArgs.outDNscaleStack)


def unmixTMSurf(info, inputs, outputs, otherArgs):
    """
    Unmixes Landsat 5 TM image from surface reflectance data.

    This user function for an applier unmixes a Landsat 5 TM image assumed to be in a 
    surface reflectance stage (dbf or dbg). The output array consists of one layer for 
    the fraction of each endmember, in addition to layers for the sum of the fractions 
    and the model residual. Output scaling is managed according to the provided 
    DNscaleStack object in otherArgs.

    :param info: Information about the applier environment.
    :param inputs: Input data stack for the function.
    :param outputs: Array to be populated with the unmixing results.
    :param otherArgs: Arguments and parameters required for processing.
    :type info: dict
    :type inputs: list
    :type outputs: list
    :type otherArgs: dict

    :key inDNscaleStack: DNscaleStack object for input image scaling.
    :key outDNscaleStack: DNscaleStack object for output image scaling.
    :key fc_model: (Optional) File path to the TensorFlow model.

    :return: None
    """
    # convert to reflectance and synthesise
    ref = otherArgs.inDNscaleStack.DNtoUnits(inputs.inimage)
    inNullVal = otherArgs.inDNscaleStack.scaleList[0].nullValUnits
    if otherArgs.isOLI:
        # Strip off the OLI band 1 (if dbg)
        if otherArgs.stage == 'dbg':
            ref = ref[1:]
        # Fudge the reflectance values to look like Landsat-7 ETM+
        # values, since this is what the cover model was fitted with.
        ref = spectra.fudgeOLItoETM_sfcRef(ref, inNullVal)
    # Call the unmixing code.
    logger.debug(f"unmixing block ({info.xblock}, {info.yblock})")
    outUnmixNullVal = -10  # Fill output image with this value on errors.
    tffractions = unmixcover.unmix_fractional_cover(
        ref, otherArgs.fc_model, inNullVal, outUnmixNullVal
    )
    nOutputBands = 3
    badinputvalues = np.any(ref == inNullVal, axis=0)
    badoutputvalues = np.any(tffractions == outUnmixNullVal, axis=0)

    # and pop the last entry off the scalestack if needed
    if len(otherArgs.outDNscaleStack.scaleList) == 4:
        _ = otherArgs.outDNscaleStack.scaleList.pop(3)

    fcLayers = np.clip(tffractions, 0, 2)
    fcLayerSum = fcLayers.sum(axis=0) + np.finfo("float32").eps
    fractions = fcLayers / fcLayerSum

    # clamp output values. Pixels that are poorly modelled, e.g. water,
    # can cause large values to be predicted. These need to be clamped
    # or they causes problems when scaled and converted to Byte.
    fractions[fractions > 1.0 ] = 1.0

    # Set output null value.
    # Data is only valid if a fraction exists for all values in the pixels.
    # the tensorflow model will provide valid output everywhere
    # so only badinputs should be bad output
    badLocations = (badinputvalues) | (badoutputvalues)
    for idx, scaleStack in enumerate(otherArgs.outDNscaleStack.scaleList):
        dnScale = otherArgs.outDNscaleStack.scaleList[idx]
        fractions[idx][badLocations] = dnScale.nullValUnits

    # Apply scaling and convert array to the correct type.

    outArray = otherArgs.outDNscaleStack.unitsToDN(fractions)
    outDType = gdal_array.GDALTypeCodeToNumericTypeCode(gdal.GDT_Byte)
    outArray = outArray.astype(outDType)

    # Set the output

    outputs.outimage = outArray


def insertHistoryMeta(inimage, outimage, strict=True):
    """
    Inserts meta data and history into the unmixed image.
    """

    meta = {}
    meta["LAYER_NAMES"] = "bare, green, non_green"
    meta[
        "DESCRIPTION"
    ] = """
        Fractional cover version 3

        A three band image as follows:
        Layer 1. Bare fraction
        Layer 2. Green fraction
        Layer 3. Non-green fraction
        """
    history.insertMetadataFilename(outimage, [inimage], meta, strict=strict)


if __name__ == "__main__":
    fractional_cover_surface_reflectance()
