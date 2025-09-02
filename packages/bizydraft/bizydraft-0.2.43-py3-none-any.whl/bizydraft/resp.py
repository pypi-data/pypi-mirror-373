from aiohttp import web


def JsonResponse(http_status_code, data):
    return web.json_response(
        data,
        status=http_status_code,
        content_type="application/json",
    )


def OKResponse():
    return JsonResponse(200, {"message": "success", "data": {}})


def ErrResponse(err_code):
    return JsonResponse(err_code, {"message": "", "data": {}})
