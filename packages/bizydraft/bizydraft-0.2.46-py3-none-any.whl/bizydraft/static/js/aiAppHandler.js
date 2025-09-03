import { app } from "../../scripts/app.js";
import { setNodeParams, filterNodeWidgets, isConfigurableNode } from "./nodeParamsFilter.js";
import { processGraphOutput } from './tool.js';
import { focusNodeOnly, setGlobalReferences, setupCanvasClickHandler, removeCanvasClickHandler } from './nodeFocusHandler.js';
import { freezeWorkflow, unfreezeWorkflow, updateHighlightedNodes } from './freezeModeHandler.js';
// 状态变量
let selectedInputNodes = [];
let activeMode = null; // 当前活动的模式: "aiapp" 或 "export"
const originalNodeColors = new Map();
/**
 * 切换应用模式
 * @param {string} mode - 模式名称: "aiapp" 或 "export"
 * @param {boolean} enable - 是否启用
 * @param {boolean} isworkflow - 是否为工作流发布模式
 * @returns {boolean} 操作是否成功
 */
function toggleMode(mode, enable, isworkflow = false) {
    console.log(`${enable ? "启用" : "禁用"} ${mode} 模式`);
    if (enable) {
        activeMode = mode;
        highlightInputNodes();
        freezeWorkflow(isworkflow);

        // 在进入发布模式时获取并打印工作流数据
        if (mode === "export") {
            // 使用 Promise 包装 graphToPrompt 调用
            Promise.resolve().then(async () => {
                const graphData = await app.graphToPrompt();
                const processedOutput = processGraphOutput(graphData.output);
                // 添加来源标识
                const sourceInfo = { from: 'aiAppHandler_toggleMode' };
                // 构建新的数据格式
                const formattedData = {
                    prompt: processedOutput,
                    extra_data: {
                        extra_pnginfo: {
                            workflow: graphData.workflow
                        }
                    }
                };
                try {
                    const response = await fetch('/bizyair/workflow_io', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formattedData)
                    });
                    const responseData = await response.json();

                    // 保存节点参数信息
                    if (responseData && responseData.data && Array.isArray(responseData.data.inputs)) {
                        // 使用新模块保存节点参数信息
                        setNodeParams(responseData.data.inputs);
                    }

                    // 将响应发送给前端
                    window.parent.postMessage({
                        type: 'WORKFLOW_IO_RESPONSE',
                        data: responseData,
                        sourceInfo: sourceInfo
                    }, '*');
                } catch (error) {
                    window.parent.postMessage({
                        type: 'WORKFLOW_IO_ERROR',
                        error: error.message
                    }, '*');
                }
            });

            // 发送模式变更通知给父窗口
            window.parent.postMessage({
                type: 'EXPORT_MODE_CHANGED',
                enabled: true
            }, '*');
        }
        return true;
    } else {
        activeMode = null;
        //修复所有节点颜色
        selectedInputNodes = [];

        // 强制恢复所有节点颜色
        if (app && app.graph && app.graph._nodes) {
            for (const node of app.graph._nodes) {
                if (node) {
                    // 恢复原始颜色
                    const original = originalNodeColors.get(node.id);
                    if (original) {
                        node.color = original.color || undefined;
                        node.bgcolor = original.bgcolor || undefined;
                    } else {
                        // 如果没有原始颜色，设置为undefined
                        node.color = undefined;
                        node.bgcolor = undefined;
                    }
                    delete node._aiAppHighlighted;
                }
            }
            originalNodeColors.clear();
            app.canvas.setDirty(true, true);
        } else {
            restoreNodeColors();
        }

        unfreezeWorkflow();

        // 发送模式变更通知给父窗口
        if (mode === "export") {
            window.parent.postMessage({
                type: 'EXPORT_MODE_CHANGED',
                enabled: false
            }, '*');
        }

        return true;
    }
}

// 切换模式函数已实现通用逻辑，下面是为了兼容现有代码的别名
function enableAIAppMode() {
    return toggleMode("aiapp", true);
}

function disableAIAppMode() {
    return toggleMode("aiapp", false);
}

function toggleExportMode(params) {
    return toggleMode("export", params.enable === true, params.isworkflow === true);
}







// 高亮输入节点
function highlightInputNodes() {
    if (!app || !app.graph || !app.graph._nodes) return;

    // 保存原始颜色并设置高亮
    for (const node of app.graph._nodes) {
        // 保存原始颜色
        if (!originalNodeColors.has(node.id)) {
            originalNodeColors.set(node.id, {
                color: node.color,
                bgcolor: node.bgcolor
            });
        }

        // 只设置已选择的节点的颜色，其他节点保持原样
        if (selectedInputNodes.some(n => n.id === node.id)) {
            // 已选择的节点 - 紫色
            node.color = "#7C3AED";
            node.bgcolor = "#7C3AED22";
        }

        node._aiAppHighlighted = true;
    }

    // 刷新画布
    app.canvas.setDirty(true, true);
}

// 恢复节点颜色
function restoreNodeColors() {
    if (!app || !app.graph || !app.graph._nodes) return;

    for (const node of app.graph._nodes) {
        if (node && node._aiAppHighlighted) {
            // 恢复原始颜色
            const original = originalNodeColors.get(node.id);
            if (original) {
                node.color = original.color || undefined;
                node.bgcolor = original.bgcolor || undefined;
            } else {
                node.color = undefined;
                node.bgcolor = undefined;
            }

            delete node._aiAppHighlighted;
        }
    }

    // 清空保存的颜色
    originalNodeColors.clear();

    // 刷新画布
    app.canvas.setDirty(true, true);
}

// 选择节点
function selectInputNode(nodeId) {
    if (!app || !app.graph) return null;

    const node = app.graph.getNodeById(nodeId);
    if (!node) return null;

    // 检查节点是否已选择
    if (selectedInputNodes.some(n => n.id === nodeId)) {
        return null; // 节点已选择
    }

    // 提取节点信息
    const nodeInfo = extractNodeInfo(node);

    // 添加到选中列表
    selectedInputNodes.push(nodeInfo);

    // 更新节点样式
    node.color = "#7C3AED"; // 紫色
    node.bgcolor = "#7C3AED22";

    // 刷新画布
    app.canvas.setDirty(true, true);

    // 返回节点信息
    return nodeInfo;
}

// 从选择中移除节点
function deselectInputNode(nodeId) {
    // 统一 nodeId 类型为数字
    const id = typeof nodeId === 'string' ? parseInt(nodeId, 10) : nodeId;

    // 从列表中移除
    const index = selectedInputNodes.findIndex(n => n.id === id);
    if (index !== -1) {
        selectedInputNodes.splice(index, 1);
    }
    // 恢复节点颜色，确保类型正确
    const node = app.graph.getNodeById(id);
    if (node) {
        // 使用undefined而不是null，避免Zod schema验证错误
        node.color = undefined;
        node.bgcolor = undefined;
        delete node._aiAppHighlighted;
        app.canvas.setDirty(true, true);
    }
}

// 提取节点信息
function extractNodeInfo(node) {
    const nodeInfo = {
        id: node.id,
        type: node.type,
        comfyClass: node.comfyClass,
        title: node.title,
        widgets: []
    };

    // 处理widgets
    if (node.widgets && node.widgets.length > 0) {
        nodeInfo.widgets = node.widgets
            .filter(widget => widget.type !== "hidden" && !widget.disabled)
            .map(widget => {
                // 获取widget的值
                const widgetValue = widget.value || "";

                const widgetInfo = {
                    name: String(widget.name || ""),
                    value: widgetValue,
                    type: String(widget.type || "")
                };

                // 处理options属性
                if (widget.options && widget.options.values) {
                    widgetInfo.options = { values: [] };

                    if (Array.isArray(widget.options.values)) {
                        widgetInfo.options.values = [...widget.options.values];
                    } else if (typeof widget.options.values === 'function') {
                        try {
                            const values = widget.options.values();
                            if (Array.isArray(values)) {
                                widgetInfo.options.values = [...values];
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                }

                return widgetInfo;
            });
    }

    return nodeInfo;
}

// 更新节点参数
function updateInputNodeWidget(nodeId, widgetName, newValue) {
    if (!app || !app.graph) return false;

    const node = app.graph.getNodeById(nodeId);
    if (!node || !node.widgets) return false;

    const widget = node.widgets.find(w => w.name === widgetName);
    if (!widget) return false;

    // 更新widget值
    widget.value = newValue;

    // 执行回调
    if (typeof widget.callback === 'function') {
        try {
            widget.callback(newValue);
        } catch (e) {
            console.error(`执行widget回调出错: ${e.message}`);
        }
    }

    // 更新内部状态
    const nodeIndex = selectedInputNodes.findIndex(n => n.id === nodeId);
    if (nodeIndex !== -1) {
        const widgetIndex = selectedInputNodes[nodeIndex].widgets.findIndex(w => w.name === widgetName);
        if (widgetIndex !== -1) {
            selectedInputNodes[nodeIndex].widgets[widgetIndex].value = newValue;
        }
    }

    // 刷新画布
    node.setDirtyCanvas(true, true);

    return true;
}

// 获取所有选中的节点
function getSelectedInputNodes() {
    return JSON.parse(JSON.stringify(selectedInputNodes));
}

// 清空选中的节点
function clearSelectedInputNodes() {
    // 恢复节点颜色
    if (activeMode) {
        for (const node of app.graph._nodes) {
            if (node && selectedInputNodes.some(n => n.id === node.id)) {
                node.color = "#7C3AED"; // 紫色
                node.bgcolor = "#7C3AED22";
            }
        }
    }

    // 清空列表
    selectedInputNodes = [];

    // 刷新画布
    app.canvas.setDirty(true, true);

    return true;
}



// 选中节点并手动聚焦
function selectNodeAndFocus(nodeId) {
        if (!app || !app.graph) {
            return;
        }

        const node = app.graph.getNodeById(parseInt(nodeId, 10));
        if (!node) {
            console.error('找不到节点:', nodeId);
            return;
        }

        // 设置节点的 selected 属性
        for (const n of app.graph._nodes) {
            n.selected = n.id === node.id;
        }

        // 设置 selected_nodes
        if (app.canvas) {
            app.canvas.selected_nodes = [node];
        }

        //使用 app.canvas.centerOnNode
        if (app.canvas && typeof app.canvas.centerOnNode === 'function') {
            app.canvas.centerOnNode(node);
        }

        // 刷新画布
        if (app.canvas) {
            app.canvas.setDirty(true, true);
            if (typeof app.canvas.draw === 'function') {
                app.canvas.draw(true, true);
            }
        }

        return
}

// 保存原始节点颜色信息
function saveOriginalNodeColors(workflowId) {
    if (!app || !app.graph || !app.graph._nodes) return;

    const nodeColors = new Map();

    // 遍历所有节点，保存原始颜色
    for (const node of app.graph._nodes) {
        if (node) {
            // 确保颜色值类型正确，使用undefined而不是null
            nodeColors.set(node.id, {
                color: node.color || undefined,
                bgcolor: node.bgcolor || undefined
            });
        }
    }
    // 发送颜色信息到前端
    window.parent.postMessage({
        type: 'ORIGINAL_NODE_COLORS_SAVED',
        workflowId: workflowId,
        nodeColors: Array.from(nodeColors.entries())
    }, '*');

    console.log('已保存原始节点颜色信息，节点数量:', nodeColors.size);
}

// 监听 window 消息，处理 centerNode
window.addEventListener('message', function(event) {

    // 处理选中并聚焦节点
    if (event.data && event.data.type === 'selectNodeAndFocus' && event.data.nodeId !== undefined) {
        selectNodeAndFocus(event.data.nodeId);
    }

    // 处理保存原始节点颜色请求
    if (event.data && event.data.type === 'saveOriginalNodeColors' && event.data.workflowId !== undefined) {
        saveOriginalNodeColors(event.data.workflowId);
    }

    // 处理获取widget信息请求
    if (event.data && event.data.type === 'get_widget_info') {
        const { messageId, nodeId, widgetName } = event.data;

        let widget = null;
        let error = null;

        try {
            // 查找节点
            const node = app && app.graph ? app.graph.getNodeById(Number(nodeId)) : null;
            if (node && node.widgets) {
                widget = node.widgets.find(w => String(w.name) === String(widgetName));
                if (!widget) {
                    error = '未找到指定widget';
                } else {
                    // 保留所有非undefined的options属性
                    const safeOptions = widget.options ?
                        Object.fromEntries(
                            Object.entries(widget.options)
                                .filter(([_, value]) => value !== undefined)
                        ) :
                        {};

                    // 直接使用 widget.value，这是截图中显示蓝色高亮的值
                    const widgetValue = widget.value || "";
                    // 创建一个新的简化widget对象，只包含我们实际需要的属性
                    // 确保只使用可序列化的属性
                    let safeWidgetValue = "";
                    try {
                        // 测试是否可序列化
                        JSON.stringify({value: widgetValue});
                        safeWidgetValue = widgetValue;
                        safeWidgetValue = safeWidgetValue.replace(/pasted\/http/g, 'http');
                    } catch (e) {
                        console.error('[aiAppHandler] 值不可序列化:', e);
                        // 使用安全的字符串值
                        safeWidgetValue = String(widgetValue) || "";
                    }

                    widget = {
                        name: widget.name || "",
                        value: safeWidgetValue,  // 使用安全处理后的值
                        type: widget.type || "string",
                        options: safeOptions,
                        displayName: widget.displayName || widget.label || widget.name || "",
                        tooltip: widget.tooltip || "", // 添加 tooltip 字段
                        node_title: node.title || "",
                        node_type: node.type || "",
                        node_comfyClass: node.comfyClass || ""
                    };
                    console.log('[aiAppHandler] 处理后的widget', widget);
                }
            } else {
                error = '未找到指定节点或节点没有widgets';
            }
        } catch (e) {
            console.error('[aiAppHandler] 查找节点/widget过程出错', e);
            error = e.message;
        }

        try {
            // 确保只发送可序列化的数据
            // 创建一个安全的、深度复制的对象，移除所有函数和不可序列化内容
            const safeWidget = widget ? JSON.parse(JSON.stringify({
                name: widget.name || "",
                value: widget.value || "",
                type: widget.type || "string",
                options: widget.options || {},
                displayName: widget.displayName || "",
                tooltip: widget.tooltip || "", // 添加 tooltip 字段
                node_title: widget.node_title || "",
                node_type: widget.node_type || "",
                node_comfyClass: widget.node_comfyClass || ""
            })) : null;

            window.parent.postMessage({
                type: 'widget_info_response',
                messageId,
                widget: safeWidget,
                error
            }, '*');
        } catch (e) {
            console.error('[aiAppHandler] 发送 widget_info_response 失败', e);
        }
    }
});

// 导出模块
export {
    enableAIAppMode,
    disableAIAppMode,
    selectInputNode,
    deselectInputNode,
    updateInputNodeWidget,
    getSelectedInputNodes,
    clearSelectedInputNodes,
    toggleExportMode
};

//前端点击清除所有
function clearExportNodes() {
    if (!app || !app.graph || !app.graph._nodes) return;
    for (const node of app.graph._nodes) {
        deselectInputNode(node.id);
    }
}
window.clearExportNodes = clearExportNodes;
window.deselectInputNode = deselectInputNode;
window.saveOriginalNodeColors = saveOriginalNodeColors;
