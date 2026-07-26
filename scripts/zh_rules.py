"""xiugai2.yaml——全中文规则源的加载与转换。

xiugai2.yaml 用全中文字段与取值写规则，本模块把它翻译成与 xiugai.yaml
完全相同的规则结构（type/value/policy/option/comment），由 generate.py 与
sync_surge_family.py 追加到主规则列表之后，参与所有客户端产物生成。

写法示例：
  规则:
    - {类型: 域名后缀, 值: example.com, 策略: 代理, 备注: "说明"}
    - {类型: 域名, 值: api.example.com, 策略: AI}
    - {类型: IP段, 值: 1.2.3.4/32, 策略: 直连, 选项: no-resolve}
    - {类型: 域名后缀, 值: old.example.com, 策略: 拒绝, 启用: 否}
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

# 中文类型 → 规则类型（与 generate.py 的 ALLOWED_TYPES 对应）
TYPE_MAP = {
    "域名": "DOMAIN",
    "域名后缀": "DOMAIN-SUFFIX",
    "域名关键词": "DOMAIN-KEYWORD",
    "域名集": "DOMAIN-SET",
    "IP段": "IP-CIDR",
    "IPV6段": "IP-CIDR6",
    "地理IP": "GEOIP",
    "目标端口": "DST-PORT",
    "来源IP段": "SRC-IP-CIDR",
    "进程名": "PROCESS-NAME",
    "规则集": "RULE-SET",
}

# 英文类型直接透传时允许的集合（与 generate.py 保持一致）
CANONICAL_TYPES = set(TYPE_MAP.values())

# 中文策略 → xiugai.yaml 既有策略名
# （代理经 surge_policy_map 映射为 Surge 的 Proxy 组；日本映射为 🇯🇵 日本节点）
POLICY_MAP = {
    "代理": "👋 手动选择",
    "直连": "DIRECT",
    "全球直连": "🎯 全球直连",
    "拒绝": "REJECT",
    "拦截": "REJECT",
    "AI": "AIGC",
    "智能助理": "AIGC",
    "日本": "SF3",
    "日本节点": "SF3",
}

_FALSY = {"否", "关", "关闭", "no", "false", "0", False}


def _fail(msg: str) -> None:
    print(f"[xiugai2.yaml] {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_zh_rules(path: Path) -> list[dict]:
    """读取 xiugai2.yaml，返回翻译后的规则列表；文件不存在或为空返回 []。"""
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        _fail(f"YAML 解析失败：{exc}")
    if data is None:
        return []
    if not isinstance(data, dict):
        _fail("根节点必须是映射（以 `规则:` 开头）")
    raw = data.get("规则")
    if raw is None:
        return []
    if not isinstance(raw, list):
        _fail("`规则:` 必须是列表")

    out: list[dict] = []
    for idx, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            _fail(f"规则[{idx}] 必须是映射，如 {{类型: 域名, 值: x.com, 策略: 代理}}")

        enabled = item.get("启用", item.get("enabled", True))
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() not in {v for v in _FALSY if isinstance(v, str)}
        if enabled in _FALSY or enabled is False:
            continue

        rtype_zh = str(item.get("类型", item.get("type", ""))).strip()
        value = str(item.get("值", item.get("value", ""))).strip()
        policy_zh = str(item.get("策略", item.get("policy", ""))).strip()
        option = str(item.get("选项", item.get("option", "")) or "").strip()
        comment = str(item.get("备注", item.get("comment", "")) or "").strip()

        if not rtype_zh:
            _fail(f"规则[{idx}] 缺少 `类型`")
        if not value:
            _fail(f"规则[{idx}] 缺少 `值`")
        if not policy_zh:
            _fail(f"规则[{idx}] 缺少 `策略`")

        rtype = TYPE_MAP.get(rtype_zh, rtype_zh.upper())
        if rtype not in CANONICAL_TYPES:
            _fail(
                f"规则[{idx}] 未知类型 {rtype_zh!r}；"
                f"可用中文类型：{'、'.join(TYPE_MAP)}"
            )

        # 未收录的策略名原样透传（允许直接写 AIGC、SF3 或自定义组名）
        policy = POLICY_MAP.get(policy_zh, policy_zh)

        rule: dict = {"type": rtype, "value": value, "policy": policy}
        if option:
            rule["option"] = option
        if comment:
            rule["comment"] = comment
        out.append(rule)
    return out
