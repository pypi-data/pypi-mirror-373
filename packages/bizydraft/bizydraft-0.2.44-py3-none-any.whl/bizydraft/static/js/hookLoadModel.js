import { app } from "../../scripts/app.js";
import '../BizyAir/bizyair_frontend.js'
import { hideWidget } from './tool.js'

// 白名单配置 - 不符合正则表达式的节点名称和对应的模型类型
const WHITELIST_NODES = {
    "LayerMask: YoloV8Detect": "Detection",
    "Lora Loader Stack (rgthree)": "LoRa",
    "easy loraNames": "LoRa",
    "easy loraStack": "LoRa",
    "Load Lora": "LoRa",
    "Intrinsic_lora_sampling": "LoRa",
    "ADE_LoadAnimateDiffModel": "Checkpoint",
    "ADE_AnimateDiffLoRALoader": "LoRa",
    "easy ultralyticsDetectorPipe": "Detection",
    "UltralyticsDetectorProvider": "Detection",
    "ONNXDetectorProvider": "Detection",
    "SAMLoader": "Detection",
    "easy samLoaderPipe": "Detection",
    "WanVideoModelLoader": "UNet",
    "LoadWanVideoT5TextEncoder": "CLIP",
    "WanVideoLoraSelect": "LoRa",
    "LoadFramePackModel": "Checkpoint",
};
const HAZY_WHITELIST_NODES = {

}

const possibleWidgetNames=[
    "clip_name",
    "clip_name1",
    "clip_name2",
    "clip_name3",
    "ckpt_name",
    "lora_name",
    "name",
    "lora",
    "lora_01",
    "lora_02",
    "lora_03",
    "lora_04",
    "lora_1_name",
    "lora_2_name",
    "lora_3_name",
    "lora_4_name",
    "lora_5_name",
    "lora_6_name",
    "lora_7_name",
    "lora_8_name",
    "lora_9_name",
    "lora_10_name",
    "lora_11_name",
    "lora_12_name",
    "model_name",
    "control_net_name",
    "ipadapter_file",
    "unet_name",
    "vae_name",
    "model",
    "instantid_file",
    "pulid_file",
    "style_model_name",
    "yolo_model"
]

// 根据节点名称匹配模型类型
function getModelTypeFromNodeName(nodeName) {
    if (/bizyair/i.test(nodeName)) {
        return null;
    }
    // 首先检查白名单
    if (WHITELIST_NODES.hasOwnProperty(nodeName)) {
        console.log(`白名单匹配: ${nodeName} -> ${WHITELIST_NODES[nodeName]}`);
        return WHITELIST_NODES[nodeName];
    }
    const HAZY_WHITELIST_NODES_KEYS = Object.keys(HAZY_WHITELIST_NODES);
    const thisKey = HAZY_WHITELIST_NODES_KEYS.find(key => nodeName.toLowerCase().includes(key.toLowerCase()));
    if (thisKey) {
        console.log(`模糊白名单匹配: ${nodeName} -> ${HAZY_WHITELIST_NODES[thisKey]}`);
        return HAZY_WHITELIST_NODES[thisKey];
    }


    // 然后使用正则表达式匹配
    const regex = /^(\w+).*Loader.*/i;
    const match = nodeName.match(regex);
    if (match) {
        return match[1];
    }
    return null;
}

function createSetWidgetCallback(modelType, selectedBaseModels = []) {
    return function setWidgetCallback() {
        const targetWidget = this.widgets.filter(widget => possibleWidgetNames.includes(widget.name));
        targetWidget.forEach((wdt, index) => {
            wdt.value = wdt.value || "to choose"
            wdt.mouse = function(e, pos, canvas) {
                try {
                    if (e.type === "pointerdown" || e.type === "mousedown" || e.type === "click" || e.type === "pointerup") {
                        e.preventDefault();
                        e.stopPropagation();
                        e.widgetClick = true;

                        const currentNode = this.node;

                        if (!currentNode || !currentNode.widgets) {
                            console.warn("Node or widgets not available");
                            return false;
                        }

                        if (typeof bizyAirLib !== 'undefined' && typeof bizyAirLib.showModelSelect === 'function') {
                            bizyAirLib.showModelSelect({
                                modelType: [modelType],
                                selectedBaseModels,
                                onApply: (version, model) => {
                                    if (!currentNode || !currentNode.widgets) return;

                                    const currentLora = currentNode.widgets.filter(widget => possibleWidgetNames.includes(widget.name));
                                    let currentModel;

                                    if (index === 0) {
                                        currentModel = currentNode.widgets.find(w => w.name === "model_version_id");
                                    } else {
                                        const fieldName = `model_version_id${index + 1}`;
                                        currentModel = currentNode.widgets.find(w => w.name === fieldName);
                                    }

                                    if (model && currentModel && version) {
                                        currentLora[index].value = model;

                                        currentModel.value = version.id;
                                        currentNode.setDirtyCanvas(true);
                                    }
                                }
                            });
                        } else {
                            console.error("bizyAirLib not available");
                        }
                        return false;
                    }
                } catch (error) {
                    console.error("Error handling mouse event:", error);
                }
            };

            // wdt.node = this;
            wdt.options = wdt.options || {};
            wdt.options.values = () => [];
            wdt.options.editable = false;
            wdt.clickable = true;
            wdt.processMouse = true;
        });
    }
}

function setupNodeMouseBehavior(node, modelType) {
    hideWidget(node, "model_version_id");

    // 只设置必要的状态信息，不修改onMouseDown（已在上面的扩展中处理）
    if (!node._bizyairState) {
        node._bizyairState = {
            lastClickTime: 0,
            DEBOUNCE_DELAY: 300,
            modelType: modelType
        };
    }
}

app.registerExtension({
    name: "bizyair.hook.load.model",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        localStorage.removeItem('workflow')
        sessionStorage.clear()
        const interval = setInterval(() => {
            if (window.switchLanguage) {
                window.switchLanguage('zh')
                clearInterval(interval)
            }
        }, 100)
        const modelType = getModelTypeFromNodeName(nodeData.name);
        if (modelType) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                try {
                    const targetWidget = this.widgets.filter(widget => possibleWidgetNames.includes(widget.name));
                    // 为每个targetWidget添加对应的model_version_id字段
                    targetWidget.forEach((widget, index) => {
                        let model_version_id;
                        if (index === 0) {
                            // 第一个保持原名
                            model_version_id = this.widgets.find(w => w.name === "model_version_id");
                            if (!model_version_id) {
                                model_version_id = this.addWidget("hidden", "model_version_id", "", function(){
                                }, {
                                    serialize: true,
                                    values: []
                                });
                            }
                        } else {
                            // 从第二个开始使用新名称
                            const fieldName = `model_version_id${index + 1}`;
                            model_version_id = this.widgets.find(w => w.name === fieldName);
                            if (!model_version_id) {
                                model_version_id = this.addWidget("hidden", fieldName, "", function(){
                                }, {
                                    serialize: true,
                                    values: []
                                });
                            }
                        }
                    });

                    const result = onNodeCreated?.apply(this, arguments);
                    let selectedBaseModels = [];
                    // if (modelType === 'Checkpoint') {
                    //     selectedBaseModels = ['SDXL', 'Pony', 'SD 3.5', 'Illustrious']
                    // }
                    createSetWidgetCallback(modelType, selectedBaseModels).call(this);
                    return result;
                } catch (error) {
                    console.error("Error in node creation:", error);
                }
            };
        }
    },
    async nodeCreated(node) {
        const modelType = getModelTypeFromNodeName(node?.comfyClass);

        if (modelType) {
            setupNodeMouseBehavior(node, modelType);
        }
    }
})
