"""读取指定 URL 的页面/文件内容。"""
import requests

from langchain_core.tools import tool


@tool
def read_web_file(url: str, max_chars: int | None = None):
    """
    读取指定 URL 的页面/文件文本内容。
    """
    try:
        session = requests.Session()
        session.trust_env = False
        resp = session.get(url, timeout=5)
        text = resp.text
        if max_chars is not None:
            text = text[:max_chars]
        return f"文件内容:\n{text}"
    except Exception as e:
        return f"读取失败: {e}"
