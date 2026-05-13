#!/usr/bin/env python3
"""Sync Rabbit-Spec Surge Family config and inject dinyue custom rules.

Outputs:
  - surge/上游/Rabbit-Spec/Conf/Spec/Surge-Family.conf
  - surge/上游/Rabbit-Spec/Rules/*.list
  - surge/generated/Surge-Family.conf
  - surge/generated/Rules/*.list
  - surge/generated/Dinyue-inline-rules.conf
"""
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import re
import shutil
import sys
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "xiugai.yaml"
UPSTREAM_ROOT = ROOT / "surge" / "上游" / "Rabbit-Spec"
GENERATED_ROOT = ROOT / "surge" / "generated"
GENERATED_RULES = GENERATED_ROOT / "Rules"

RABBIT_CONF_URL = "https://raw.githubusercontent.com/Rabbit-Spec/Surge/refs/heads/Master/Conf/Spec/Surge-Family.conf"
RABBIT_RAW_PREFIX_RE = re.compile(r"https://raw\.githubusercontent\.com/Rabbit-Spec/Surge/(?:refs/heads/)?Master/Rules/([^,\s]+)")
SELF_RAW_PREFIX = "https://raw.githubusercontent.com/25175/dinyue/main"

DEFAULT_SURGE_POLICY_MAP = {
    "🎯 全球直连": "DIRECT",
    "👋 手动选择": "Proxy",
    "SF3": "日本节点",
}

ALLOWED_TYPES = {
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-SET",
    "IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN",
    "DST-PORT", "SRC-IP-CIDR", "PROCESS-NAME", "RULE-SET",
}

# Verified in Surge with direct-keyword-test.list: DOMAIN-KEYWORD works in remote RULE-SET.
SURGE_REMOTE_RULE_TYPES = {
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-SET",
    "IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN",
}

# These can be ordinary [Rule] lines but are not emitted as remote ruleset entries here.
SURGE_INLINE_ONLY_TYPES = {"DST-PORT", "SRC-IP-CIDR", "PROCESS-NAME", "RULE-SET"}

SAFE_FILENAME_TABLE = {
    "DIRECT": "Dinyue-DIRECT.list",
    "REJECT": "Dinyue-REJECT.list",
    "REJECT-DROP": "Dinyue-REJECT-DROP.list",
    "REJECT-TINYGIF": "Dinyue-REJECT-TINYGIF.list",
    "Proxy": "Dinyue-Proxy.list",
    "日本节点": "Dinyue-日本节点.list",
    "AIGC": "Dinyue-AIGC.list",
    "Apple": "Dinyue-Apple.list",
    "Telegram": "Dinyue-Telegram.list",
    "Netflix": "Dinyue-Netflix.list",
    "Disney+": "Dinyue-DisneyPlus.list",
    "YouTube": "Dinyue-YouTube.list",
    "Spotify": "Dinyue-Spotify.list",
    "TikTok": "Dinyue-TikTok.list",
    "BiliBili": "Dinyue-BiliBili.list",
    "GlobalMedia": "Dinyue-GlobalMedia.list",
    "Microsoft": "Dinyue-Microsoft.list",
    "Google": "Dinyue-Google.list",
    "Game": "Dinyue-Game.list",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "dinyue-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_xiugai() -> tuple[list[dict[str, str]], dict[str, str]]:
    if not SOURCE.exists():
        fail(f"missing source file: {SOURCE}")
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("xiugai.yaml root must be a mapping")
    raw_rules = data.get("rules")
    if not isinstance(raw_rules, list):
        fail("xiugai.yaml rules must be a list")
    mapping = dict(DEFAULT_SURGE_POLICY_MAP)
    user_map = data.get("surge_policy_map") or {}
    if not isinstance(user_map, dict):
        fail("surge_policy_map must be a mapping")
    mapping.update({str(k).strip(): str(v).strip() for k, v in user_map.items()})

    rules: list[dict[str, str]] = []
    for idx, item in enumerate(raw_rules, 1):
        if not isinstance(item, dict):
            fail(f"rules[{idx}] must be a mapping")
        if item.get("enabled", True) is False:
            continue
        rtype = str(item.get("type", "")).strip().upper()
        value = str(item.get("value", "")).strip()
        policy = str(item.get("policy", "")).strip()
        option = str(item.get("option", "")).strip() if item.get("option") is not None else ""
        if not rtype or rtype not in ALLOWED_TYPES:
            fail(f"rules[{idx}] unsupported or missing type: {rtype!r}")
        if not value:
            fail(f"rules[{idx}] missing value")
        if not policy:
            fail(f"rules[{idx}] missing policy")
        for name, val in [("type", rtype), ("value", value), ("policy", policy), ("option", option)]:
            if "\n" in val or "\r" in val:
                fail(f"rules[{idx}] {name} must be one line")
        rules.append({"type": rtype, "value": value, "policy": policy, "option": option})
    return rules, mapping


def rule_line(rule: dict[str, str], *, include_policy: bool, policy: str | None = None) -> str:
    parts = [rule["type"], rule["value"]]
    if include_policy:
        parts.append(policy if policy is not None else rule["policy"])
    if rule.get("option"):
        parts.append(rule["option"])
    return ",".join(parts)


def safe_filename(policy: str) -> str:
    if policy in SAFE_FILENAME_TABLE:
        return SAFE_FILENAME_TABLE[policy]
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in policy).strip("-") or "Policy"
    return f"Dinyue-{cleaned}.list"


def split_sections(conf_text: str) -> tuple[list[str], list[str], list[str], list[str]]:
    lines = conf_text.splitlines()
    before_rule: list[str] = []
    rule_header: list[str] = []
    rule_body: list[str] = []
    after_rule: list[str] = []
    state = "before"
    for line in lines:
        if re.match(r"^\[Rule\]\s*$", line.strip()):
            state = "rule"
            rule_header.append(line)
            continue
        if state == "rule" and re.match(r"^\[.+\]\s*$", line.strip()):
            state = "after"
            after_rule.append(line)
            continue
        if state == "before":
            before_rule.append(line)
        elif state == "rule":
            rule_body.append(line)
        else:
            after_rule.append(line)
    if not rule_header:
        fail("upstream config missing [Rule] section")
    return before_rule, rule_header, rule_body, after_rule


def upstream_rule_path(name: str) -> Path:
    return UPSTREAM_ROOT / "Rules" / name


def generated_rule_path(name: str) -> Path:
    return GENERATED_RULES / name


def mirror_upstream(conf_text: str) -> list[str]:
    write(UPSTREAM_ROOT / "Conf" / "Spec" / "Surge-Family.conf", conf_text + ("\n" if not conf_text.endswith("\n") else ""))
    names = []
    for name in OrderedDict.fromkeys(RABBIT_RAW_PREFIX_RE.findall(conf_text)):
        names.append(name)
        url = f"https://raw.githubusercontent.com/Rabbit-Spec/Surge/refs/heads/Master/Rules/{name}"
        text = fetch_text(url)
        write(upstream_rule_path(name), text + ("\n" if not text.endswith("\n") else ""))
        write(generated_rule_path(name), text + ("\n" if not text.endswith("\n") else ""))
    return names


def build_dinyue_rules(rules: list[dict[str, str]], mapping: dict[str, str]) -> tuple[list[str], list[str], OrderedDict[str, str]]:
    buckets: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    inline: list[str] = []
    for rule in rules:
        policy = mapping.get(rule["policy"], rule["policy"])
        if rule["type"] in SURGE_REMOTE_RULE_TYPES:
            buckets.setdefault(policy, []).append(rule)
        elif rule["type"] in SURGE_INLINE_ONLY_TYPES:
            inline.append(rule_line(rule, include_policy=True, policy=policy))
        else:
            inline.append(rule_line(rule, include_policy=True, policy=policy))

    rule_set_lines: list[str] = []
    policy_to_file: OrderedDict[str, str] = OrderedDict()
    for policy, bucket in buckets.items():
        filename = safe_filename(policy)
        policy_to_file[policy] = filename
        out = [
            f"# Dinyue 自定义规则：{policy}",
            "# 源数据：xiugai.yaml；由 scripts/sync_surge_family.py 自动生成。",
            "# 本文件为 Surge 外部 RULE-SET 匹配条件，不包含策略列。",
            "",
        ]
        out.extend(rule_line(rule, include_policy=False) for rule in bucket)
        write(generated_rule_path(filename), "\n".join(out) + "\n")
        rule_set_lines.append(
            f"RULE-SET,{SELF_RAW_PREFIX}/surge/generated/Rules/{filename},{policy},extended-matching"
        )
    return rule_set_lines, inline, policy_to_file


def rewrite_upstream_rule_line(line: str) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        return f"{SELF_RAW_PREFIX}/surge/generated/Rules/{name}"
    return RABBIT_RAW_PREFIX_RE.sub(repl, line)


def build_generated_conf(conf_text: str, dinyue_rule_set_lines: list[str], inline_lines: list[str]) -> str:
    before, header, rule_body, after = split_sections(conf_text)
    new_rule_body: list[str] = []
    new_rule_body.extend([
        "# ============================================================",
        "# Dinyue 自定义规则（优先匹配）",
        "# 源数据：xiugai.yaml；生成规则：surge/generated/Rules/Dinyue-*.list",
        "# ============================================================",
    ])
    if dinyue_rule_set_lines:
        new_rule_body.extend(dinyue_rule_set_lines)
    else:
        new_rule_body.append("# 当前没有可生成远程 RULE-SET 的 Dinyue 自定义规则")
    if inline_lines:
        new_rule_body.extend([
            "# ------------------------------------------------------------",
            "# Dinyue 需手动内联/特殊规则：已另存 surge/generated/Dinyue-inline-rules.conf",
            "# 如需完整生效，请按需把这些行直接放入 [Rule] 靠前位置。",
            "# ------------------------------------------------------------",
        ])
        new_rule_body.extend(f"# {line}" for line in inline_lines)
    new_rule_body.extend([
        "",
        "# ============================================================",
        "# Rabbit-Spec 上游规则（URL 已改写到本仓库镜像）",
        "# 上游备份：surge/上游/Rabbit-Spec/",
        "# ============================================================",
    ])
    for line in rule_body:
        new_rule_body.append(rewrite_upstream_rule_line(line))

    parts = []
    parts.extend(before)
    parts.extend(header)
    parts.extend(new_rule_body)
    parts.extend(after)
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    # Keep generated output deterministic: remove old generated rules before rebuilding.
    # Do not remove surge/上游 blindly outside the Rabbit-Spec subtree.
    if GENERATED_RULES.exists():
        shutil.rmtree(GENERATED_RULES)
    conf_text = fetch_text(RABBIT_CONF_URL)
    upstream_names = mirror_upstream(conf_text)
    rules, mapping = load_xiugai()
    dinyue_rule_set_lines, inline_lines, policy_to_file = build_dinyue_rules(rules, mapping)
    generated_conf = build_generated_conf(conf_text, dinyue_rule_set_lines, inline_lines)
    write(GENERATED_ROOT / "Surge-Family.conf", generated_conf)
    write(GENERATED_ROOT / "Dinyue-inline-rules.conf", "\n".join([
        "# Dinyue 自定义规则：无法/不建议放入 Surge 外部 RULE-SET 的内联规则",
        "# 如需完整生效，请把下方规则直接复制到 Surge [Rule] 靠前位置。",
        "# 源数据：xiugai.yaml；由 scripts/sync_surge_family.py 自动生成。",
        "",
        *inline_lines,
        "",
    ]))
    write(GENERATED_ROOT / "README.md", "\n".join([
        "# Dinyue Surge Family 生成目录",
        "",
        "- `Surge-Family.conf`：基于 Rabbit-Spec 上游配置生成，已插入 Dinyue 自定义规则区块。",
        "- `Rules/`：Rabbit 上游规则镜像 + Dinyue 自定义规则集。",
        "- `Dinyue-inline-rules.conf`：少数需要手动内联的规则。",
        "- 上游原始备份在 `surge/上游/Rabbit-Spec/`。",
        "",
    ]))
    print(f"mirrored upstream rules: {len(upstream_names)}")
    print("dinyue remote policies:", ", ".join(policy_to_file.keys()) or "none")
    print(f"dinyue inline rules: {len(inline_lines)}")
    print(f"generated: {GENERATED_ROOT / 'Surge-Family.conf'}")


if __name__ == "__main__":
    main()
