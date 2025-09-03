import base64
import json
import os
from http.cookies import SimpleCookie
from time import time
from typing import Any, Dict

import aiohttp
import oss2
from aiohttp import web
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from loguru import logger
from werkzeug.utils import secure_filename

from bizydraft.env import BIZYAIR_API_KEY, BIZYDRAFT_SERVER

private_key_pem = os.getenv(
    "RSA_PRIVATE_KEY",
    """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAuROqSPqhJlpv5R1wDl2sGuyA59Hf1y+VLR0w3cCyM6/WEQ4b
+TBFfM5HeCLc2YVDybc0ZJxsEqCXKpTweMlQg063ECK4961icF3xL8DRfXkwpUFJ
CfG24tLdXwWK3CJDb4RqGSyZm2F0mE/kqMpidsoJrXy24B4iSJrk5DGRSL1dChiL
vuvNNWPtdDHylormBxz2f8ePvvO8v/qsN+Xpxt7YirqWe5P2VavqMv66H7tItcZj
LMIFF2kV8rYF94tk6/jL/Hb7gG7ujG2p5ikG+sNhrzn0TsWdh97S6F9kTC5D1IkM
TXEhedXN1CQ4Z35TvIHxU1DBiax8t8mq/lF3rwIDAQABAoIBAQCvR8SaYWOF41jd
8MdTk7uPtDVRWB9auSHbHC5PllQvR3TBqk8r7V+iF+rwCHSJPgE5ZV0lfE+ORLFm
DrDAdEjgUwhlK71qNLdqHE50H3VIFCLSH8aAuH+wymwFtkYQvhKH5yxksyy3T9EQ
/3lbsnEWd7o6qEa6c0+c27WzuI4UCEdQpeSG+5UYHykC/Rdfc25wXTjeK8QSUcw4
Xlbt1O7omKAdrbSwbTValfqoUpKlAZ55nvJGqHnBWE5cvx9UHPooGWMUpq8004xb
sU42q2mDSEkRNE+irvc1FInxJ+gDk51Qem1r4Uy4pUnzyngXBFrp2XQazE/aVZSr
JG9fxfmBAoGBAN66SwUJg5LsRBFlPZTXzTLTzwXqm8e9ipKfe9dkuXX5Mx9mEbTd
mjZL1pHX0+YZAQu2V6dekvABFwEOnlvm0l0TopR1yyzA7PZK5ZUF0Tb9binLobO1
8G01Cp2jmrlarRGbwRdr9YXQ4ZKbvKUMevzYMIvPUFIkKQxHY/+x2IkRAoGBANS5
gDHwJ/voZTqqcJpn916MwhjsQvOmlNdDzqKe5FYd/DKb1X+tDAXK/sAFMOMj5Row
qCWu5G1T4f7DRY/BDXEU4u6YqcdokXTeZ45Z+fAZotcSit50T9gGoCTx8MMdeTUb
y4uY6cvCnd6x5PYOoBRL9QQX/ML7LX0S1Q2xL/S/AoGAfOQ/nuJ32hIMFSkNAAKG
eOLWan3kvnslUhSF8AD2EhYbuZaVhTLh/2JFPmCk3JjWwkeMHTjl8hjaWmhlGilz
emfBObhXpo/EEFNtK0QozcoMVPlvggMaf1JH0p9j6l3TQFVzT/vkoBXB92DGxlIa
QN/FURB9/KF0NwNtKnsCbdECgYARgUZUVa/koeYaosXrXtzTUf/y7xY/WJjs8e6C
IVMm5wbG3139SK8xltfJ02OHfX+v3QspNrAjcwCo50bFIpzJjm9yNOvbtfYqSNb6
ttrDcEifLC5zSdz8KOdqwuIOHFHKFgR081th4hz9o2P0/5UatnluIc8x+Ftw7GjN
3KPWnwKBgQCrt3Zs5eqDvFRmuB6d1uMFhAPqjrxnvdl3xhONnIopM4A62FLW4AoI
jpIg9K5YWK3nrROMWINH286CewjHXu2fhkhk1VPKo6Mz8bTqUoFZkI8cap/wfyqv
BMb5TNmgx+tp12pH2VNc/kC5c+GKi8VnNYx8K6gRzpZIIDfSUR10RQ==
-----END RSA PRIVATE KEY-----""",
)


class TokenExpiredError(Exception):
    """Exception raised when the token has expired."""

    pass


def decrypt(encrypted_message):
    try:
        if not encrypted_message or not isinstance(encrypted_message, str):
            raise ValueError("无效的加密消息")

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None, backend=default_backend()
        )

        encrypted_bytes = base64.b64decode(encrypted_message)
        decrypted_bytes = private_key.decrypt(encrypted_bytes, padding.PKCS1v15())
        decrypted_str = decrypted_bytes.decode("utf-8")

        parsed_data = json.loads(decrypted_str)

        now = int(time() * 1000)  # Convert to milliseconds to match JavaScript
        if now - parsed_data["timestamp"] > parsed_data["expiresIn"]:
            raise TokenExpiredError("Token已过期")

        return parsed_data["data"]

    except Exception as error:
        logger.error(
            "解密失败:",
            {
                "message": str(error),
                "input": encrypted_message[:100] + "..." if encrypted_message else None,
            },
        )
        return None


async def get_upload_token(
    filename: str,
    api_key: str,
) -> Dict[str, Any]:
    url = f"{BIZYDRAFT_SERVER}/upload/token?file_name={filename}&file_type=inputs"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()


async def upload_filefield_to_oss(file_field, token_data):
    file_info = token_data["data"]["file"]
    storage_info = token_data["data"]["storage"]

    auth = oss2.StsAuth(
        file_info["access_key_id"],
        file_info["access_key_secret"],
        file_info["security_token"],
    )
    bucket = oss2.Bucket(
        auth, f"http://{storage_info['endpoint']}", storage_info["bucket"]
    )

    try:
        result = bucket.put_object(
            file_info["object_key"],  # OSS存储路径
            file_field.file,  # 直接使用文件流对象
            headers={
                "Content-Type": file_field.content_type,  # 保留原始MIME类型
                "Content-Disposition": f"attachment; filename={secure_filename(file_field.filename)}",
            },
        )

        if result.status == 200:
            return {
                "status": result.status,
                "url": f"https://{storage_info['bucket']}.{storage_info['endpoint']}/{file_info['object_key']}",
            }
        else:
            return {
                "status": result.status,
                "reason": f"OSS返回状态码: {result.status}",
            }

    except Exception as e:
        return {"status": 500, "reason": str(e)}


async def commit_file(object_key: str, filename: str, api_key: str):
    url = f"{BIZYDRAFT_SERVER}/input_resource/commit"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "object_key": object_key,
        "name": filename,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            response.raise_for_status()


async def upload_to_oss(post, api_key: str):
    from bizydraft.oss_utils import get_upload_token

    image = post.get("image")
    overwrite = post.get("overwrite")
    image_upload_type = post.get("type")
    subfolder = post.get("subfolder", "")
    logger.debug(f"{image=}, {overwrite=}, {image_upload_type=}, {subfolder=}")

    if not (image and image.file):
        return web.Response(status=400)

    filename = image.filename
    if not filename:
        return web.Response(status=400)

    oss_token = await get_upload_token(filename, api_key)
    result = await upload_filefield_to_oss(image, oss_token)
    if result["status"] != 200:
        return web.Response(status=result["status"], text=result.get("reason", ""))
    logger.debug(f"upload file: {result['url']}")
    try:
        object_key = oss_token["data"]["file"]["object_key"]
        await commit_file(object_key, filename, api_key)
        logger.debug(f"sucess: commit {filename=}")
    except Exception as e:
        logger.error(f"Commit file failed: {e}")
        return web.Response(status=500, text=str(e))
    return web.json_response(
        {"name": result["url"], "subfolder": subfolder, "type": image_upload_type}
    )


def get_api_key(request):
    if BIZYAIR_API_KEY:
        return BIZYAIR_API_KEY

    cookies = request.headers.get("Cookie")
    if not cookies:
        return None

    try:
        cookie = SimpleCookie()
        cookie.load(cookies)

        bizy_token = cookie.get("bizy_token").value if "bizy_token" in cookie else None

        decrypted_token = decrypt(bizy_token)
        api_key = decrypted_token if decrypted_token else None

    except Exception as e:
        logger.error(f"error happens when get_api_key from cookies: {e}")
        return None

    return api_key


async def upload_image(request):
    logger.debug(f"Received request to upload image: {request.path}")
    api_key = get_api_key(request)
    if not api_key:
        return web.Response(status=403, text="No validated key found")
    post = await request.post()
    return await upload_to_oss(post, api_key)
