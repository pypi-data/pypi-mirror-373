const loadNodeList = [
    'LoadImage',
    'LoadImageMask',
    'LoadAudio',
    'LoadVideo',
    'Load3D',
    'VHS_LoadVideo'
]
const extMap = {
    'LoadImage': '.png,.jpg,.jpeg,.webp,.gif,.svg,.ico,.bmp,.tiff,.tif,.heic,.heif',
    'LoadImageMask': '.png,.jpg,.jpeg,.webp,.gif,.svg,.ico,.bmp,.tiff,.tif,.heic,.heif',
    'LoadAudio': '.mp3,.wav,.ogg,.m4a,.aac,.flac,.wma,.m4r',
    'LoadVideo': '.mp4,.mov,.avi,.mkv,.webm,.flv,.wmv,.m4v',
    'Load3D': '.glb,.gltf,.fbx,.obj,.dae,.ply,.stl',
    'VHS_LoadAudioUpload': '.mp3,.wav,.ogg,.m4a,.aac,.flac,.wma,.m4r',
    "VHS_LoadVideo": '.mp4,.mov,.avi,.mkv,.webm,.flv,.wmv,.m4v',
}
export function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
export const hideWidget = (node, widget_name) => {
    const widget = node.widgets.find(widget => widget.name === widget_name)
    if (!widget) {
        return
    }
    const originalComputeSize = widget.computeSize;
    const originalType = widget.type;

    widget.computeSize = () => [0, -4];
    widget.type = "hidden";
    widget.hidden = true
    widget.options = widget.options || {};
    widget.show = () => {
        widget.computeSize = originalComputeSize;
        widget.type = originalType;
        widget.height = undefined;
    };
}
export const computeIsLoadNode = (nodeName) => {

    return loadNodeList.includes(nodeName)
}
export const computeExt = (nodeName) => {

    return extMap[nodeName] || ''
}
/**
 * 判断节点名是否为模型加载类（不包含 bizyair）
 * @param {string} nodeName
 * @returns {boolean}
 */
function isModelLoaderType(nodeName) {
    const regex = /^(\w+).*Loader.*/i;
    return regex.test(nodeName);
}

/**
 * 处理 graphData.output
 * @param {Object} output - graphData.output 对象
 * @returns {Object} 处理后的新对象
 */
export function processGraphOutput(output) {
    const newOutput = JSON.parse(JSON.stringify(output));
    for (const key in newOutput) {
        const node = newOutput[key];
        // 1. 如果 class_type 在 loadNodeList 里，删除 inputs.image_name
        if (loadNodeList.includes(node.class_type) && node.inputs && node.inputs.image_name !== undefined) {
            delete node.inputs.image_name;
        }
        if (isModelLoaderType(node.class_type)) {
            delete newOutput[key];
        }
        // 2. 如果 class_type 满足 Loader 正则且不包含 bizyair，删除 inputs.model_version_id
        if (isModelLoaderType(node.class_type) && node.inputs) {
            if (node.inputs.model_version_id !== undefined) {
                delete node.inputs.model_version_id;
            }
            if (node.inputs.ckpt_name !== undefined) {
                delete node.inputs.ckpt_name;
            }
        }
    }
    return newOutput;
}
