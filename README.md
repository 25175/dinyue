# dinyue 自定义代理规则

统一管理个人自定义代理规则，并输出多种客户端格式。

## 文件

- `rules/custom.list`：通用 Clash/Mihomo/Surge 风格规则行
- `clash/custom.yaml`：Clash rule-providers payload
- `mihomo/custom.yaml`：Mihomo rule-providers payload
- `surge/custom.list`：Surge 规则列表
- `loon/custom.list`：Loon 规则列表
- `quanx/custom.list`：Quantumult X 规则列表
- `sing-box/custom-source.json`：sing-box 转换源数据

## Raw 地址

```text
https://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/loon/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/quanx/custom.list
```

## 维护

规则源在 `scripts/generate.py`，修改后运行：

```bash
python3 scripts/generate.py
```

当前规则数：69。
