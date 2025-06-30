#!/usr/bin/env python3
"""
更新 README.md 中的 release notes 脚本
"""

import json
import os
import re
from datetime import datetime
from typing import Optional
from urllib.request import Request, urlopen


def get_github_releases(repo: str, token: Optional[str] = None) -> list[dict]:
    """获取 GitHub releases 信息"""
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-Script",
    }

    if token:
        headers["Authorization"] = f"token {token}"

    request = Request(url, headers=headers)
    with urlopen(request) as response:
        return json.loads(response.read().decode())


def is_prerelease_version(tag: str) -> bool:
    """判断是否为预发布版本"""
    return any(
        keyword in tag.lower() for keyword in ["alpha", "beta", "rc", "pre", "dev"]
    )


def find_latest_releases(
    releases: list[dict], include_drafts: bool = False
) -> tuple[Optional[dict], Optional[dict]]:
    """处理版本列表，查找最新的正式版和预发布版"""
    latest_release = None
    latest_prerelease = None

    for release in releases:
        if release["draft"] and not include_drafts:
            continue

        if release["prerelease"] or is_prerelease_version(release["tag_name"]):
            if latest_prerelease is None:
                latest_prerelease = release
        else:
            if latest_release is None:
                latest_release = release

    return latest_release, latest_prerelease


def format_release_content(release: dict, is_prerelease: bool = False) -> str:
    """格式化 release 内容"""
    title = release["name"] or release["tag_name"]
    body = release["body"] or ""
    tag_name = release["tag_name"]
    html_url = release["html_url"]
    published_at = release["published_at"]

    # 解析发布日期，转换为 YYYY-MM-DD 格式
    publish_date = datetime.fromisoformat(published_at.replace("Z", "+00:00")).strftime(
        "%Y-%m-%d"
    )

    # 构建 GitHub 链接
    repo_url = html_url.rsplit("/", 2)[0]  # 获取仓库 URL
    tag_url = f"{repo_url}/tree/{tag_name}"

    # 清理 body 内容，移除多余的空行
    body = re.sub(r"\n(?:\s*\n){2,}", "\n\n", body.strip())

    # 根据是否为预发布版本添加不同的标识
    label = "### 最新预览版本" if is_prerelease else "### 最新正式版本"

    content = f"{label}\n"
    content += f"- [{title}]({html_url}) - [{tag_name}]({tag_url}) - {publish_date}\n"
    content += f"> # {title}\n>\n"

    if body:
        # 将 body 内容转换为引用块格式
        quoted_body = "\n".join(
            f"> {line}" if line.strip() else ">" for line in body.split("\n")
        )
        content += f"{quoted_body}\n"

    return content


def update_readme_changelog(
    readme_path: str, latest_release: Optional[dict], latest_prerelease: Optional[dict]
) -> bool:
    """更新 README.md 中的 changelog 部分"""
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # 准备 release 内容
    release_content = ""
    if latest_release:
        release_content = format_release_content(latest_release, is_prerelease=False)

    # 准备 prerelease 内容
    prerelease_content = ""
    if latest_prerelease and latest_release:
        # 检查预发布版本是否比正式版本更新
        if latest_prerelease["created_at"] > latest_release["created_at"]:
            prerelease_content = format_release_content(
                latest_prerelease, is_prerelease=True
            )
    elif latest_prerelease and not latest_release:
        # 如果没有正式版本，只有预发布版本
        prerelease_content = format_release_content(
            latest_prerelease, is_prerelease=True
        )

    # 更新 RELEASE_CHANGELOG 部分
    release_pattern = (
        r"(<!-- RELEASE_CHANGELOG_START -->)(.*?)(<!-- RELEASE_CHANGELOG_END -->)"
    )
    release_replacement = f"\\1\n{release_content}\n\\3"
    content = re.sub(release_pattern, release_replacement, content, flags=re.DOTALL)

    # 更新 PRERELEASE_CHANGELOG 部分
    prerelease_pattern = (
        r"(<!-- PRERELEASE_CHANGELOG_START -->)(.*?)(<!-- PRERELEASE_CHANGELOG_END -->)"
    )
    prerelease_replacement = f"\\1\n{prerelease_content}\n\\3"
    content = re.sub(
        prerelease_pattern, prerelease_replacement, content, flags=re.DOTALL
    )

    # 写回文件
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    repo = "LuoChu-NB2Dev/nonebot-plugin-noadpls"
    readme_path = "README.md"
    token = os.getenv("GITHUB_TOKEN")

    # 检查是否在发布工作流中，如果是则包含草稿版本
    include_drafts = os.getenv("GITHUB_WORKFLOW") == "Release"

    releases = get_github_releases(repo, token)
    latest_release, latest_prerelease = find_latest_releases(releases, include_drafts)

    update_readme_changelog(readme_path, latest_release, latest_prerelease)


if __name__ == "__main__":
    main()
