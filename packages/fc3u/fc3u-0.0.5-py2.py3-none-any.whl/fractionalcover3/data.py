import importlib.resources as resources
# import tflite_runtime.interpreter as tflite
import sys
import platform

IS_SILICON_MAC = (sys.platform == "darwin" and platform.machine() == "arm64")

# if IS_SILICON_MAC:
#     # on macOS-ARM (M1/M2/...): use full TF-Lite
#     import tensorflow.lite as tflite
# else:
#     # on other platforms: use tflite_runtime package
#     import tflite_runtime.interpreter as tflite

from tensorflow import lite as tflite


def landsat7_refimage():
    """
    Returns a path to the example landsat 7 reflectance images.
    """
    refimagePath = resources.files("fractionalcover3") / "pkgdata/l7tmre_sub_20190511_dbgm3.img"
    return refimagePath


def sentinel2_refimage():
    """
    Returns a tuple path to the example sentinel2 reflectance images.
    """
    refimagePath10m = resources.files("fractionalcover3") / "pkgdata/cfmsre_sub_20200510_abam5.img"
    refimagePath20m = resources.files("fractionalcover3") /  "pkgdata/cfmsre_sub_20200510_abbm5.img"
    return (refimagePath10m, refimagePath20m)


# we have 4 candidate models
def get_model(n=2):
    """
    Get model number n.

    Args:
        n: the of the model to choose. There are 4
            available models, ordered by complexity, with the simplest
            first. n counts from 1. Default
            is the second model.

    Returns:
        A tensorflow lite interpreted model
        (tflite_runtime.interpreter.Interpreter)
    """
    data_dir = resources.files("fractionalcover3") / 'pkgdata/'

    available_models = [data_dir / "fcModel_32x32x32.tflite",
                        data_dir / "fcModel_64x64x64.tflite",
                        data_dir / "fcModel_256x64x256.tflite",
                        data_dir / "fcModel_256x128x256.tflite"]
    fc_model = tflite.Interpreter(model_path=str(available_models[n-1]))
    return fc_model
