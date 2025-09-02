import { app } from "../../scripts/app.js";

// 全局变量引用（从aiAppHandler.js中引用）
let freezeOverlay = null;
let globalEventBlocked = false;
let keyboardListener = null;
let contextMenuListener = null;

// 设置全局变量引用
export function setGlobalReferences(overlay, eventBlocked, kListener, cListener) {
    freezeOverlay = overlay;
    globalEventBlocked = eventBlocked;
    keyboardListener = kListener;
    contextMenuListener = cListener;
}

// 只聚焦节点，不高亮
export function focusNodeOnly(nodeId) {
    console.log('[nodeFocusHandler] focusNodeOnly called with nodeId:', nodeId);

    if (!app || !app.graph) {
        console.error('[nodeFocusHandler] app or app.graph not available');
        return false;
    }

    const node = app.graph.getNodeById(parseInt(nodeId, 10));
    if (!node) {
        console.error('[nodeFocusHandler] 找不到节点:', nodeId);
        return false;
    }

    console.log('[nodeFocusHandler] 找到节点:', node);

    // 临时禁用冻结模式
    const wasFreezed = !!freezeOverlay;
    let originalOverlayDisplay = null;

    if (wasFreezed && freezeOverlay) {
        originalOverlayDisplay = freezeOverlay.style.display;
        freezeOverlay.style.display = 'none';

        // 临时解除事件阻止
        if (globalEventBlocked) {
            document.removeEventListener('keydown', keyboardListener, true);
            document.removeEventListener('contextmenu', contextMenuListener, true);
        }
    }

    // 只设置节点的 selected 属性，不改变颜色
    for (const n of app.graph._nodes) {
        n.selected = n.id === node.id;
    }

    // 设置 selected_nodes
    if (app.canvas) {
        app.canvas.selected_nodes = [node];
    }

    // 聚焦到节点 - 使用与selectNodeAndFocus相同的方法
    if (app.canvas && typeof app.canvas.centerOnNode === 'function') {
        console.log('[nodeFocusHandler] 使用 centerOnNode 方法聚焦节点');
        app.canvas.centerOnNode(node);
    }

    // 刷新画布
    if (app.canvas) {
        app.canvas.setDirty(true, true);
        if (typeof app.canvas.draw === 'function') {
            app.canvas.draw(true, true);
        }
    }

    // 恢复冻结模式
    setTimeout(() => {
        if (wasFreezed && freezeOverlay) {
            freezeOverlay.style.display = originalOverlayDisplay;

            // 恢复事件阻止
            if (globalEventBlocked) {
                document.addEventListener('keydown', keyboardListener, true);
                document.addEventListener('contextmenu', contextMenuListener, true);
            }
        }

        // 再次刷新画布
        if (app.canvas) {
            app.canvas.setDirty(true, true);
            if (typeof app.canvas.draw === 'function') {
                app.canvas.draw(true, true);
            }
        }
    }, 100);

    console.log('[nodeFocusHandler] focusNodeOnly 完成');
    return true;
}

// 处理画布节点点击事件
export function handleCanvasNodeClick(e) {
    if (!app || !app.graph) return;

    // 获取点击的节点
    const nodeUnderMouse = getNodeUnderMouse(e);
    if (!nodeUnderMouse) return;

    console.log('[nodeFocusHandler] 画布点击节点:', nodeUnderMouse.id, nodeUnderMouse.title);

    // 发送消息到前端，通知节点被点击
    window.parent.postMessage({
        type: 'CANVAS_NODE_CLICKED',
        nodeId: nodeUnderMouse.id,
        nodeTitle: nodeUnderMouse.title,
        nodeType: nodeUnderMouse.type
    }, '*');
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

// 设置画布点击事件监听
export function setupCanvasClickHandler() {
    // 移除现有的事件监听器
    removeCanvasClickHandler();

    // 添加画布点击事件监听
    const canvas = document.querySelector('canvas');
    if (canvas) {
        canvas.addEventListener('click', handleCanvasNodeClick);
        console.log('[nodeFocusHandler] 画布点击事件监听器已设置');
    }
}

// 移除画布点击事件监听
export function removeCanvasClickHandler() {
    const canvas = document.querySelector('canvas');
    if (canvas) {
        canvas.removeEventListener('click', handleCanvasNodeClick);
        console.log('[nodeFocusHandler] 画布点击事件监听器已移除');
    }
}
