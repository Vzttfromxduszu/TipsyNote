"""头像 URL 规范化工具"""
from pathlib import Path


def normalize_avatar_url(url: str | None) -> str | None:
    """将旧格式的头像路径转为前端可访问的 URL。

    - 已规范化的 /api/avatars/xxx 直接返回
    - 旧格式的绝对/相对路径提取文件名后转为 /api/avatars/xxx
    """
    if not url:
        return None
    if url.startswith("/api/avatars/"):
        return url
    # 从任意路径中提取文件名
    filename = Path(url).name
    if filename:
        return f"/api/avatars/{filename}"
    return None
