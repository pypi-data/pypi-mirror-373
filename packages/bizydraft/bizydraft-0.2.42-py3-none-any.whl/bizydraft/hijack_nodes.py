import re

from loguru import logger

try:
    from comfy_extras.nodes_video import LoadVideo
    from nodes import NODE_CLASS_MAPPINGS, LoadImage
except ImportError:
    logger.error(
        "failed to import ComfyUI nodes modules, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
    )
    exit(1)


class BizyDraftLoadVideo(LoadVideo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"file": (["choose your file"], {"video_upload": True})},
        }

    @classmethod
    def VALIDATE_INPUTS(s, *args, **kwargs):
        return True


class BizyDraftLoadImage(LoadImage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"image": (["choose your file"], {"image_upload": True})},
        }

    @classmethod
    def VALIDATE_INPUTS(s, *args, **kwargs):
        return True


CLASS_PATCHES = {
    # "LoadImage": BizyDraftLoadImage,
    # "LoadVideo": BizyDraftLoadVideo,
}

DATA_LOAD_CLASSES = [
    "LoadImage",
    "LoadVideo",
    "LoadImageMask",
    "LoadAudio",
    "Load3D",
    "LayerMask: YoloV8Detect",
    "Lora Loader Stack (rgthree)",
    "easy loraNames",
    "easy loraStack",
    "Load Lora",
    "Intrinsic_lora_sampling",
    "ADE_LoadAnimateDiffModel",
    "ADE_AnimateDiffLoRALoader",
    "easy ultralyticsDetectorPipe",
    "UltralyticsDetectorProvider",
    "ONNXDetectorProvider",
    "SAMLoader",
    "easy samLoaderPipe",
    "WanVideoModelLoader",
    "LoadWanVideoT5TextEncoder",
    "WanVideoLoraSelect",
]


def hijack_nodes():
    def _hijack_node(node_name, new_class):
        if node_name in NODE_CLASS_MAPPINGS:
            logger.warning(
                f"Node {node_name} already exists, replacing with {new_class.__name__}"
            )
        NODE_CLASS_MAPPINGS[node_name] = new_class

    # 特例情况，用手写的 class 替换
    for node_name, new_class in CLASS_PATCHES.items():
        _hijack_node(node_name, new_class)

    # 通用情况，正则匹配后，打通用patch、替换
    for node_name, base_class in NODE_CLASS_MAPPINGS.items():
        regex = r"^(?!BizyAir_)\w+.*Loader.*"
        match = re.match(regex, node_name, re.IGNORECASE)
        if (match and (node_name not in CLASS_PATCHES)) or (
            node_name in DATA_LOAD_CLASSES
        ):
            logger.debug(f"Creating patched class for {node_name}")
            patched_class = create_patched_class(base_class)
            NODE_CLASS_MAPPINGS[node_name] = patched_class


def create_patched_class(base_class, validate_inputs_func=None):
    class PatchedClass(base_class):
        pass

    if validate_inputs_func:
        PatchedClass.VALIDATE_INPUTS = classmethod(validate_inputs_func)
    else:
        PatchedClass.VALIDATE_INPUTS = classmethod(lambda cls, *a, **k: True)

    return PatchedClass
