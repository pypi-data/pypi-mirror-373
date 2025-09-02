import { app } from "../../scripts/app.js";
import { getCookie, computeIsLoadNode, computeExt, hideWidget } from './tool.js';


app.registerExtension({
    name: "bizyair.image.to.oss",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        let workflowParams = null
        document.addEventListener('workflowLoaded', (event) => {
            workflowParams = event.detail;
        })
        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;

            Array.from(files).forEach((file) => {
                if (file.type === 'application/json' || file.name.endsWith('.json')) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        try {
                            const jsonContent = JSON.parse(event.target.result);
                            if (jsonContent && jsonContent.nodes) {
                                window.currentWorkflowData = jsonContent;
                            }
                        } catch (error) {
                            console.error('解析JSON文件失败:', error);
                        }
                    };
                    reader.readAsText(file);
                }
            });
        })
        if (computeIsLoadNode(nodeData.name)) {
            nodeType.prototype.onNodeCreated = async function() {
                const apiHost = 'https://bizyair.cn/api'
                const image_widget = this.widgets.find(w => {
                    return w.name === 'image'
                            || w.name === 'file'
                            || w.name === 'audio'
                            || w.name === 'model_file'
                });
                let image_name_widget = this.widgets.find(w => w.name === 'image_name');
                let image_list = []
                const getData = async () => {
                    const res = await fetch(`${apiHost}/special/community/commit_input_resource?${
                        new URLSearchParams({
                            ext: computeExt(nodeData.name),
                            current: 1,
                            page_size: 100

                        }).toString()
                    }`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getCookie('bizy_token')}`
                        }
                    })
                    const {data} = await res.json()
                    const list = (data && data.data && data.data.data && data.data.data.list) || []
                    image_list = list.filter(item => item.name).map(item => {
                        return {
                            url: item.url,
                            id: item.id,
                            name: item.name
                        }
                    })
                    if (!image_name_widget) {
                        image_name_widget = this.addWidget("combo", "image_name", "", function(e){
                            const item = image_list.find(item => item.name === e)
                            const image_url = decodeURIComponent(item.url);
                            image_widget.value = image_url;
                            if (image_widget.callback) {
                                image_widget.callback(e);
                            }
                        }, {
                            serialize: true,
                            values: image_list.map(item => item.name)
                        });
                    }
                    const val = image_list.find(item => item.url === image_widget.value)?.name || image_widget.value
                    image_name_widget.label = image_widget.label
                    image_name_widget.value = val

                    const currentIndex = this.widgets.indexOf(image_name_widget);
                    if (currentIndex > 1) {
                        this.widgets.splice(currentIndex, 1);
                        this.widgets.splice(1, 0, image_name_widget);
                    }
                    hideWidget(this, image_widget.name)
                    image_widget.options.values = image_list.map(item => item.name);

                    const callback = image_widget.callback
                    image_widget.callback = async function(e) {
                        console.log(e)
                        if (typeof e == 'string') {
                            const item = e.includes('http') ?
                                image_list.find(item => item.url === e) :
                                image_list.find(item => item.name === e)

                            const image_url = item ? decodeURIComponent(item.url) : e;

                            image_name_widget.value = item ? item.name : e;
                            image_widget.value = image_url;
                            console.log('=================image_url=================')
                            console.log(image_url)
                            console.log(item)
                            console.log(await app.graphToPrompt())
                            callback([image_url])
                            console.log(await app.graphToPrompt())
                        } else {
                            const item = e[0].split('/')
                            image_name_widget.options.values.pop()
                            image_name_widget.options.values.push(item[item.length - 1])
                            image_name_widget.value = item[item.length - 1]
                            image_list.push({
                                name: item[item.length - 1],
                                url: e[0]
                            })
                            callback(e)
                        }
                    }
                    return true
                }
                await getData()


                function applyWorkflowImageSettings(workflowParams, image_list, image_widget, image_name_widget) {
                    if (workflowParams && workflowParams.nodes) {
                        const imageNode = workflowParams.nodes.find(item => computeIsLoadNode(item.type))
                        if (imageNode && imageNode.widgets_values) {
                            const item = imageNode.widgets_values[0].split('/')
                            image_list.push({
                                name: item[item.length - 1],
                                url: imageNode.widgets_values[0]
                            })
                            image_widget.value = imageNode.widgets_values[0]

                            image_widget.options.values = image_list.map(item => item.url)
                            image_name_widget.options.values = image_list.map(item => item.name)
                            image_widget.callback(imageNode.widgets_values[0])
                        }
                    }
                }

                // 如果有存储的工作流数据，应用图像设置
                if (window.currentWorkflowData) {
                    applyWorkflowImageSettings(window.currentWorkflowData, image_list, image_widget, image_name_widget);
                    // 清除存储的数据，避免重复处理
                    delete window.currentWorkflowData;
                } else {
                    // 原有的调用
                    applyWorkflowImageSettings(workflowParams, image_list, image_widget, image_name_widget);
                }


            }
        }
    }
})

// app.api.addEventListener('graphChanged', (e) => {
//     console.log('Graph 发生变化，当前 workflow JSON:', e.detail)
//     window.parent.postMessage({
//         type: 'functionResult',
//         method: 'workflowChanged',
//         result: e.detail
//     }, '*');

//     document.dispatchEvent(new CustomEvent('workflowLoaded', {
//         detail: e.detail
//     }));
// })
