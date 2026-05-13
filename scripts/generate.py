#!/usr/bin/env python3
"""Generate proxy rule files from xiugai.yaml.

Only edit xiugai.yaml for normal maintenance.
The script keeps Clash/Mihomo policy names as-is, and generates Surge files with
policy mapping + split RULE-SET lists so Surge can use its own strategy groups.
"""
from pathlib import Path
from collections import OrderedDict
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'xiugai.yaml'

ALLOWED_TYPES = {
    'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'DOMAIN-SET',
    'IP-CIDR', 'IP-CIDR6', 'GEOIP', 'DST-PORT', 'SRC-IP-CIDR',
    'PROCESS-NAME', 'RULE-SET',
}

DEFAULT_SURGE_POLICY_MAP = {
    '🎯 全球直连': 'DIRECT',
    '👋 手动选择': 'Proxy',
    'SF3': '🇯🇵 日本节点',
}

BUILTIN_POLICIES = {'DIRECT', 'REJECT', 'REJECT-DROP', 'REJECT-TINYGIF', 'Proxy'}

# Surge external RULE-SET files are stricter than normal [Rule] lines. Keep only
# commonly supported match-only rule types in remote split lists. Port rules,
# nested RULE-SET references, process rules, etc. are emitted as inline rules for
# manual copy instead of breaking the whole external rule-set parse.
# Keep DOMAIN-KEYWORD inline for Surge. Some Surge versions/configs are picky
# about DOMAIN-KEYWORD inside external rule-set files; inline [Rule] form is safer
# for important keyword rules such as mtyy/mt.
# If a keyword also needs Surge remote split matching, add real DOMAIN/DOMAIN-SUFFIX rules.
SURGE_REMOTE_RULE_TYPES = {'DOMAIN', 'DOMAIN-SUFFIX', 'IP-CIDR', 'IP-CIDR6', 'GEOIP'}


def fail(message):
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)


def load_source():
    if not SOURCE.exists():
        fail(f'missing source file: {SOURCE}')
    try:
        data = yaml.safe_load(SOURCE.read_text(encoding='utf-8'))
    except yaml.YAMLError as exc:
        fail(f'YAML parse failed in {SOURCE}: {exc}')
    if not isinstance(data, dict):
        fail('source root must be a YAML mapping, with comments: and rules:')
    comments = data.get('comments') or []
    rules = data.get('rules')
    surge_policy_map = data.get('surge_policy_map') or {}
    if not isinstance(comments, list) or not all(isinstance(x, str) for x in comments):
        fail('comments must be a list of strings')
    if not isinstance(rules, list):
        fail('rules must be a list')
    if not isinstance(surge_policy_map, dict):
        fail('surge_policy_map must be a mapping')
    merged_map = dict(DEFAULT_SURGE_POLICY_MAP)
    merged_map.update({str(k).strip(): str(v).strip() for k, v in surge_policy_map.items()})
    return comments, rules, merged_map


def normalize_rule(item, index):
    if not isinstance(item, dict):
        fail(f'rules[{index}] must be a mapping')
    if item.get('enabled', True) is False:
        return None
    rtype = str(item.get('type', '')).strip().upper()
    value = str(item.get('value', '')).strip()
    policy = str(item.get('policy', '')).strip()
    option = str(item.get('option', '')).strip() if item.get('option') is not None else ''

    if not rtype:
        fail(f'rules[{index}] missing type')
    if rtype not in ALLOWED_TYPES:
        fail(f'rules[{index}] unsupported type {rtype!r}; allowed: {sorted(ALLOWED_TYPES)}')
    if not value:
        fail(f'rules[{index}] missing value')
    if not policy:
        fail(f'rules[{index}] missing policy')
    for field_name, field_value in [('type', rtype), ('value', value), ('policy', policy), ('option', option)]:
        if '\n' in field_value or '\r' in field_value:
            fail(f'rules[{index}] {field_name} must be one line')
    return {'type': rtype, 'value': value, 'policy': policy, 'option': option}


def rule_line(rule, policy=None, include_policy=True):
    parts = [rule['type'], rule['value']]
    if include_policy:
        parts.append(policy if policy is not None else rule['policy'])
    if rule.get('option'):
        parts.append(rule['option'])
    return ','.join(parts)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def yaml_quote(s):
    return json.dumps(s, ensure_ascii=False)


def safe_filename(policy):
    table = {
        'DIRECT': 'direct',
        'REJECT': 'reject',
        'REJECT-DROP': 'reject-drop',
        'REJECT-TINYGIF': 'reject-tinygif',
        'Proxy': 'proxy',
        'AIGC': 'aigc',
        'Apple': 'apple',
        'Telegram': 'telegram',
        'Netflix': 'netflix',
        'Disney+': 'disney-plus',
        'YouTube': 'youtube',
        'Spotify': 'spotify',
        'TikTok': 'tiktok',
        'BiliBili': 'bilibili',
        'GlobalMedia': 'global-media',
        'Microsoft': 'microsoft',
        'Google': 'google',
        'Game': 'game',
        '🇯🇵 日本节点': 'japan',
        '✈️ 主力机场': 'main-airport',
        '🚀 备用机场': 'backup-airport',
    }
    if policy in table:
        return table[policy]
    cleaned = ''.join(ch.lower() if ch.isalnum() else '-' for ch in policy).strip('-')
    return cleaned or 'policy'


def main():
    comments, raw_rules, surge_policy_map = load_source()
    rule_objs = []
    for i, item in enumerate(raw_rules, 1):
        rule = normalize_rule(item, i)
        if rule:
            rule_objs.append(rule)

    if not rule_objs:
        fail('no enabled rules found')

    clash_rules = [rule_line(r) for r in rule_objs]
    all_lines = comments + [''] + clash_rules + ['']
    list_text = '\n'.join(all_lines)
    write(ROOT / 'rules' / 'custom.list', list_text)
    write(ROOT / 'loon' / 'custom.list', list_text)
    write(ROOT / 'quanx' / 'custom.list', list_text)

    payload_lines = [
        '# 自定义规则 payload，供 Clash/Mihomo rule-providers 使用',
        '# 源数据：xiugai.yaml；修改后运行 python3 scripts/generate.py',
        '# 在 Clash/Mihomo 主配置中请使用 behavior: classical',
        'payload:',
    ]
    payload_lines += [f'  - {yaml_quote(rule)}' for rule in clash_rules]
    write(ROOT / 'clash' / 'custom.yaml', '\n'.join(payload_lines) + '\n')
    write(ROOT / 'mihomo' / 'custom.yaml', '\n'.join(payload_lines) + '\n')

    # Surge: map Clash/Mihomo policy names to this Surge profile's policy groups,
    # then split by final Surge policy so every remote RULE-SET has one correct target.
    surge_buckets = OrderedDict()
    for rule in rule_objs:
        surge_policy = surge_policy_map.get(rule['policy'], rule['policy'])
        if not surge_policy:
            fail(f'empty Surge policy after mapping for {rule_line(rule)}')
        surge_buckets.setdefault(surge_policy, []).append(rule)

    surge_all_lines = [
        '# Surge 汇总规则：源数据由 xiugai.yaml 维护',
        '# 已按 surge_policy_map 把 Clash/Mihomo 策略名映射为当前 Surge 策略组',
        '# 如果直接复制本文件到 [Rule]，每行末尾策略会生效；如果用远程 RULE-SET，建议使用 split/ 下的按策略拆分文件。',
        '',
    ]
    for policy, bucket in surge_buckets.items():
        surge_all_lines.append(f'# policy: {policy}')
        surge_all_lines.extend(rule_line(r, policy=policy) for r in bucket)
        surge_all_lines.append('')
    write(ROOT / 'surge' / 'custom.list', '\n'.join(surge_all_lines))

    split_dir = ROOT / 'surge' / 'split'
    split_dir.mkdir(parents=True, exist_ok=True)
    for old in split_dir.glob('*.list'):
        old.unlink()
    surge_rule_set_lines = []
    surge_inline_lines = []
    for policy, bucket in surge_buckets.items():
        remote_rules = [r for r in bucket if r['type'] in SURGE_REMOTE_RULE_TYPES]
        inline_rules = [r for r in bucket if r['type'] not in SURGE_REMOTE_RULE_TYPES]

        if remote_rules:
            filename = safe_filename(policy) + '.list'
            split_lines = [
                f'# Surge split rules for policy: {policy}',
                '# 源数据：xiugai.yaml；本文件只保留 Surge 外部 RULE-SET 兼容的匹配条件，不带策略列。',
                '',
            ]
            split_lines.extend(rule_line(r, include_policy=False) for r in remote_rules)
            split_lines.append('')
            write(split_dir / filename, '\n'.join(split_lines))
            surge_rule_set_lines.append(f'RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/{filename},{policy}')

        for r in inline_rules:
            surge_inline_lines.append(rule_line(r, policy=policy))

    write(ROOT / 'surge' / 'inline-rules.conf', '\n'.join([
        '# 这些规则类型不适合放进 Surge 外部 RULE-SET，需直接复制到 [Rule]。',
        '# 例如 DOMAIN-KEYWORD、DST-PORT、嵌套 RULE-SET 等。',
        *surge_inline_lines,
        '',
    ]))

    write(ROOT / 'surge' / 'rule-set-lines.conf', '\n'.join([
        '# 复制下面这些行到 Surge [Rule] 靠前位置。',
        '# 每个远程 RULE-SET 已按当前 Surge 策略组拆分，自适应匹配，不会引用不存在的 Clash 策略名。',
        '# 如果只想远程拉取，不想手写很多行，只复制下面这些 RULE-SET 即可。',
        '# 少数 Surge 不支持放进外部 RULE-SET 的类型会留在 surge/inline-rules.conf，可按需手动补充。',
        *surge_rule_set_lines,
        '',
    ]))

    sing_rules = []
    for rule in rule_objs:
        entry = {'type': rule['type'], 'value': rule['value'], 'outbound': rule['policy']}
        if rule.get('option'):
            entry['option'] = rule['option']
        sing_rules.append(entry)
    write(ROOT / 'sing-box' / 'custom-source.json', json.dumps({'version': 1, 'rules': sing_rules}, ensure_ascii=False, indent=2) + '\n')

    # README.md is maintained manually in Chinese. Do not overwrite it here.
    readme_path = ROOT / 'README.md'
    if not readme_path.exists():
        write(readme_path, f'# 订阅规则维护与部署说明\n\n当前启用规则数：{len(rule_objs)}。\n')

    print(f'generated {len(rule_objs)} rules from {SOURCE}')
    print('surge split policies:', ', '.join(surge_buckets.keys()))


if __name__ == '__main__':
    main()
