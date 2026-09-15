"""检查论文 Markdown 的格式、引用与研究方向一致性。"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONTENT_FILES = [ROOT / "proposals" / "thesis_proposal.md"]
CONTENT_FILES.extend(sorted((ROOT / "chapters").glob("*.md")))
TERMINOLOGY_FILES = [ROOT / "README.md", ROOT / "outline.md", *CONTENT_FILES]


def display_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def extract_title(path: Path) -> str | None:
    content = path.read_text(encoding="utf-8")
    if path.name == "README.md":
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    else:
        match = re.search(r"^\*\*题目：\*\*(.+)$", content, re.MULTILINE)
        if not match:
            match = re.search(r"^\*\*论文题目：\*\*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def bib_keys() -> set[str]:
    bib_path = ROOT / "references.bib"
    if not bib_path.exists():
        return set()
    return set(
        re.findall(
            r"@\w+\s*\{\s*([^,\s]+)\s*,",
            bib_path.read_text(encoding="utf-8"),
            re.IGNORECASE,
        )
    )


def check_markdown_rules() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    known_bib_keys = bib_keys()

    for path in CONTENT_FILES:
        content = path.read_text(encoding="utf-8")
        relative = display_path(path)

        if re.search(r"!\[.*?\]\([A-Za-z]:[/\\]", content):
            errors.append(f"{relative} 包含绝对路径图片引用")

        if content.count("$$") % 2 != 0:
            errors.append(f"{relative} 存在未闭合的块级公式 $$")

        inline_math = re.findall(r"(?<!\$)\$([^$\n]+)\$(?!\$)", content)
        if any(re.search(r"[，。！？]", formula) for formula in inline_math):
            warnings.append(f"{relative} 的 LaTeX 行内公式中疑似包含中文标点")

        used_keys = set(re.findall(r"\[@([A-Za-z0-9_.:-]+)", content))
        for key in sorted(used_keys - known_bib_keys):
            errors.append(f"{relative} 使用了 references.bib 中不存在的引用键 @{key}")

    title_sources = [
        ROOT / "README.md",
        ROOT / "outline.md",
        ROOT / "proposals" / "thesis_proposal.md",
    ]
    titles = {display_path(path): extract_title(path) for path in title_sources}
    canonical_title = titles["README.md"]
    for relative, title in titles.items():
        if title is None:
            errors.append(f"{relative} 未找到论文题目")
        elif canonical_title is not None and title != canonical_title:
            errors.append(f"{relative} 的论文题目与 README.md 不一致")

    proposal = (ROOT / "proposals" / "thesis_proposal.md").read_text(encoding="utf-8")
    obsolete_claims = (
        "拟研究的混合精度量化不主动丢弃令牌",
        "在全量缓存可访问的前提下减少数值表示开销",
        "本课题保留全量缓存并压缩表示",
    )
    for claim in obsolete_claims:
        if claim in proposal:
            errors.append(f"proposals/thesis_proposal.md 仍包含旧研究方向表述：{claim}")

    deprecated_terms = {
        "令牌": "token",
        "提示词": "prompt",
        "预填充": "Prefill",
        "解码": "Decode",
        "注意力汇聚点": "Attention Sink",
        "键值头": "KV head",
        "分页缓存": "Paged KV Cache",
        "连续批处理": "Continuous Batching",
    }
    for path in TERMINOLOGY_FILES:
        content = path.read_text(encoding="utf-8")
        relative = display_path(path)
        for deprecated, preferred in deprecated_terms.items():
            if deprecated in content:
                errors.append(
                    f"{relative} 使用了非约定术语“{deprecated}”，应改为“{preferred}”"
                )

    for message in errors:
        print(f"[错误] {message}")
    for message in warnings:
        print(f"[提示] {message}")

    if errors:
        print(f"检查失败：{len(errors)} 个错误，{len(warnings)} 个提示。")
        return 1

    print(
        f"检查通过：已检查 {len(TERMINOLOGY_FILES)} 个 Markdown 文件，"
        f"{len(known_bib_keys)} 个参考文献条目。"
    )
    if warnings:
        print(f"另有 {len(warnings)} 个非阻断提示。")
    return 0


if __name__ == "__main__":
    sys.exit(check_markdown_rules())
