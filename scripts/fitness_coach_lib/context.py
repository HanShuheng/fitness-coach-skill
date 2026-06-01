from __future__ import annotations

from itertools import islice

from .settings import DAILY_DIR, MONTHLY_SUMMARY_DIR, PROFILE_FILE, WEEKLY_SUMMARY_DIR


def read_tail(path, max_chars: int = 1200) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    return text[-max_chars:]


def build_context(topic: str) -> int:
    print(f"# 用户健身饮食上下文（topic: {topic}）")
    print("")
    profile = read_tail(PROFILE_FILE, 2200)
    if profile:
        print("## 基础档案")
        print(profile)
        print("")
    print("## 最近14天记录")
    files = sorted(DAILY_DIR.glob("*.md"), reverse=True)
    for path in islice(files, 14):
        print(f"### {path.stem}")
        print(read_tail(path, 900))
        print("")
    print("## 最近周摘要")
    for path in islice(sorted(WEEKLY_SUMMARY_DIR.glob("*.md"), reverse=True), 8):
        print(read_tail(path, 700))
        print("")
    print("## 最近月摘要")
    for path in islice(sorted(MONTHLY_SUMMARY_DIR.glob("*.md"), reverse=True), 3):
        print(read_tail(path, 700))
        print("")
    return 0


def summarize(period: str) -> int:
    from .settings import now_local
    from .storage import atomic_write_text

    if period not in {"weekly", "monthly"}:
        raise ValueError("period must be weekly or monthly")
    target_dir = WEEKLY_SUMMARY_DIR if period == "weekly" else MONTHLY_SUMMARY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    name = now_local().strftime("%Y-W%U" if period == "weekly" else "%Y-%m")
    lines = [f"# {period} summary {name}", "", "## 自动摘要占位", ""]
    for path in sorted(DAILY_DIR.glob("*.md"), reverse=True)[:14]:
        lines.append(f"- {path.stem}: 已记录")
    out = target_dir / f"{name}.md"
    atomic_write_text(out, "\n".join(lines) + "\n")
    print(f"OK summary written: {out}")
    return 0
