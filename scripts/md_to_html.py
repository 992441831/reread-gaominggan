#!/usr/bin/env python3
"""
将 src/posts/*.md 转换为 docs/*.html
使用 scripts/template.html 作为页面模板。
"""

import re
import sys
from pathlib import Path

# Windows 控制台默认 GBK，强制使用 UTF-8 输出中文和特殊符号
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import markdown
    import yaml
    from bs4 import BeautifulSoup
    from jinja2 import Template
except ImportError as e:
    print(f"缺少依赖：{e}")
    print("请先安装依赖：pip install -r requirements.txt")
    sys.exit(1)


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src" / "posts"
OUT_DIR = ROOT / "docs"
TEMPLATE_PATH = ROOT / "scripts" / "template.html"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 Markdown 顶部的 YAML frontmatter，返回元数据和正文。"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return meta, body
            except yaml.YAMLError:
                pass
    return {}, content


def extract_title(html_content: str) -> str:
    """从 HTML 正文中提取第一个 <h1> 的纯文本作为标题。"""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.DOTALL)
    if match:
        return re.sub(r"<.*?>", "", match.group(1)).strip()
    return "未命名文章"


def extract_first_paragraph(html_content: str) -> str:
    """提取第一个 <p> 的纯文本作为描述。"""
    match = re.search(r"<p>(.*?)</p>", html_content, re.DOTALL)
    if match:
        text = re.sub(r"<.*?>", "", match.group(1)).strip()
        return text[:160]
    return ""


def remove_first_h1(html_content: str) -> str:
    """移除正文中的第一个 <h1>，避免与页面标题重复。"""
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", html_content, count=1, flags=re.DOTALL)


def convert_file(md_path: Path, template: Template) -> None:
    """转换单个 Markdown 文件为 HTML。"""
    raw_content = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw_content)

    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "nl2br",
        ]
    )
    html_body = md.convert(body)

    title = meta.get("title", extract_title(html_body))
    html_body = remove_first_h1(html_body)

    subtitle = meta.get("subtitle", "")
    description = meta.get("description") or extract_first_paragraph(html_body)
    reading_time = meta.get("reading_time", "")

    rendered = template.render(
        title=title,
        subtitle=subtitle,
        description=description,
        reading_time=reading_time,
        content=html_body,
    )

    # 使用 BeautifulSoup 美化 HTML 缩进
    soup = BeautifulSoup(rendered, "html.parser")
    pretty_html = soup.prettify()

    out_path = OUT_DIR / md_path.with_suffix(".html").name
    out_path.write_text(pretty_html, encoding="utf-8")
    print(f"[OK] 已生成：{out_path.relative_to(ROOT)}")


def main() -> None:
    if not SRC_DIR.exists():
        print(f"源目录不存在：{SRC_DIR}")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    template_content = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(template_content)

    md_files = sorted(SRC_DIR.glob("*.md"))
    if not md_files:
        print(f"在 {SRC_DIR} 中没有找到 Markdown 文件")
        sys.exit(0)

    print(f"发现 {len(md_files)} 个 Markdown 文件，开始转换...")
    for md_path in md_files:
        convert_file(md_path, template)

    print("\n转换完成！")


if __name__ == "__main__":
    main()
