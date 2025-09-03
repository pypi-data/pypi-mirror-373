/**
 * 节点参数过滤工具
 * 用于处理节点参数在发布模式下的过滤
 */

// 存储从服务端获取的节点参数信息
let nodeParamsMap = new Map();

/**
 * 设置节点参数映射
 * @param {Array} inputsData - 服务端返回的inputs数组
 */
function setNodeParams(inputsData) {
    if (!Array.isArray(inputsData)) {
        console.error('Invalid inputs data format:', inputsData);
        return;
    }

    // 清空现有映射
    nodeParamsMap.clear();

    // 构建新的映射
    inputsData.forEach(nodeInfo => {
        if (nodeInfo && nodeInfo.nodeId && Array.isArray(nodeInfo.params)) {
            // 以nodeId为键，存储参数信息
            const paramNames = nodeInfo.params.map(param => param.name);
            nodeParamsMap.set(nodeInfo.nodeId, {
                name: nodeInfo.name,
                displayName: nodeInfo.displayName,
                paramNames: paramNames,
                params: nodeInfo.params
            });
        }
    });

    console.log('节点参数映射已更新:', nodeParamsMap);
}

/**
 * 过滤节点参数
 * @param {Object} node - 节点对象
 * @returns {Object|null} - 过滤后的节点信息，如果节点不符合条件则返回null
 */
function filterNodeWidgets(node) {
    if (!node || !node.id) return null;

    // 如果节点ID不在参数映射中，则不是可配置节点
    if (!nodeParamsMap.has(String(node.id))) {
        console.log(`节点 ${node.id} 不在可配置列表中`);
        return null;
    }

    // 获取节点的允许参数列表
    const nodeParamsInfo = nodeParamsMap.get(String(node.id));
    const allowedParamNames = nodeParamsInfo.paramNames;

    // 提取节点信息
    const nodeInfo = {
        id: node.id,
        type: node.type,
        comfyClass: node.comfyClass,
        title: node.title || nodeParamsInfo.displayName,
        widgets: []
    };

    // 过滤widgets，只保留在allowedParamNames中的widget
    if (node.widgets && node.widgets.length > 0) {
        nodeInfo.widgets = node.widgets
            .filter(widget => {
                return widget.type !== "hidden" &&
                       !widget.disabled &&
                       allowedParamNames.includes(String(widget.name));
            })
            .map(widget => {
                const widgetInfo = {
                    name: String(widget.name || ""),
                    value: widget.value != null ? widget.value : "",
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

    // 如果过滤后没有可配置的参数，则不符合条件
    if (nodeInfo.widgets.length === 0) {
        console.log(`节点 ${node.id} 没有可配置的参数`);
        return null;
    }

    return nodeInfo;
}

/**
 * 检查节点是否可配置
 * @param {number|string} nodeId - 节点ID
 * @returns {boolean} - 节点是否可配置
 */
function isConfigurableNode(nodeId) {
    return nodeParamsMap.has(String(nodeId));
}

/**
 * 获取节点原始参数信息
 * @param {number|string} nodeId - 节点ID
 * @returns {Object|null} - 节点参数信息
 */
function getNodeParamsInfo(nodeId) {
    return nodeParamsMap.get(String(nodeId)) || null;
}

// 导出模块
export {
    setNodeParams,
    filterNodeWidgets,
    isConfigurableNode,
    getNodeParamsInfo
};
