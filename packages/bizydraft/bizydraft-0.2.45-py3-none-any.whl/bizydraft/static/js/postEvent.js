import { app } from "../../scripts/app.js";
import { enableAIAppMode, disableAIAppMode, selectInputNode, deselectInputNode, updateInputNodeWidget, getSelectedInputNodes, clearSelectedInputNodes, toggleExportMode } from "./aiAppHandler.js";
import { focusNodeOnly } from "./nodeFocusHandler.js";

app.registerExtension({
    name: "comfy.BizyAir.Socket",

    dispatchCustomEvent(type, detail) {
        app.api.dispatchCustomEvent(type, detail);
    },

    socket: null,
    isConnecting: false,
    taskRunning: false,

    // 心跳检测
    pingInterval: 5000, // 5秒发送一次心跳
    pingTimer: null,
    pingTimeout: 3000,
    pongReceived: false,
    pingTimeoutTimer: null, // ping超时计时器

    /**
     * 开始心跳检测
     */
    startPing() {
        this.stopPing();

        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }

        // 立即发送一次ping消息
        this.pongReceived = false;
        this.socket.send('ping');

        // 设置ping超时检测
        this.pingTimeoutTimer = setTimeout(() => {
            if (!this.pongReceived) {
                this.stopPing();
                this.reconnect();
            }
        }, this.pingTimeout);

        // 设置定时发送ping
        this.pingTimer = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.pongReceived = false;
                this.socket.send('ping');
                // 设置ping超时检测
                this.pingTimeoutTimer = setTimeout(() => {
                    // 如果没有收到pong响应
                    if (!this.pongReceived) {
                        console.log('心跳检测超时，重新连接WebSocket');
                        this.stopPing();
                        this.reconnect();
                    }
                }, this.pingTimeout);
            } else {
                this.stopPing();
            }
        }, this.pingInterval);
    },

    /**
     * 停止心跳检测
     */
    stopPing() {
        if (this.pingTimer) {
            clearInterval(this.pingTimer);
            this.pingTimer = null;
        }

        if (this.pingTimeoutTimer) {
            clearTimeout(this.pingTimeoutTimer);
            this.pingTimeoutTimer = null;
        }
    },

    /**
     * 重新连接
     */
    reconnect() {
        if (this.isConnecting) {
            return;
        }
        const url = this.socket ? this.socket.url : app.api.socket.url;
        this.closeSocket();
        this.createSocket(url);
    },

    /**
     * 创建新的WebSocket连接
     */
    createSocket(customUrl) {
        // 如果正在连接中，避免重复创建
        if (this.isConnecting) {
            console.log('WebSocket连接已在创建中，避免重复创建');
            return null;
        }

        // 标记为连接中
        this.isConnecting = true;

        // 先关闭现有连接
        this.closeSocket();

        const url = customUrl || app.api.socket.url;
        console.log('创建WebSocket连接:', url);

        try {
            const socket = new WebSocket(url);
            const dispatchCustomEvent = this.dispatchCustomEvent;
            const self = this;

            socket.onopen = function() {
                console.log('WebSocket连接已打开');
                // 清除连接中标志
                self.isConnecting = false;
                // 存储为单例
                self.socket = socket;
                // 替换app.api.socket
                app.api.socket = socket;
                // 开始心跳检测
                self.startPing();
            };

            socket.onmessage = function (event) {
                try {
                    // 处理心跳响应
                    if (event.data === 'pong') {
                        // 标记收到pong响应
                        self.pongReceived = true;
                        return;
                    }
                    if (event.data instanceof ArrayBuffer) {
                        const view = new DataView(event.data);
                        const eventType = view.getUint32(0);

                        let imageMime;
                        switch (eventType) {
                            case 3:
                                const decoder = new TextDecoder();
                                const data = event.data.slice(4);
                                const nodeIdLength = view.getUint32(4);
                                dispatchCustomEvent('progress_text', {
                                    nodeId: decoder.decode(data.slice(4, 4 + nodeIdLength)),
                                    text: decoder.decode(data.slice(4 + nodeIdLength))
                                });
                                break;
                            case 1:
                                const imageType = view.getUint32(4);
                                const imageData = event.data.slice(8);
                                switch (imageType) {
                                    case 2:
                                        imageMime = 'image/png';
                                        break;
                                    case 1:
                                    default:
                                        imageMime = 'image/jpeg';
                                        break;
                                }
                                const imageBlob = new Blob([imageData], {
                                    type: imageMime
                                });
                                dispatchCustomEvent('b_preview', imageBlob);
                                break;
                            default:
                                throw new Error(
                                    `Unknown binary websocket message of type ${eventType}`
                                );
                        }
                    } else {
                        // 检测[DONE]消息
                        if (event.data === '[DONE]') {
                            console.log('收到[DONE]消息，任务已完成，停止心跳并关闭连接');
                            self.taskRunning = false;
                            self.stopPing();
                            self.closeSocket(1000);
                            return;
                        }

                        const msg = JSON.parse(event.data);
                        window.parent.postMessage({
                            type: 'functionResult',
                            method: 'progress_info_change',
                            result: msg.progress_info
                        }, '*');
                        switch (msg.type) {
                            case 'load_start':
                            case 'load_end':
                            case 'prompt_id':
                                window.parent.postMessage({
                                    type: 'functionResult',
                                    method: 'preparingStatus',
                                    result: msg
                                }, '*')
                            case 'status':
                                if (msg.data.sid) {
                                    const clientId = msg.data.sid;
                                    window.name = clientId;
                                    sessionStorage.setItem('clientId', clientId);
                                    socket.clientId = clientId;
                                }
                                dispatchCustomEvent('status', msg.data.status ?? null);
                                break;
                            case 'executing':
                                dispatchCustomEvent(
                                    'executing',
                                    msg.data.display_node || msg.data.node
                                );
                                break;
                            case 'execution_success':
                            case 'execution_cached':
                                // 检查任务是否完成
                                if (msg.data.completed) {
                                    self.taskRunning = false;
                                }
                                dispatchCustomEvent(msg.type, msg.data);
                                break;
                            case 'error':
                                self.taskRunning = false;
                                dispatchCustomEvent('execution_error', {
                                    exception_message: msg.data.error_message || 'Unknown error',
                                    traceback: ['Manual error triggered'],
                                    executed: [],
                                    prompt_id: 'manual',
                                    node_id: '0',
                                    node_type: 'RunError',
                                });
                                break;
                            case 'execution_error':
                            case 'execution_interrupted':
                                self.taskRunning = false;
                                dispatchCustomEvent(msg.type, msg.data);
                                break;
                            case 'execution_start':
                                self.taskRunning = true;
                                dispatchCustomEvent(msg.type, msg.data);
                                break;
                            case 'progress':
                            case 'executed':
                            case 'graphChanged':
                            case 'promptQueued':
                            case 'logs':
                            case 'b_preview':
                                dispatchCustomEvent(msg.type, msg.data);
                                break;
                            default:
                                const registeredTypes = socket.registeredTypes || new Set();
                                const reportedUnknownMessageTypes = socket.reportedUnknownMessageTypes || new Set();

                                if (registeredTypes.has(msg.type)) {
                                    app.dispatchEvent(
                                        new CustomEvent(msg.type, { detail: msg.data })
                                    );
                                } else if (!reportedUnknownMessageTypes.has(msg.type)) {
                                    reportedUnknownMessageTypes.add(msg.type);
                                    console.warn(`Unknown message type ${msg.type}`);
                                }
                        }
                    }
                } catch (error) {
                    console.warn('Unhandled message:', event.data, error);
                }
            };

            socket.onerror = function(error) {
                console.log('WebSocket 错误:', error);
                // 清除连接中标志
                self.isConnecting = false;
                // 停止心跳
                self.stopPing();
            };

            socket.onclose = function(event) {
                console.log('WebSocket 连接已关闭, 状态码:', event.code, event.reason);
                // 清除连接中标志
                self.isConnecting = false;
                // 清理单例引用
                if (self.socket === socket) {
                    self.socket = null;
                }
                // 停止心跳
                self.stopPing();
            };

            socket.registeredTypes = new Set();
            socket.reportedUnknownMessageTypes = new Set();

            // 返回创建的socket，但不要立即使用，等待onopen
            return socket;
        } catch (error) {
            console.error('创建WebSocket连接失败:', error);
            this.isConnecting = false;
            return null;
        }
    },

    /**
     * 获取可用的socket连接，如果不存在则创建
     * 返回Promise以确保连接已就绪
     */
    async getSocketAsync(customUrl) {
        return new Promise((resolve, reject) => {
            // 如果已有可用连接，直接返回
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                resolve(this.socket);
                return;
            }

            // 如果连接正在创建中，等待一段时间后检查
            if (this.isConnecting) {
                console.log('WebSocket连接创建中，等待...');
                const checkInterval = setInterval(() => {
                    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                        clearInterval(checkInterval);
                        resolve(this.socket);
                    } else if (!this.isConnecting) {
                        clearInterval(checkInterval);
                        reject(new Error('WebSocket连接创建失败'));
                    }
                }, 100); // 每100ms检查一次
                return;
            }

            // 创建新连接
            const socket = this.createSocket(customUrl);
            if (!socket) {
                reject(new Error('创建WebSocket连接失败'));
                return;
            }

            // 监听连接打开事件
            socket.addEventListener('open', () => {
                resolve(socket);
            });

            // 监听错误事件
            socket.addEventListener('error', (error) => {
                reject(error);
            });
        });
    },

    /**
     * 获取可用的socket连接，如果不存在则创建
     * 同步版本，可能返回尚未就绪的连接
     */
    getSocket(customUrl) {
        // 如果已有可用连接，直接返回
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return this.socket;
        }

        // 创建新连接
        return this.createSocket(customUrl);
    },

    /**
     * 关闭socket连接
     * @param {number} code - 关闭状态码
     */
    closeSocket(code) {
        // 先停止心跳
        this.stopPing();

        if (this.socket) {
            if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
                console.log('关闭WebSocket连接');
                this.socket.close(code);
            }
            this.socket = null;
        }

        // 重置任务状态
        this.taskRunning = false;

        return true;
    },

    /**
     * 更改socket URL并创建新连接
     */
    changeSocketUrl(newUrl) {
        const clientId = sessionStorage.getItem("clientId");
        const fullUrl = newUrl + "?clientId=" + clientId + "&a=1";

        return this.createSocket(fullUrl);
    },

    /**
     * 发送socket消息
     * 确保连接已就绪
     */
    async sendSocketMessage(message) {
        try {
            const socket = await this.getSocketAsync();
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(typeof message === 'string' ? message : JSON.stringify(message));
                return true;
            }
            return false;
        } catch (error) {
            console.error('发送消息失败:', error);
            return false;
        }
    },

    /**
     * 发送任务提示
     */
    async sendPrompt(prompt) {
        try {
            // 确保有连接
            await this.getSocketAsync();
            // 发送提示
            app.queuePrompt(prompt);
            return true;
        } catch (error) {
            console.error('发送任务提示失败:', error);
            return false;
        }
    },

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    },

    async setup() {
        const createSocket = this.createSocket.bind(this);
        const closeSocket = this.closeSocket.bind(this);

        const customErrorStyles = new Map()



        // 方法映射
        const methods = {
            customSocket: async function (params) {
                const socket = createSocket(params.url);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'customSocket',
                    result: '自定义socket执行结果'
                }, '*');
                return socket;
            },

            closeSocket: function () {
                const result = closeSocket();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'closeSocket',
                    result: result ? 'Socket连接已关闭' : 'Socket连接关闭失败或已关闭'
                }, '*');
                return result;
            },

            clearCanvas: function () {
                app.graph.clear();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'clearCanvas',
                    result: true
                }, '*');
                return true;
            },
            loadWorkflow: function (params) {
                app.graph.clear();
                document.dispatchEvent(new CustomEvent('workflowLoaded', {
                    detail: params.json
                }));
                if (params.json.version) {
                    app.loadGraphData(params.json);
                } else {
                    app.loadApiJson(params.json, 'bizyair');
                }
                console.log("-----------loadWorkflow-----------", params.json)
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'loadWorkflow',
                    result: true
                }, '*');
                return true;
            },

            saveWorkflow: async function () {
                const graph = await app.graphToPrompt();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'saveWorkflow',
                    result: graph.workflow
                }, '*');
                return graph.workflow;
            },
            getWorkflow: async function () {
                const graph = await app.graphToPrompt();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'getWorkflow',
                    result: graph.workflow
                }, '*');
                return graph.workflow;
            },
            getWorkflowNotSave: async function () {
                const graph = await app.graphToPrompt();
                // 规范化工作流，移除不影响逻辑的视觉字段，避免颜色等样式变化影响校验
                const normalizeWorkflow = (workflow) => {
                    const json = JSON.stringify(workflow, (key, value) => {
                        if (key === 'color' || key === 'bgcolor' || key === 'extra') return undefined;
                        return value;
                    });
                    return JSON.parse(json);
                };
                const normalized = normalizeWorkflow(graph.workflow);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'getWorkflowNotSave',
                    result: normalized
                }, '*');
                return normalized;
            },
            // 新增：获取 workflow 和 output
            getWorkflowWithOutput: async function () {
                const graph = await app.graphToPrompt();
                // graph.workflow.nodes.forEach(node => {
                //     for (const key in graph.output) {
                //         if (graph.output[key].class_type === node.type) {
                //             if (!graph.output[key]._meta) {
                //                 graph.output[key]._meta = {};
                //             }
                //             graph.output[key]._meta.id = node.id;
                //             break; // 找到匹配的就跳出循环
                //         }
                //     }
                // });
                for (const key in graph.output) {
                    graph.output[key]._meta.id = Number(key);
                }
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'getWorkflowWithOutput',
                    result: {
                        workflow: graph.workflow,
                        output: graph.output
                    }
                }, '*');
                return { workflow: graph.workflow, output: graph.output };
            },
            saveApiJson: async function (params) {
                const graph = await app.graphToPrompt();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'saveApiJson',
                    result: graph.output
                }, '*');
                return graph.output;
            },
            getClientId: function () {
                const clientId = sessionStorage.getItem("clientId");
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'getClientId',
                    result: clientId
                }, '*');
                return clientId;
            },
            runWorkflow: async function () {
                try {
                    // 确保有连接
                    // await getSocketAsync();
                    const graph = await app.graphToPrompt();
                    const clientId = sessionStorage.getItem("clientId");
                    await app.queuePrompt(graph.output);
                    const resPrompt = await fetch("api/prompt", {
                        method: "POST",
                        body: JSON.stringify({
                            prompt: graph.output,
                            clientId,
                            number: graph.output,
                            extra_data: {
                                extra_pnginfo: {
                                    workflow: graph.workflow
                                }
                            }
                        })
                    });
                    const resPromptJson = await resPrompt.json();
                    if (resPromptJson.error) {
                        this.openCustomError({
                            nodeId: resPromptJson.node_id,
                            nodeType: resPromptJson.node_type,
                            errorMessage: resPromptJson.details,
                            borderColor: '#FF0000'
                        })
                        return
                    }

                    for (const i in resPromptJson.node_errors) {

                        if (resPromptJson.node_errors[i].errors) {
                            const err = resPromptJson.node_errors[i].errors[0]
                            if (err) {
                                this.openCustomError({
                                    nodeId: i,
                                    nodeType: err.type,
                                    errorMessage: err.details,
                                    borderColor: '#FF0000'
                                })
                                return
                            }
                        } else {
                            console.log(resPromptJson.node_errors[i])
                        }
                    }

                    if (Object.keys(resPromptJson.node_errors).length) return
                    // graph.workflow.nodes.forEach(node => {
                    //     for (const key in graph.output) {
                    //         if (graph.output[key].class_type === node.type) {
                    //             if (!graph.output[key]._meta) {
                    //                 graph.output[key]._meta = {};
                    //             }
                    //             graph.output[key]._meta.id = node.id;
                    //             console.log(graph.output[key].class_type, node.type, graph.output[key]._meta.id)
                    //             break; // 找到匹配的就跳出循环
                    //         }
                    //     }
                    // });
                    for (const key in graph.output) {
                        graph.output[key]._meta.id = Number(key);
                    }

                    for (let i in graph.output) {
                        if (graph.output[i].class_type == 'LoadImage') {
                            graph.output[i].inputs.image = graph.output[i].inputs.image.replace('pasted/http', 'http')
                        }
                    }
                    console.log(graph.output)
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'runWorkflow',
                        result: {
                            clientId: clientId,
                            jsonWorkflow: graph.output,
                            workflow: graph.workflow,
                            prompt: resPromptJson
                        }
                    }, '*');
                    return true;
                } catch (error) {
                    console.error('运行工作流失败:', error);
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'runWorkflow',
                        error: '运行工作流失败: ' + error.message,
                        success: false
                    }, '*');
                    return false;
                }
            },
            setCookie: function (params) {
                const setCookie = (name, value, days) => {
                    let expires = "";
                    if (days) {
                        const date = new Date();
                        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                        expires = "; expires=" + date.toUTCString();
                    }
                    document.cookie = name + "=" + (value || "") + expires + "; path=/";
                };
                // console.log("-----------setCookie-----------", params)
                // console.log("-----------setCookie-----------", params)
                setCookie(params.name, params.value, params.days);


                return true;
            },
            fitView: function () {
                app.canvas.fitViewToSelectionAnimated()
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'fitView',
                    result: true
                }, '*');
                return true;
            },
            clickAssistant: function () {
                const assistantBtn = document.querySelector('.btn-assistant');
                if (assistantBtn) {
                    assistantBtn.click();
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'clickAssistant',
                        result: true
                    }, '*');
                    return true;
                } else {
                    console.warn('Assistant button not found');
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'clickAssistant',
                        result: false
                    }, '*');
                    return false;
                }
            },
            clickCommunity: function () {
                const communityBtn = document.querySelector('.btn-community');
                if (communityBtn) {
                    communityBtn.click();
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'clickCommunity',
                        result: true
                    }, '*');
                    return true;
                } else {
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'clickCommunity',
                        result: false
                    }, '*');
                    return false;
                }
            },
            toPublish: async function () {
                const graph = await app.graphToPrompt();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'toPublish',
                    result: graph.workflow
                }, '*');
                return graph.workflow;
            },

            graphToPrompt: async function (params) {
                console.log('postEvent.js - graphToPrompt被调用，参数:', params);
                const graph = await app.graphToPrompt();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'graphToPrompt',
                    params: params, // 传递原始参数
                    result: {
                        workflow: graph.workflow,
                        output: graph.output
                    }
                }, '*');
                return {
                    workflow: graph.workflow,
                    output: graph.output
                };
            },
            loadGraphData: function (params) {
                    const { json, clear = true, center = false, workflow_name = "" } = params;
                    if (clear) {
                        app.graph.clear();
                    }
                    app.loadGraphData(json, clear, center, workflow_name);
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: 'loadGraphData',
                        result: true
                    }, '*');
                    return true;
            },

            // AI应用相关方法
            toggleAIAppMode: function(params) {
                const enable = params.enable === true;
                const result = enable ? enableAIAppMode() : disableAIAppMode();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'toggleAIAppMode',
                    result: result
                }, '*');
                return result;
            },

            selectInputNode: function(params) {
                if (!params.nodeId) return false;
                const result = selectInputNode(params.nodeId);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'selectInputNode',
                    result: result
                }, '*');
                return result;
            },

            selectExportNode: function(params) {
                if (!params.nodeId) return false;
                const result = selectInputNode(params.nodeId);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'selectExportNode',
                    result: result
                }, '*');
                return result;
            },

            deselectInputNode: function(params) {
                if (!params.nodeId) return false;
                const result = deselectInputNode(params.nodeId);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'deselectInputNode',
                    result: result
                }, '*');
                return result;
            },

            updateInputNodeWidget: function(params) {
                if (!params.nodeId || params.widgetName === undefined) return false;
                const result = updateInputNodeWidget(params.nodeId, params.widgetName, params.value);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'updateInputNodeWidget',
                    result: result
                }, '*');
                return result;
            },

            getInputNodes: function() {
                const result = getSelectedInputNodes();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'getInputNodes',
                    result: result
                }, '*');
                return result;
            },

            clearInputNodes: function() {
                const result = clearSelectedInputNodes();
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'clearInputNodes',
                    result: result
                }, '*');
                return result;
            },
            toggleExportMode: function(params) {
                const result = toggleExportMode(params);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'toggleExportMode',
                    result: result
                }, '*');
                return result;
            },
            openCustomError: function (params) {
                const { nodeId, nodeType, errorMessage, borderColor='#FF0000' } = params;
                const nodeIds = Array.isArray(nodeId) ? nodeId : [nodeId];
                function injectErrorDialogStyles() {
                    const styleId = 'custom-error-dialog-styles';
                    if (document.getElementById(styleId)) {
                        return; // 样式已经存在
                    }

                    const style = document.createElement('style');
                    style.id = styleId;
                    style.textContent = `
                        .comfy-error-report .no-results-placeholder p {
                            text-align: left;
                        }
                    `;
                    document.head.appendChild(style);
                };
                injectErrorDialogStyles()
                function simulateExecutionError(nodeId, nodeType, errorMessage, borderColor) {
                    // const originalNodeErrorStyle = node.strokeStyles?.['nodeError']
                    const node = app.graph.getNodeById(nodeId)
                    if (!node) return
                    if (!customErrorStyles.has(nodeId)) {
                        customErrorStyles.set(nodeId, {
                          originalStyle: node.strokeStyles?.['nodeError'],
                          customColor: borderColor,
                          nodeId: nodeId
                        })
                    }
                    node.strokeStyles = node.strokeStyles || {}
                    node.strokeStyles['nodeError'] = function () {
                        // if (this.id === nodeId) {
                        return { color: borderColor, lineWidth: 2 } // 自定义颜色和线宽
                        // }
                    }
                    const mockErrorEvent = {
                        detail: {
                            node_id: nodeId,
                            node_type: nodeType,
                            exception_message: errorMessage,
                            exception_type: 'ManualError',
                            traceback: ['Manual error triggered'],
                            executed: [],
                            prompt_id: 'manual',
                            timestamp: Date.now()
                        }
                    }

                    // 手动触发事件监听器
                    app.api.dispatchCustomEvent('execution_error', mockErrorEvent.detail)
                }

                nodeIds.forEach(id => {
                    simulateExecutionError(id, nodeType, errorMessage, borderColor)
                })

                app.canvas.draw(true, true)

                // 添加发送消息给前端折叠侧边栏的代码
                window.parent.postMessage({
                    type: 'collapseParamSelector',
                    method: 'collapseParamSelector',
                    result: true
                }, '*');

                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'openCustomError',
                    result: true
                }, '*');
            },
            clearAllCustomStyles: function () {
                customErrorStyles.forEach((styleInfo, nodeId) => {
                  const node = app.graph.getNodeById(nodeId)
                  if (!node) return
                  console.log(node)
                  // 恢复原始样式
                  if (styleInfo.originalStyle) {
                    node.strokeStyles['nodeError'] = styleInfo.originalStyle
                  } else {
                    delete node.strokeStyles['nodeError']
                  }

                  // 从映射中移除
                  customErrorStyles.delete(nodeId)
                })

                // 重绘画布
                app.canvas.draw(true, true)
            },
            focusNodeOnly: function(params) {
                if (!params.nodeId) return false;
                const result = focusNodeOnly(params.nodeId);
                window.parent.postMessage({
                    type: 'functionResult',
                    method: 'focusNodeOnly',
                    result: result
                }, '*');
                return result;
            },
        };

        methods.deselectExportNode = function(params) {
            if (params && params.nodeId !== undefined) {
                if (typeof window.deselectInputNode === 'function') {
                    window.deselectInputNode(params.nodeId);
                }
            }
        };
        methods.clearExportNodes = function() {
            if (typeof window.clearExportNodes === 'function') {
                window.clearExportNodes();
            }
        };
        // 保存工作流的原始节点颜色信息
        methods.saveOriginalNodeColors = function(params) {
            if (typeof window.saveOriginalNodeColors === 'function') {
                window.saveOriginalNodeColors(params.workflowId);
            }
        };
        window.addEventListener('message', function (event) {
            if (event.data && event.data.type === 'callMethod') {
                const methodName = event.data.method;
                const params = event.data.params || {};



                if (methods[methodName]) {
                    methods[methodName](params);
                } else {
                    console.error('方法不存在:', methodName);
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: methodName,
                        error: `方法 ${methodName} 不存在`,
                        success: false
                    }, '*');
                    window.parent.postMessage({
                        type: 'functionResult',
                        method: methodName,
                        error: `方法 ${methodName} 不存在`,
                        success: false
                    }, '*');
                }
            }
        });
        window.parent.postMessage({ type: 'iframeReady' }, '*');
        app.api.addEventListener('graphChanged', (e) => {
            console.log('Graph 发生变化，当前 workflow JSON:', e.detail)
            window.parent.postMessage({
                type: 'functionResult',
                method: 'workflowChanged',
                result: e.detail
            }, '*');

            document.dispatchEvent(new CustomEvent('workflowLoaded', {
                detail: e.detail
            }));
        })
    }
});
