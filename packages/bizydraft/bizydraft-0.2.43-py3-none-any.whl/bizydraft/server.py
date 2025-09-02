import os
from typing import Union

from loguru import logger

from .workflow_io import parse_workflow_io

try:
    from server import PromptServer
except ImportError:
    logger.error(
        "Failed to import ComfyUI server modules, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
    )
    exit(1)

from .resp import ErrResponse, JsonResponse, OKResponse

_API_PREFIX = "bizyair"
_SERVER_MODE_HC_FLAG = True

BIZYAIR_MAGIC_STRING = os.getenv("BIZYAIR_MAGIC_STRING", "QtDtsxAc8JI1bTb7")

if BIZYAIR_MAGIC_STRING == "QtDtsxAc8JI1bTb7":
    logger.warning(
        "BIZYAIR_MAGIC_STRING is not set, using default value. This is insecure and should be changed in production!"
    )


class BizyDraftServer:
    def __init__(self):
        BizyDraftServer.instance = self
        self.prompt_server = PromptServer.instance
        self.setup_routes()

    def setup_routes(self):
        @self.prompt_server.routes.get(f"/{_API_PREFIX}/are_you_alive")
        async def are_you_alive(request) -> Union[OKResponse, ErrResponse]:
            if _SERVER_MODE_HC_FLAG:
                return OKResponse()
            return ErrResponse(500)

        @self.prompt_server.routes.post(
            f"/{_API_PREFIX}/are_you_alive_{BIZYAIR_MAGIC_STRING}"
        )
        async def toggle_are_you_alive(request) -> OKResponse:
            global _SERVER_MODE_HC_FLAG
            _SERVER_MODE_HC_FLAG = not _SERVER_MODE_HC_FLAG
            return OKResponse()

        @self.prompt_server.routes.post(f"/{_API_PREFIX}/workflow_io")
        async def workflow_io(request) -> Union[JsonResponse, ErrResponse]:
            try:
                data = await request.json()
            except Exception as e:
                logger.error(f"解析 request.json() 失败: {e}")
                return ErrResponse(400)
            try:
                response = parse_workflow_io(data)
                return JsonResponse(200, response)
            except Exception as e:
                logger.error(f"parse_workflow_io 处理失败: {e}")
                return ErrResponse(500)
