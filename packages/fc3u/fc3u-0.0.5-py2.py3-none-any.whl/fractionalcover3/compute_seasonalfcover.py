# -*- coding: utf-8 -*-
"""
Compute seasonal fractional cover from seasonal surface reflectance.

For landsat, we can save a lot of processing and disk space if we
make our seasonal fractional cover product from seasonal surface
reflectance. That is, instead of making single date fractional 
cover images, then taking the medoid of that, we take a pre-prepared
seasonal surface reflectance product, and just calculate the fractional
cover from that.

One issue is that the seasonal surface reflectance won't have the
water masks applied. So we apply these, but use the code file to work
out which mask needs to be applied to which pixel.

Another issue is that in the landsat 8 era, the seasonal surface 
reflectance is a composite of only landsat 8 (that is, its not a mix
of landsat 7 and landsat8). This means that a product from a landsat
8 surface reflectance composite image will likely have more missing data
than if you created all the single date fractional cover images based
on both l8 and l7, and then composited that.

"""
import logging
import os
import subprocess

import click
import coloredlogs
import numpy as np
from rss_da import qv
from rss_da import qvf
import sys
from fractionalcover3 import __version__
from osgeo import gdal
from rios import applier
from rsc.utils import DNscaling, history, masks

gdal.UseExceptions()

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.WARNING)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--inimage", "-i", help="Input image (stage dbi).")
@click.option(
    "--outimage", "-o", help="Output image. If specified the stage must be stage dpb"
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
@click.version_option(version=__version__)
def seasonal_fractional_cover_surface_reflectance(
    inimage, outimage=None, fc_model=None, verbosity=0
):
    """Generate seasonal fractional cover image from a seasonal surface reflectance image.

    Assume that the input is scaled seasonal surface reflectance, and is stage
    dbi under the JRSRP stage name guidelines.\f

    We also assume that the code file for the dbi is also in the same directory
    as the dbi file.\f

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

    if not qvf.stage(inimage) == "dbi":
        logger.error(f"Input stage must be dbi ({qvf.stage(inimage)} supplied)")
        sys.exit(2)

    if not outimage:
        # depends on the input
        outstage = 'dpb'
        outimage = qvf.changestage(inimage, outstage)
    logger.info(f"outimage={outimage}")

    # do as much set up early, so if something goes wrong
    # we identify it before running the fractional cover routine
    codefile = qvf.changestage(inimage, "dbj")
    watermasks = get_watermasks(codefile)
    # recall the watermasks
    qv.recallToHere(watermasks)
    maskerList = [masks.Masker(maskfile) for maskfile in watermasks]

    inFiles = applier.FilenameAssociations()
    outFiles = applier.FilenameAssociations()
    otherArgs = applier.OtherInputs()
    inFiles.inimage = qvf.changestage(inimage, "dpbinterim")
    inFiles.codeimage = codefile
    inFiles.watermasks = watermasks

    # generate the infile
    # construct the commandline
    cmd = ["-i", inimage, "-o", inFiles.inimage]
    if fc_model:
        cmd.extend(["-f", fc_model])
    if verbosity > 0:
        cmd.append("-" + "".join(["v"] * verbosity))
    cmd = ["compute_fractionalcover.py"] + cmd
    logger.info(f"running command {cmd}")
    subprocess.check_call(cmd)
    logger.info("done")

    inscale_stack = DNscaling.getDNscaleStackFromFile(inFiles.inimage)
    otherArgs.null_vals = [obj.nullValDN for obj in inscale_stack]
    # otherArgs.null_vals = [201, 201, 201]
    otherArgs.maskerList = maskerList

    outFiles.outimage = outimage
    controls = applier.ApplierControls()
    controls.setReferenceImage(inFiles.inimage)
    controls.setFootprintType(applier.BOUNDS_FROM_REFERENCE)

    logger.info(f"infile={inFiles.inimage}, outfile={outFiles.outimage}")
    applier.apply(multimask, inFiles, outFiles, otherArgs, controls=controls)

    # Add history
    opt = {}
    opt["DESCRIPTION"] = "Water masks applied"
    parents = [inimage] + watermasks
    history.insertMetadataFilename(outimage, parents, opt)

    # get rid of the interim file
    os.unlink(inFiles.inimage)


def multimask(info, inputs, outputs, otherArgs):
    """
    multi water masks
    """
    output = inputs.inimage
    # what we need to do, is to find all those
    # elements that are both water and selected
    # pixels
    for i, mask in enumerate(inputs.watermasks):
        # a value in the mask where the pixel value
        # is from that date should be masked
        # all the water from this mask:
        potential_mask = otherArgs.maskerList[i].mask(mask[0])
        # but only apply if the code pixel value is the same
        # as the position in the list of masks
        # (note, pixel values count from 1)
        to_mask = (inputs.codeimage[0] == (i + 1)) & (potential_mask)
        for band in range(inputs.inimage.shape[0]):
            output[band] = np.where(to_mask, otherArgs.null_vals[band], output[band])
    outputs.outimage = output


def get_watermasks(codefile):
    """Get a list of water masks from a codefile.

    A seasonal code file has information on which
    files were used to create a composite image.

    The filesnames are stored in the RAT, and order
    is important.

    Args:
        codefile (str): Filename of the code file.
    """

    ds = gdal.Open(codefile)
    band1 = ds.GetRasterBand(1)
    rat = band1.GetDefaultRAT()
    fnames = rat.ReadAsArray(1)
    # get the masks

    watermasks = []
    for fname in fnames:
        try:
            thismask = masks.getAvailableMaskname(fname.decode(), masks.MT_WATERNDX)
            watermasks.append(thismask)
        except masks.FilenameError:
            pass
    rat = None
    band1 = None
    ds = None
    return watermasks


if __name__ == "__main__":
    seasonal_fractional_cover_surface_reflectance()
