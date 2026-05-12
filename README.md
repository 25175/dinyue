# dinyue 自定义代理规则

统一维护一份规则源，自动输出 Surge 与 Clash/Mihomo 可引用格式。

## 只改这一份

- `rules/custom-source.yaml`：单一源文件，里面有详细注释和格式说明。

修改后如果只想本地生成文件，运行：

```bash
python3 scripts/generate.py
```

如果要一键生成、验证、提交并推送到 GitHub，运行：

```bash
python3 scripts/update_github.py
```

也可以自定义提交说明：

```bash
python3 scripts/update_github.py -m "update custom rules"
```

## 自动生成文件

- `rules/custom.list`：通用规则行
- `surge/custom.list`：Surge `RULE-SET` 列表
- `clash/custom.yaml`：Clash `rule-providers` payload
- `mihomo/custom.yaml`：Mihomo `rule-providers` payload
- `loon/custom.list`：Loon 规则列表
- `quanx/custom.list`：Quantumult X 规则列表
- `sing-box/custom-source.json`：结构化备份/转换源

## Raw 地址

```text
https://raw.githubusercontent.com/25175/dinyue/main/rules/custom-source.yaml
https://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/loon/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/quanx/custom.list
```

## 接入现有两份配置

### Surge：`/Users/ha/Downloads/Surge.surgeconfig`

在 `[Rule]` 靠前位置加入：

```text
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list,Proxy
```

说明：Surge 的远程 `RULE-SET` 最后一列是命中的统一策略；如果同一份列表里既有 DIRECT/REJECT/Proxy 等不同策略，请改为复制 `surge/custom.list` 里的规则行到 `[Rule]` 靠前位置，或者按策略拆分多个远程列表。

### Clash/Mihomo：`/Users/ha/Downloads/26-05-2.yaml`

在 `rule-providers:` 下加入：

```yaml
  dinyue-custom:
    type: http
    behavior: classical
    format: yaml
    url: "https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml"
    path: ./ruleset/dinyue-custom.yaml
    interval: 86400
```

在 `rules:` 靠前位置加入：

```yaml
  - RULE-SET,dinyue-custom,Proxy
```

注意：这里用 `behavior: classical`，因为规则源里包含 domain/ip/port/rule-set 等混合类型。

当前启用规则数：69。
