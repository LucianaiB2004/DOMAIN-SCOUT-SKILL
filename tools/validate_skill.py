#!/usr/bin/env python3
from pathlib import Path
import re
import sys


REQUIRED_SECTIONS = [
    "## 1. 目标是什么",
    "## 2. 什么情况下触发",
    "## 3. 什么情况下不要触发",
    "## 4. 开始前先收集什么信息",
    "## 5. 按什么顺序干活",
    "## 6. 输出必须长什么样",
    "## 7. 做到什么程度算完成",
    "## 8. 搞不定的时候怎么处理",
    "## 9. 什么时候去读参考文件",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate(skill_dir: Path) -> None:
    if not skill_dir.is_dir():
        fail(f"not a directory: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        fail("missing SKILL.md")

    for name in ["scripts", "references", "assets"]:
        if not (skill_dir / name).is_dir():
            fail(f"missing {name}/")

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")

    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("invalid YAML frontmatter boundary")

    frontmatter = match.group(1)
    if not re.search(r"^name:\s*domain-scout\s*$", frontmatter, re.MULTILINE):
        fail("frontmatter must include name: domain-scout")

    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not description_match:
        fail("frontmatter must include description")

    description = description_match.group(1)
    for keyword in ["功能", "触发关键词", "排除条件"]:
        if keyword not in description:
            fail(f"description missing {keyword}")

    body = text[match.end():]
    if len(body.splitlines()) > 500:
        fail("SKILL.md body exceeds 500 lines")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            fail(f"missing section: {section}")

    example = skill_dir / "references" / "output-example.md"
    if not example.is_file():
        fail("missing references/output-example.md")

    example_text = example.read_text(encoding="utf-8")
    for marker in ["正确示例", "错误示例", "完整输入到输出示例"]:
        if marker not in example_text:
            fail(f"output-example.md missing {marker}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: python tools/validate_skill.py <skill-dir>")

    skill_dir = Path(sys.argv[1]).resolve()
    validate(skill_dir)
    print(f"Skill is valid: {skill_dir.name}")


if __name__ == "__main__":
    main()
