"""Project information loaded from pyproject.toml."""

import tomllib
from pathlib import Path


def get_project_info():
    """从 pyproject.toml 读取项目信息"""
    # 定位到项目根目录的 pyproject.toml
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        authors = project.get("authors", [{}])
        urls = project.get("urls", {})

        return {
            "name": project.get("name", "mdtt"),
            "version": project.get("version", "unknown"),
            "description": project.get("description", "MDict pack/unpack tool"),
            "author": authors[0].get("name", "") if authors else "",
            "email": authors[0].get("email", "") if authors else "",
            "url": urls.get("Homepage", ""),
            "license_type": project.get("license", {}).get("text", "MIT"),
        }
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        # 如果无法读取 pyproject.toml，使用默认值
        return {
            "name": "mdtt",
            "version": "2.0",
            "description": "MDx Dict Trans ToolKit",
            "author": "Libukai",
            "email": "xiaobuyao@gmail.com",
            "url": "https://github.com/likai/mdtt",
            "license_type": "MIT",
        }


# 兼容旧的导入方式
_info = get_project_info()
name = _info["name"]
version = _info["version"]
description = _info["description"]
author = _info["author"]
email = _info["email"]
url = _info["url"]
license_type = _info["license_type"]
