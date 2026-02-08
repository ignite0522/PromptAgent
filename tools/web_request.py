"""HTTP 请求工具。"""
import json
from typing import Literal
from urllib.parse import quote_plus

import requests
from langchain_core.tools import tool



@tool
def web_request(
    url: str,
    method: Literal["GET", "POST"] = "GET",
    params: dict | None = None,
    data: dict | None = None,
    json_data: dict | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    max_chars: int | None = None,
):
    """
    发起 HTTP 请求。
    - url: 目标 URL
    - method: GET/POST
    - params/data/json_data/headers/cookies: 可选参数（cookies 传 dict，如 {"PHPSESSID": "..."}，值将原样传递）
    - max_chars: 返回体截断长度
    """

    session = requests.Session()
    session.trust_env = False

    try:
        if headers is None:
            headers = {}

        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) CTF-Agent/1.0"
        }
        if headers:
            default_headers.update(headers)

        # cookies 直接原样传递（保持原始值，不做 URL 编码）
        encoded_cookies = None
        if cookies:
            # 确保所有 cookie 值为字符串
            encoded_cookies = {k: str(v) for k, v in cookies.items()}

        req = requests.Request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=default_headers,
            cookies=encoded_cookies,
        )
        prepped = session.prepare_request(req)

        response = session.send(
            prepped,
            timeout=10,
            allow_redirects=False,
        )

        result = {
            "status_code": response.status_code,
            "reason": response.reason,
            "headers": dict(response.headers),
            "content": response.text if max_chars is None else response.text[:max_chars],
        }

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"请求执行失败: {str(e)}"
