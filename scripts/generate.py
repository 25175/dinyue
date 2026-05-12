#!/usr/bin/env python3
"""Generate proxy rule files from rules/custom-source.yaml.

Only edit rules/custom-source.yaml for normal maintenance.
This script outputs Surge list + Clash/Mihomo YAML payload from the same source.
"""
from pathlib import Path
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'rules' / 'custom-source.yaml'

ALLOWED_TYPES = {
    'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'DOMAIN-SET',
    'IP-CIDR', 'IP-CIDR6', 'GEOIP', 'DST-PORT', 'SRC-IP-CIDR',
    'PROCESS-NAME', 'RULE-SET',
}


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
    if not isinstance(comments, list) or not all(isinstance(x, str) for x in comments):
        fail('comments must be a list of strings')
    if not isinstance(rules, list):
        fail('rules must be a list')
    return comments, rules


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
    parts = [rtype, value, policy]
    if option:
        parts.append(option)
    return ','.join(parts)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def yaml_quote(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    comments, raw_rules = load_source()
    rules = []
    for i, item in enumerate(raw_rules, 1):
        line = normalize_rule(item, i)
        if line:
            rules.append(line)

    if not rules:
        fail('no enabled rules found')

    all_lines = comments + [''] + rules + ['']
    list_text = '\n'.join(all_lines)
    write(ROOT / 'rules' / 'custom.list', list_text)
    write(ROOT / 'surge' / 'custom.list', list_text)
    write(ROOT / 'loon' / 'custom.list', list_text)
    write(ROOT / 'quanx' / 'custom.list', list_text)

    payload_lines = [
        '# 自定义规则 payload，供 Clash/Mihomo rule-providers 使用',
        '# 源数据：rules/custom-source.yaml；修改后运行 python3 scripts/generate.py',
        '# 在 Clash/Mihomo 主配置中请使用 behavior: classical',
        'payload:',
    ]
    payload_lines += [f'  - {yaml_quote(rule)}' for rule in rules]
    write(ROOT / 'clash' / 'custom.yaml', '\n'.join(payload_lines) + '\n')
    write(ROOT / 'mihomo' / 'custom.yaml', '\n'.join(payload_lines) + '\n')

    sing_rules = []
    for line in rules:
        parts = line.split(',')
        entry = {'type': parts[0], 'value': parts[1], 'outbound': parts[2]}
        if len(parts) > 3:
            entry['option'] = ','.join(parts[3:])
        sing_rules.append(entry)
    write(ROOT / 'sing-box' / 'custom-source.json', json.dumps({'version': 1, 'rules': sing_rules}, ensure_ascii=False, indent=2) + '\n')

    readme = f'''# dinyue 自定义代理规则\n\n统一维护一份规则源，自动输出 Surge 与 Clash/Mihomo 可引用格式。\n\n## 只改这一份\n\n- `rules/custom-source.yaml`：单一源文件，里面有详细注释和格式说明。\n\n修改后如果只想本地生成文件，运行：\n\n```bash\npython3 scripts/generate.py\n```\n\n如果要一键生成、验证、提交并推送到 GitHub，运行：\n\n```bash\npython3 scripts/update_github.py\n```\n\n也可以自定义提交说明：\n\n```bash\npython3 scripts/update_github.py -m "update custom rules"\n```\n\n## 自动生成文件\n\n- `rules/custom.list`：通用规则行\n- `surge/custom.list`：Surge `RULE-SET` 列表\n- `clash/custom.yaml`：Clash `rule-providers` payload\n- `mihomo/custom.yaml`：Mihomo `rule-providers` payload\n- `loon/custom.list`：Loon 规则列表\n- `quanx/custom.list`：Quantumult X 规则列表\n- `sing-box/custom-source.json`：结构化备份/转换源\n\n## Raw 地址\n\n```text\nhttps://raw.githubusercontent.com/25175/dinyue/main/rules/custom-source.yaml\nhttps://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml\nhttps://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml\nhttps://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/loon/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/quanx/custom.list\n```\n\n## 接入现有两份配置\n\n### Surge：`/Users/ha/Downloads/Surge.surgeconfig`\n\n在 `[Rule]` 靠前位置加入：\n\n```text\nRULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list,Proxy\n```\n\n说明：Surge 的远程 `RULE-SET` 最后一列是命中的统一策略；如果同一份列表里既有 DIRECT/REJECT/Proxy 等不同策略，请改为复制 `surge/custom.list` 里的规则行到 `[Rule]` 靠前位置，或者按策略拆分多个远程列表。\n\n### Clash/Mihomo：`/Users/ha/Downloads/26-05-2.yaml`\n\n在 `rule-providers:` 下加入：\n\n```yaml\n  dinyue-custom:\n    type: http\n    behavior: classical\n    format: yaml\n    url: "https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml"\n    path: ./ruleset/dinyue-custom.yaml\n    interval: 86400\n```\n\n在 `rules:` 靠前位置加入：\n\n```yaml\n  - RULE-SET,dinyue-custom,Proxy\n```\n\n注意：这里用 `behavior: classical`，因为规则源里包含 domain/ip/port/rule-set 等混合类型。\n\n当前启用规则数：{len(rules)}。\n'''
    write(ROOT / 'README.md', readme)

    print(f'generated {len(rules)} rules from {SOURCE}')


if __name__ == '__main__':
    main()
