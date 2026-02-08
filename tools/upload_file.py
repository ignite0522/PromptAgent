"""文件上传工具：multipart/form-data 上传，用于文件上传类 CTF。"""
import base64
import json

import requests
from langchain_core.tools import tool


@tool
def upload_file(
    url: str,
    filename: str,
    content_text: str | None = None,
    content_base64: str | None = None,
    field_name: str = "file",
    extra_form: dict | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    max_chars: int | None = None,
):
    """
    向目标 URL 以 multipart/form-data 方式上传文件。
    - url: 上传接口地址（如 https://xxx/upload.php）
    - filename: 上传时使用的文件名（可用来测双后缀、大小写等绕过，如 shell.php、shell.phtml、shell.php.jpg）
    - content_text: 文件内容（纯文本，如 PHP webshell）。与 content_base64 二选一
    - content_base64: 文件内容（Base64 编码，用于图片马等二进制）。与 content_text 二选一
    - field_name: 表单中文件字段名，默认 "file"
    - extra_form: 额外表单字段，如 {"submit": "1"}
    - headers/cookies: 可选
    - max_chars: 响应体截断长度
    """
    if content_text is None and content_base64 is None:
        return json.dumps({"error": "必须提供 content_text 或 content_base64 之一"}, ensure_ascii=False)

    try:
        if content_text is not None:
            payload = content_text.encode("utf-8")
        else:
            payload = base64.b64decode(content_base64)

        if headers is None:
            headers = {}
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS 10_15_7) CTF-Agent/1.0"
        }
        default_headers.update(headers)

        encoded_cookies = {k: str(v) for k, v in cookies.items()} if cookies else None

        files = {field_name: (filename, payload)}
        data = dict(extra_form) if extra_form else None

        resp = requests.post(
            url,
            files=files,
            data=data,
            headers=default_headers,
            cookies=encoded_cookies,
            timeout=15,
            allow_redirects=False,
        )

        content = resp.text if max_chars is None else resp.text[:max_chars]
        result = {
            "status_code": resp.status_code,
            "reason": resp.reason,
            "headers": dict(resp.headers),
            "content": content,
        }
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"上传失败: {str(e)}"}, ensure_ascii=False)
