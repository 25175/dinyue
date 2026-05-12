#!/usr/bin/env python3
"""Generate files, commit changes, and push to GitHub.

Normal usage after editing xiugai.yaml:

    python3 scripts/update_github.py

Optional custom commit message:

    python3 scripts/update_github.py -m "update custom rules"

What it does:
1. Run scripts/generate.py to refresh all generated files.
2. Validate generated YAML/JSON/list outputs.
3. Show git status.
4. Commit changed files.
5. Push to the current branch on origin.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    if result.returncode != 0:
        if capture and result.stdout:
            print(result.stdout)
        raise SystemExit(result.returncode)
    return result.stdout or ""


def validate_outputs() -> int:
    source = yaml.safe_load((ROOT / "xiugai.yaml").read_text(encoding="utf-8"))
    clash = yaml.safe_load((ROOT / "clash/custom.yaml").read_text(encoding="utf-8"))
    mihomo = yaml.safe_load((ROOT / "mihomo/custom.yaml").read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not isinstance(source.get("rules"), list):
        raise SystemExit("xiugai.yaml 格式错误：需要包含 rules: 列表")
    if clash != mihomo:
        raise SystemExit("clash/custom.yaml 和 mihomo/custom.yaml 内容不一致")
    payload = clash.get("payload")
    if not isinstance(payload, list) or not payload:
        raise SystemExit("clash/custom.yaml 缺少 payload 规则")
    rules_lines = [
        line for line in (ROOT / "rules/custom.list").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    if rules_lines != payload:
        raise SystemExit("生成文件不一致：rules/custom.list 和 clash payload 应相同")

    surge_summary = ROOT / "surge/custom.list"
    surge_rule_sets = ROOT / "surge/rule-set-lines.conf"
    split_dir = ROOT / "surge/split"
    if not surge_summary.exists() or not surge_rule_sets.exists() or not split_dir.is_dir():
        raise SystemExit("Surge 生成文件缺失：需要 surge/custom.list、surge/rule-set-lines.conf、surge/split/")
    if "RULE-SET," not in surge_rule_sets.read_text(encoding="utf-8"):
        raise SystemExit("surge/rule-set-lines.conf 缺少 RULE-SET 行")
    if not list(split_dir.glob("*.list")):
        raise SystemExit("surge/split/ 没有生成按策略拆分的 list 文件")

    json.loads((ROOT / "sing-box/custom-source.json").read_text(encoding="utf-8"))
    return len(payload)


def current_branch() -> str:
    branch = run(["git", "branch", "--show-current"], capture=True).strip()
    if not branch:
        raise SystemExit("无法识别当前 git 分支")
    return branch


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate, commit, and push dinyue rules to GitHub.")
    parser.add_argument("-m", "--message", default="update custom proxy rules", help="git commit message")
    parser.add_argument("--no-push", action="store_true", help="只生成和提交，不 push 到 GitHub")
    args = parser.parse_args()

    print("1/5 生成文件：python3 scripts/generate.py")
    run([sys.executable, "scripts/generate.py"])

    print("2/5 验证生成结果")
    count = validate_outputs()
    print(f"验证通过：{count} 条规则")

    status = run(["git", "status", "--short"], capture=True)
    if not status.strip():
        print("没有发现需要提交的更改。")
        return

    print("3/5 当前改动：")
    print(status, end="")

    print("4/5 git add + commit")
    run(["git", "add", "README.md", "xiugai.yaml", "rules", "surge", "clash", "mihomo", "loon", "quanx", "sing-box", "scripts", ".github/workflows"])
    run(["git", "commit", "-m", args.message])

    if args.no_push:
        print("已提交本地 commit；按 --no-push 要求未推送。")
        return

    branch = current_branch()
    print(f"5/5 push 到 GitHub：origin {branch}")
    run(["git", "push", "origin", branch])
    print("完成：GitHub 仓库已更新。")


if __name__ == "__main__":
    main()
