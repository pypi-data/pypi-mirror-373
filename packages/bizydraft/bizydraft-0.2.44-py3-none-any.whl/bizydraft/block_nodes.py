import os

from loguru import logger

BIZYDRAFT_BLACKLIST_NODES = os.getenv(
    "BIZYDRAFT_BLACKLIST_NODES", "blacklist_nodes.json"
)
logger.info(f"Using blacklist nodes file: {BIZYDRAFT_BLACKLIST_NODES=}")

if os.path.exists(BIZYDRAFT_BLACKLIST_NODES):
    import json

    with open(BIZYDRAFT_BLACKLIST_NODES, "r") as f:
        BLACKLIST_NODE_CLASS = json.load(f)
else:
    logger.error(f"Blacklisted nodes file {BIZYDRAFT_BLACKLIST_NODES} does not exist.")
    BLACKLIST_NODE_CLASS = []


def remove_blacklisted_nodes():
    try:
        import nodes
    except ImportError:
        logger.error(
            "Failed to import NODE_CLASS_MAPPINGS, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
        )
        return

    for node_name in BLACKLIST_NODE_CLASS:
        if node_name in nodes.NODE_CLASS_MAPPINGS:
            del nodes.NODE_CLASS_MAPPINGS[node_name]
            logger.info(f"Removed blacklisted node: {node_name}")
        else:
            pass
            # logger.warning(f"Node {node_name} not found in NODE_CLASS_MAPPINGS")
