import { app } from "../../scripts/app.js";

// 冻结模式相关的状态变量
let freezeOverlay = null;
let highlightedNodes = new Set();
let mouseTrackingEnabled = false;
let mouseMoveListener = null;
let globalEventBlocked = false; // 全局事件是否被阻止
let keyboardListener = null; // 键盘事件监听器
let contextMenuListener = null; // 右键菜单监听器
let originalMethods = null; // 存储原始方法
let nodeSearchStyleElement = null; // 用于存储禁用节点搜索的样式元素
let bottomTipElement = null; // 用于存储底部提示元素
let dragDropBlocker = null;
let isFrozen = false; // 跟踪是否处于冻结模式
let originalRequestAnimationFrame = null; // 保存原始的requestAnimationFrame

// 冻结工作流，添加遮罩层
function freezeWorkflow(isworkflow = false) {
    // 设置冻结状态
    isFrozen = true;
    // 禁用全局快捷键和鼠标事件
    blockGlobalEvents(true);

    // 创建遮罩层
    createOverlay();

    // 更新高亮节点列表
    updateHighlightedNodes();

    // 启用鼠标追踪
    enableMouseTracking();

    // 禁用节点搜索容器
    disableNodeSearch(true);

    // 显示底部提示
    showBottomTip(isworkflow);

    // 阻止拖拽上传文件
    blockDragDropEvents(true);

    // 关闭并禁用最小地图按钮
    setMiniMapButtonDisabled(true, true);
}

// 解冻工作流，移除遮罩层
function unfreezeWorkflow() {
    isFrozen = false;
    // 恢复原始的requestAnimationFrame
    if (originalRequestAnimationFrame && window.requestAnimationFrame !== originalRequestAnimationFrame) {
        window.requestAnimationFrame = originalRequestAnimationFrame;
        originalRequestAnimationFrame = null;
    }

    // 恢复全局快捷键和鼠标事件
    blockGlobalEvents(false);

    // 移除遮罩层
    removeOverlay();

    // 清空高亮节点列表
    highlightedNodes.clear();

    // 禁用鼠标追踪
    disableMouseTracking();

    // 恢复节点搜索容器
    disableNodeSearch(false);

    // 隐藏底部提示
    hideBottomTip();

    // 恢复拖拽上传文件
    blockDragDropEvents(false);

    // 恢复最小地图按钮可用
    setMiniMapButtonDisabled(false);
}

// 显示提示信息
function showBottomTip(isworkflow = false) {
    // 如果已经存在提示元素，先移除
    if (bottomTipElement) {
        bottomTipElement.remove();
        bottomTipElement = null;
    }

    // 创建提示元素
    bottomTipElement = document.createElement('div');
    bottomTipElement.id = 'aiapp-bottom-tip';

    // 设置样式
    bottomTipElement.style.position = 'fixed';
    bottomTipElement.style.left = '64%';
    bottomTipElement.style.top = '89%';
    bottomTipElement.style.transform = 'translate(-50%, -50%)';
    bottomTipElement.style.backgroundColor = 'white'; // 白色背景
    bottomTipElement.style.color = 'black'; // 黑色文字
    bottomTipElement.style.padding = '10px 20px';
    bottomTipElement.style.textAlign = 'center';
    bottomTipElement.style.fontSize = '14px';
    bottomTipElement.style.zIndex = '10000';
    bottomTipElement.style.borderRadius = '4px';
    bottomTipElement.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
    bottomTipElement.style.border = '1px solid #e0e0e0';

    // 根据模式设置不同的提示文本
    if (isworkflow) {
        bottomTipElement.textContent = '发布工作流时不可编辑原工作流';
    } else {
        bottomTipElement.textContent = '编辑AI应用参数时不可编辑原工作流';
    }

    // 添加到DOM
    document.body.appendChild(bottomTipElement);
}

// 隐藏底部提示信息
function hideBottomTip() {
    if (bottomTipElement) {
        bottomTipElement.remove();
        bottomTipElement = null;
    }
}

// 禁用或启用节点搜索功能
function disableNodeSearch(disable) {
    // 如果已经有样式元素，先移除它
    if (nodeSearchStyleElement) {
        nodeSearchStyleElement.remove();
        nodeSearchStyleElement = null;
    }

    if (disable) {
        // 创建样式元素
        nodeSearchStyleElement = document.createElement('style');
        nodeSearchStyleElement.id = 'aiapp-disable-node-search-style';

        // 添加CSS规则来禁用节点搜索容器和相关元素
        nodeSearchStyleElement.textContent = `
            /* 禁用节点搜索容器 */
            .comfy-vue-node-search-container,
            .litegraph-dialog,
            .litecontextmenu,
            .litesearchbox,
            #node-panel,
            #dialog_node_panel,
            #dialog_search_panel {
                display: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
                opacity: 0 !important;
            }
        `;

        // 添加到文档头部
        document.head.appendChild(nodeSearchStyleElement);
    }
}

// 阻止全局快捷键和鼠标事件
function blockGlobalEvents(block) {
    if (block && !globalEventBlocked) {
        // 启用拦截
        globalEventBlocked = true;

        // 阻止键盘快捷键
        keyboardListener = function(e) {
            // 检查是否是需要阻止的按键
            // 阻止: 退格键(8), Delete(46), Ctrl+C(67), Ctrl+V(86), Ctrl+Z(90), Ctrl+Y(89)
            const key = e.keyCode || e.which;
            const isCtrl = e.ctrlKey || e.metaKey;

            // 检查节点附近的鼠标位置 - 如果在节点附近则不阻止
            // const isNearHighlightedNode = isMouseNearHighlightedNode(e);

            // if ( (
            //     key === 8 || // Backspace
            //     key === 46 || // Delete
            //     (isCtrl && (
            //         key === 67 || // C
            //         key === 86 || // V
            //         key === 90 || // Z
            //         key === 89   // Y
            //     ))
            // )) {
                // console.log('阻止键盘快捷键:', e.key, key);
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();

                // 只在冻结模式下覆盖requestAnimationFrame
                if (isFrozen && !originalRequestAnimationFrame) {
                    // 保存原始的 requestAnimationFrame
                    originalRequestAnimationFrame = window.requestAnimationFrame;

                    // 覆盖 requestAnimationFrame，过滤掉包含撤销逻辑的回调
                    window.requestAnimationFrame = function(callback) {
                        // 检查回调函数是否包含撤销相关的逻辑
                        const callbackStr = callback.toString();
                        if (callbackStr.includes('undoRedo') ||
                            callbackStr.includes('changeTracker') ||
                            callbackStr.includes('checkState')) {
                            console.log('拦截了包含撤销逻辑的 requestAnimationFrame');
                            // 返回一个空函数，不执行撤销逻辑
                            return originalRequestAnimationFrame(() => {});
                        }
                        // 其他回调正常执行
                        return originalRequestAnimationFrame(callback);
                    };
                }

                return false;
            // }
        };

        // 阻止右键菜单
        contextMenuListener = function(e) {
            // 检查鼠标是否在高亮节点附近
            const isNearHighlightedNode = isMouseNearHighlightedNode(e);

            // 如果不在高亮节点附近，阻止右键菜单
            if (!isNearHighlightedNode) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        };

        // 添加事件监听器
        document.addEventListener('keydown', keyboardListener, true);
        document.addEventListener('contextmenu', contextMenuListener, true);

        // 保存并替换LiteGraph的双击相关方法
        if (window.LGraphCanvas) {
            // 保存原始方法
            originalMethods = {
                showNodePanel: LGraphCanvas.prototype.showNodePanel,
                processNodeDblClicked: LGraphCanvas.prototype.processNodeDblClicked,
                processContextMenu: LGraphCanvas.prototype.processContextMenu
            };

            // 禁用节点面板(双击弹出的)
            LGraphCanvas.prototype.showNodePanel = function() {
                return false;
            };

            // 禁用节点双击
            LGraphCanvas.prototype.processNodeDblClicked = function() {
                return false;
            };

            // 禁用右键菜单
            LGraphCanvas.prototype.processContextMenu = function(node, event) {
                // 检查是否在高亮节点附近
                if (node && highlightedNodes.has(node.id)) {
                    // 在高亮节点上，允许菜单
                    if (originalMethods.processContextMenu) {
                        return originalMethods.processContextMenu.call(this, node, event);
                    }
                } else {
                    // 检查鼠标是否在节点附近（即使不是该节点本身）
                    if (event && isMouseNearHighlightedNode(event)) {
                        return false; // 在节点附近但不允许菜单
                    }
                    return false;
                }
            };
        }

    } else if (!block && globalEventBlocked) {
        // 禁用拦截
        globalEventBlocked = false;

        // 移除事件监听器
        document.removeEventListener('keydown', keyboardListener, true);
        document.removeEventListener('contextmenu', contextMenuListener, true);

        // 恢复LiteGraph的方法
        if (window.LGraphCanvas && originalMethods) {
            if (originalMethods.showNodePanel) {
                LGraphCanvas.prototype.showNodePanel = originalMethods.showNodePanel;
            }

            if (originalMethods.processNodeDblClicked) {
                LGraphCanvas.prototype.processNodeDblClicked = originalMethods.processNodeDblClicked;
            }

            if (originalMethods.processContextMenu) {
                LGraphCanvas.prototype.processContextMenu = originalMethods.processContextMenu;
            }
        }

        originalMethods = null;
        keyboardListener = null;
        contextMenuListener = null;
    }
}

// 检查鼠标是否在高亮节点附近（包括扩展范围）
function isMouseNearHighlightedNode(e) {
    if (!app || !app.graph) return false;

    // 转换为图形坐标
    const pos = app.canvas.convertEventToCanvasOffset(e);

    // 检查所有高亮节点
    for (const node of app.graph._nodes) {
        if (node && node._aiAppHighlighted) {
            // 使用正确的属性名：_pos 和 _posSize
            const nodeX = node._pos[0];
            const nodeY = node._pos[1];
            const nodeWidth = node._posSize[2];
            const nodeHeight = node._posSize[3];

            const nodeBounds = {
                left: nodeX - 10,
                top: nodeY - 50,
                right: nodeX + nodeWidth + 2,
                bottom: nodeY + nodeHeight + 2
            };

            // 检查鼠标是否在扩展边界内
            if (pos[0] >= nodeBounds.left && pos[0] <= nodeBounds.right &&
                pos[1] >= nodeBounds.top && pos[1] <= nodeBounds.bottom) {
                return true;
            }
        }
    }

    return false;
}

// 创建遮罩层
function createOverlay() {
    // 如果已存在，先移除
    removeOverlay();

    // 创建新的遮罩层
    freezeOverlay = document.createElement('div');
    freezeOverlay.id = 'aiapp-freeze-overlay';

    // 设置样式
    freezeOverlay.style.position = 'absolute';
    freezeOverlay.style.top = '0';
    freezeOverlay.style.left = '0';
    freezeOverlay.style.width = '100%';
    freezeOverlay.style.height = '100%';
    freezeOverlay.style.backgroundColor = 'transparent';
    freezeOverlay.style.zIndex = '9999';
    freezeOverlay.style.pointerEvents = 'none'; // 默认不拦截事件，让画布可移动
    freezeOverlay.style.cursor = 'move'; // 默认指示可拖动

    // 添加事件监听
    freezeOverlay.addEventListener('mousedown', handleOverlayMouseDown);

    // 添加到DOM
    const container = document.querySelector('#graph-canvas')?.parentElement || document.body;
    container.appendChild(freezeOverlay);
}

// 移除遮罩层
function removeOverlay() {
    if (freezeOverlay) {
        freezeOverlay.removeEventListener('mousedown', handleOverlayMouseDown);
        freezeOverlay.remove();
        freezeOverlay = null;
    }
}

// 启用鼠标追踪
function enableMouseTracking() {
    if (!mouseTrackingEnabled) {
        mouseMoveListener = handleMouseMove.bind(this);
        document.addEventListener('mousemove', mouseMoveListener);
        mouseTrackingEnabled = true;
    }
}

// 禁用鼠标追踪
function disableMouseTracking() {
    if (mouseTrackingEnabled) {
        document.removeEventListener('mousemove', mouseMoveListener);
        mouseMoveListener = null;
        mouseTrackingEnabled = false;
    }
}

// 处理鼠标移动事件
function handleMouseMove(e) {
    if (!freezeOverlay || !app || !app.graph) return;

    // 转换为图形坐标
    const pos = app.canvas.convertEventToCanvasOffset(e);

    // 检查鼠标是否在高亮节点附近
    let isNearHighlightedNode = false;
    for (const node of app.graph._nodes) {
        if (node && node._aiAppHighlighted) {
            // 使用正确的属性名：_pos 和 _posSize
            const nodeX = node._pos[0];
            const nodeY = node._pos[1];
            const nodeWidth = node._posSize[2];
            const nodeHeight = node._posSize[3];

            const nodeBounds = {
                left: nodeX - 10,
                top: nodeY - 50,
                right: nodeX + nodeWidth + 2,
                bottom: nodeY + nodeHeight + 2
            };

            if (pos[0] >= nodeBounds.left && pos[0] <= nodeBounds.right &&
                pos[1] >= nodeBounds.top && pos[1] <= nodeBounds.bottom) {
                isNearHighlightedNode = true;
                break;
            }
        }
    }

    // 根据鼠标位置控制遮罩层
    if (isNearHighlightedNode) {
        // 鼠标在高亮节点附近，打开遮罩层
        showOverlay();
    } else {
        // 鼠标在空白区域，隐藏遮罩层
        hideOverlay();
    }
}

// 显示遮罩层
function showOverlay() {
    if (freezeOverlay) {
        freezeOverlay.style.pointerEvents = 'all';
        freezeOverlay.style.cursor = 'pointer';
    }
}

// 隐藏遮罩层
function hideOverlay() {
    if (freezeOverlay) {
        freezeOverlay.style.pointerEvents = 'none';
    }
}

// 更新高亮节点列表
function updateHighlightedNodes() {
    highlightedNodes.clear();

    if (!app || !app.graph || !app.graph._nodes) return;

    for (const node of app.graph._nodes) {
        if (node && node._aiAppHighlighted) {
            highlightedNodes.add(node.id);
        }
    }
}
//关闭并禁用小地图按钮
function setMiniMapButtonDisabled(disabled, clickIfActive = false) {
    const miniMapBtn = document.querySelector('button[data-testid="toggle-minimap-button"]');
    if (!miniMapBtn) return;

    if (disabled) {
        const isActive = miniMapBtn.classList.contains('minimap-active') ||
            miniMapBtn.hasAttribute('minimap-active') ||
            miniMapBtn.getAttribute('aria-pressed') === 'true';
        if (clickIfActive && isActive) {
            miniMapBtn.click();
        }
        miniMapBtn.disabled = true;
    } else {
        miniMapBtn.disabled = false;
    }
}

// 处理遮罩层上的鼠标按下事件
function handleOverlayMouseDown(e) {
    // 检查是否点击了高亮节点附近
    const isNearHighlightedNode = isMouseNearHighlightedNode(e);

    if (isNearHighlightedNode) {
        // 获取实际点击的节点（用于发送消息）
        const nodeUnderMouse = getNodeUnderMouse(e);

        if (nodeUnderMouse) {
            // 发送消息到前端，通知节点被点击
            window.parent.postMessage({
                type: 'CANVAS_NODE_CLICKED',
                nodeId: nodeUnderMouse.id,
                nodeTitle: nodeUnderMouse.title,
                nodeType: nodeUnderMouse.type
            }, '*');
        }

        // 阻止事件冒泡，避免触发其他处理
        e.preventDefault();
        e.stopPropagation();
        return false;
    }

    // 让事件传递给画布 - 允许画布正常处理点击事件
    return true;
}

// 获取鼠标下方的节点
function getNodeUnderMouse(e) {
    if (!app || !app.graph) return null;

    // 获取画布位置
    const canvas = document.querySelector('canvas');
    if (!canvas) return null;

    // 转换为图形坐标
    const pos = app.canvas.convertEventToCanvasOffset(e);

    // 检查点击位置是否在某个节点上
    const node = app.graph.getNodeOnPos(pos[0], pos[1]);
    return node;
}

// 阻止拖拽上传文件
function blockDragDropEvents(enable) {
    if (enable) {
        if (dragDropBlocker) return; // 已经阻止过了
        dragDropBlocker = function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        };
        document.addEventListener('dragover', dragDropBlocker, true);
        document.addEventListener('drop', dragDropBlocker, true);
    } else {
        if (!dragDropBlocker) return;
        document.removeEventListener('dragover', dragDropBlocker, true);
        document.removeEventListener('drop', dragDropBlocker, true);
        dragDropBlocker = null;
    }
}

export {
    freezeWorkflow,
    unfreezeWorkflow,
    isMouseNearHighlightedNode,
    getNodeUnderMouse,
    updateHighlightedNodes
};
