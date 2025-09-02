from typing import Any, Dict, List, Set

BASIC_TYPES = (int, float, str, bool)


def is_basic_type(val: Any) -> bool:
    return isinstance(val, BASIC_TYPES)


def get_input_params(prompt: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    遍历所有节点inputs，保留基础类型参数。
    返回格式：[{node_id, class_type, param_name, param_value}]
    """
    input_params = []
    for node_id, node in prompt.items():
        class_type = node.get("class_type")
        for k, v in node.get("inputs", {}).items():
            if is_basic_type(v):
                input_params.append(
                    {
                        "node_id": node_id,
                        "class_type": class_type,
                        "param_name": k,
                        "param_value": v,
                    }
                )
    return input_params


def get_leaf_nodes_from_prompt(prompt: Dict[str, Any]) -> Set[str]:
    """
    仅通过prompt参数推断叶子节点（即没有被其他节点inputs引用的节点）。
    返回节点id集合（字符串）。
    """
    referenced = set()
    for node_id, node in prompt.items():
        for v in node.get("inputs", {}).values():
            # 如果是引用（如["4", 1]），则v为list且第一个元素为节点id
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                referenced.add(v[0])
    all_nodes = set(prompt.keys())
    leaf_nodes = all_nodes - referenced
    return leaf_nodes


def summarize_params(
    input_params: List[Dict[str, Any]],
    exclude_node_ids: Set[str],
    wf_nodes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    按节点类型和参数名整理参数信息，便于输出。
    exclude_node_ids: 需要从inputs中排除的节点id集合
    """
    summary = {}
    for param in input_params:
        node_id = param["node_id"]
        if node_id in exclude_node_ids:
            continue
        wf_node = get_node_id_from_wf_nodes(wf_nodes, node_id)
        title = param["class_type"]
        if wf_node and wf_node.get("title", None):
            title = wf_node.get("title")
        key = (param["class_type"], node_id)
        if key not in summary:
            summary[key] = {
                "name": param["class_type"],
                "displayName": param["class_type"],
                "nodeId": node_id,
                "params": [],
                "title": title,
            }
        summary[key]["params"].append(
            {
                "name": param["param_name"],
                "displayName": param["param_name"],
                "type": type(param["param_value"]).__name__.upper(),
                "defaultValue": param["param_value"],
            }
        )
    return list(summary.values())


def get_node_id_from_wf_nodes(
    wf_nodes: List[Dict[str, Any]], node_id: str
) -> Dict[str, Any]:
    for wf_node in wf_nodes:
        if str(wf_node.get("id", 0)) == node_id:
            return wf_node
    return None


def parse_workflow_io(request_data) -> Dict[str, Any]:
    prompt = request_data.get("prompt", {})
    extra_data = request_data.get("extra_data", {})

    extra_pnginfo = extra_data.get("extra_pnginfo", {})
    workflow = extra_pnginfo.get("workflow", {})
    wf_nodes = workflow.get("nodes", [])

    # 1. 输出参数（推断叶子节点）
    leaf_nodes = get_leaf_nodes_from_prompt(prompt)
    output_nodes = []
    for node_id in leaf_nodes:
        node = prompt[node_id]
        class_type = node.get("class_type")
        wf_node = get_node_id_from_wf_nodes(wf_nodes, node_id)
        title = class_type
        if wf_node and wf_node.get("title", None):
            title = wf_node.get("title")
        output_nodes.append(
            {
                "nodeId": node_id,
                "name": class_type,
                "displayName": class_type,
                "title": title,
                "params": [],
            }
        )

    # 2. 输入参数（排除已作为输出的节点）
    input_params = get_input_params(prompt)
    input_summary = summarize_params(
        input_params, exclude_node_ids=leaf_nodes, wf_nodes=wf_nodes
    )

    # 3. 构造response_body.json格式
    return {"data": {"inputs": input_summary, "outputs": output_nodes}}
