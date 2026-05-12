#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

RULES = [
    ('DOMAIN', 'cc0cd.cc.cd', 'DIRECT', ''),
    ('DOMAIN-SUFFIX', 'cc0cd.cc.cd', 'DIRECT', ''),
    ('DOMAIN-KEYWORD', 'mtyy', 'DIRECT', ''),
    ('DOMAIN-KEYWORD', 'mt', 'DIRECT', ''),
    ('DOMAIN-SUFFIX', 'm.kuku.lu', 'SF3', ''),
    ('DOMAIN-SUFFIX', 'kuku.lu', 'SF3', ''),
    ('DOMAIN-KEYWORD', 'kuku', 'SF3', ''),
    ('IP-CIDR', '23.27.240.115/32', 'DIRECT', ''),
    ('DST-PORT', '22', 'DIRECT', ''),
    ('RULE-SET', 'adblock', 'REJECT', ''),
    ('DOMAIN', 'www.gstatic.com', 'DIRECT', ''),
    ('DOMAIN', 'cp.cloudflare.com', 'DIRECT', ''),
    ('DOMAIN', 'accel.ipflygates.com', 'DIRECT', ''),
    ('IP-CIDR', '15.235.225.64/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '15.235.225.65/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '15.235.225.66/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '15.235.228.46/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '15.235.231.178/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '15.235.231.196/32', 'DIRECT', 'no-resolve'),
    ('IP-CIDR', '149.52.110.74/32', 'DIRECT', 'no-resolve'),
    ('DOMAIN', 'www.hostbuf.com', 'REJECT', ''),
    ('DOMAIN', 'backup.www.hostbuf.com', 'REJECT', ''),
    ('DOMAIN', 'www.youtusoft.com', 'REJECT', ''),
    ('DOMAIN', 'youtusoft.com', 'REJECT', ''),
    ('DOMAIN', 'hostbuf.com', 'REJECT', ''),
    ('DOMAIN', 'dkys.org', 'REJECT', ''),
    ('DOMAIN', 'tcpspeed.com', 'REJECT', ''),
    ('DOMAIN', 'www.wn1998.com', 'REJECT', ''),
    ('DOMAIN', 'wn1998.com', 'REJECT', ''),
    ('DOMAIN', 'pwlt.wn1998.com', 'REJECT', ''),
    ('DOMAIN', 'agentseller.temu', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'seller', '🎯 全球直连', ''),
    ('DOMAIN', 'agentseller.temu.com', '🎯 全球直连', ''),
    ('DOMAIN', 'seller.temu.com', '🎯 全球直连', ''),
    ('DOMAIN', 'netcut.cn', '👋 手动选择', ''),
    ('DOMAIN', 'wenshushu.cn', '👋 手动选择', ''),
    ('DOMAIN', 'wenshushu.com', '👋 手动选择', ''),
    ('DOMAIN', 'mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN', 'access.mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN', 'api-drive.mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN', 'config.mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN', 'static.mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN', 'user.mypikpak.com', '👋 手动选择', ''),
    ('DOMAIN-KEYWORD', '17qcc.com', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'v6.navy', '🎯 全球直连', ''),
    ('DOMAIN', 'v6.navy', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'dynv6', '🎯 全球直连', ''),
    ('DOMAIN', 'dynv6', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'navy', '🎯 全球直连', ''),
    ('DOMAIN', 'navy', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'keke1.app', '🎯 全球直连', 'no-resolve'),
    ('DOMAIN-KEYWORD', 'iPv6', '🎯 全球直连', 'no-resolve'),
    ('DOMAIN-SUFFIX', 'ls.apple.com', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '0.0.0.0/8', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '10.0.0.0/8', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '100.64.0.0/10', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '127.0.0.0/8', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '172.16.0.0/12', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '192.168.0.0/16', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '198.18.0.0/16', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR', '224.0.0.0/4', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR6', '::1/128', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR6', 'fc00::/7', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR6', 'fe80::/10', '🎯 全球直连', 'no-resolve'),
    ('IP-CIDR6', 'fd00::/8', '🎯 全球直连', 'no-resolve'),
    ('DOMAIN-KEYWORD', 'clipber', '🎯 全球直连', ''),
    ('DOMAIN', 'hd.lz-cdn18.com', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', '333ys.tv', '🎯 全球直连', ''),
    ('DOMAIN-KEYWORD', 'afreecatv.com', '👋 手动选择', ''),
]

COMMENTS = [
    '# 自定义代理规则：源数据由 scripts/generate.py 维护',
    '# 兼容 Clash/Mihomo 风格 rules，可按需拆分到 rule-providers',
    '# kuku.lu 同时保留 m.kuku.lu、kuku.lu 和 keyword 兜底规则',
]

def rule_line(rule):
    t, v, policy, opt = rule
    parts = [t, v, policy]
    if opt:
        parts.append(opt)
    return ','.join(parts)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def yaml_quote(s):
    return json.dumps(s, ensure_ascii=False)

def main():
    all_lines = COMMENTS + [''] + [rule_line(r) for r in RULES] + ['']
    write(ROOT / 'rules' / 'custom.list', '\n'.join(all_lines))
    write(ROOT / 'surge' / 'custom.list', '\n'.join(all_lines))
    write(ROOT / 'loon' / 'custom.list', '\n'.join(all_lines))
    write(ROOT / 'quanx' / 'custom.list', '\n'.join(all_lines))

    payload_lines = ['# 自定义规则 payload，供 Clash/Mihomo rule-providers 使用', 'payload:']
    payload_lines += [f'  - {yaml_quote(rule_line(r))}' for r in RULES]
    write(ROOT / 'clash' / 'custom.yaml', '\n'.join(payload_lines) + '\n')
    write(ROOT / 'mihomo' / 'custom.yaml', '\n'.join(payload_lines) + '\n')

    # sing-box source format: keep actions as outbound labels, suitable for manual import/conversion.
    sing_rules = []
    for t, v, policy, opt in RULES:
        entry = {'type': t, 'value': v, 'outbound': policy}
        if opt:
            entry['option'] = opt
        sing_rules.append(entry)
    write(ROOT / 'sing-box' / 'custom-source.json', json.dumps({'version': 1, 'rules': sing_rules}, ensure_ascii=False, indent=2) + '\n')

    readme = f'''# dinyue 自定义代理规则\n\n统一管理个人自定义代理规则，并输出多种客户端格式。\n\n## 文件\n\n- `rules/custom.list`：通用 Clash/Mihomo/Surge 风格规则行\n- `clash/custom.yaml`：Clash rule-providers payload\n- `mihomo/custom.yaml`：Mihomo rule-providers payload\n- `surge/custom.list`：Surge 规则列表\n- `loon/custom.list`：Loon 规则列表\n- `quanx/custom.list`：Quantumult X 规则列表\n- `sing-box/custom-source.json`：sing-box 转换源数据\n\n## Raw 地址\n\n```text\nhttps://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml\nhttps://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml\nhttps://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/loon/custom.list\nhttps://raw.githubusercontent.com/25175/dinyue/main/quanx/custom.list\n```\n\n## 维护\n\n规则源在 `scripts/generate.py`，修改后运行：\n\n```bash\npython3 scripts/generate.py\n```\n\n当前规则数：{len(RULES)}。\n'''
    write(ROOT / 'README.md', readme)

if __name__ == '__main__':
    main()
