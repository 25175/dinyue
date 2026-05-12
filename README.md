# dinyue 自定义代理规则

统一维护一份规则源，自动输出 Surge 与 Clash/Mihomo 可引用格式。

## 只改这一份

- `xiugai.yaml`：单一源文件，里面有详细注释和格式说明。

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

- `rules/custom.list`：通用 Clash/Mihomo/Loon/QuanX 风格规则行
- `surge/custom.list`：Surge 汇总规则，已映射为 Surge 策略组，可直接复制到 `[Rule]`
- `surge/split/*.list`：Surge 按策略拆分的远程规则集，推荐用这个接入 Surge
- `surge/rule-set-lines.conf`：可复制到 Surge `[Rule]` 的远程 `RULE-SET` 行
- `clash/custom.yaml`：Clash `rule-providers` payload
- `mihomo/custom.yaml`：Mihomo `rule-providers` payload
- `loon/custom.list`：Loon 规则列表
- `quanx/custom.list`：Quantumult X 规则列表
- `sing-box/custom-source.json`：结构化备份/转换源

## Raw 地址

```text
https://raw.githubusercontent.com/25175/dinyue/main/xiugai.yaml
https://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/rule-set-lines.conf
```

## Surge 接入：`/Users/ha/Downloads/Surge.surgeconfig`

推荐复制 `surge/rule-set-lines.conf` 里的规则到 `[Rule]` 靠前位置，例如：

```text
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/reject.list,REJECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/proxy.list,Proxy
```

脚本会自动用 `xiugai.yaml` 里的 `surge_policy_map` 做映射，当前默认：

```yaml
surge_policy_map:
  "🎯 全球直连": DIRECT
  "👋 手动选择": Proxy
  SF3: Proxy
```

也就是说 Clash/Mihomo 可以继续使用 `🎯 全球直连`、`👋 手动选择`、`SF3`，Surge 输出会自动变成当前配置里存在的 `DIRECT` / `Proxy`。

## Clash/Mihomo：`/Users/ha/Downloads/26-05-2.yaml`

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
