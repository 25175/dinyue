# 订阅规则维护与部署说明

本仓库用于统一维护个人代理分流规则。日常只需要修改根目录下的 `xiugai.yaml`，GitHub Actions 会自动生成 Surge、Clash/Mihomo、Loon、QuanX 等客户端可使用的规则文件。

## 一、日常修改入口

只改这一份文件：

```text
xiugai.yaml
```

推荐规则写法：

```yaml
- {type: DOMAIN-SUFFIX, value: example.com, policy: DIRECT, comment: "example.com 及所有子域名直连"}
- {type: DOMAIN, value: api.example.com, policy: Proxy, comment: "精确域名走代理"}
```

说明：

- `type`：规则类型，例如 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`。
- `value`：匹配值，例如域名、域名后缀、关键词、IP 段。
- `policy`：目标策略，例如 `DIRECT`、`REJECT`、`Proxy`、`🎯 全球直连`、`👋 手动选择`。
- `comment`：备注说明，只给人看，不会写入最终规则。
- 推荐域名通配用 `DOMAIN-SUFFIX`，不要写 `*.example.com`。

## 二、自动部署方式

在 GitHub 网页直接修改 `xiugai.yaml` 并提交后，仓库会自动运行：

```text
.github/workflows/generate-rules.yml
```

自动流程：

1. 读取 `xiugai.yaml`
2. 生成各客户端规则文件
3. 校验 YAML / JSON / Surge 拆分规则
4. 自动提交生成结果到仓库

通常 10 秒到 2 分钟完成。完成后在 GitHub 的 Actions 页面会看到绿色成功状态。

## 三、本地手动部署

如果在本地修改，进入仓库目录：

```bash
cd /Users/ha/Downloads/dinyue
```

只生成文件，不提交：

```bash
python3 scripts/generate.py
```

生成、验证、提交并推送到 GitHub：

```bash
python3 scripts/update_github.py
```

自定义提交说明：

```bash
python3 scripts/update_github.py -m "更新自定义规则"
```

## 四、自动生成文件

- `rules/custom.list`：通用 Clash/Mihomo/Loon/QuanX 风格规则行
- `clash/custom.yaml`：Clash `rule-providers` payload
- `mihomo/custom.yaml`：Mihomo `rule-providers` payload
- `surge/custom.list`：Surge 汇总规则，已映射为 Surge 策略组
- `surge/split/direct.list`：Surge 直连远程规则集
- `surge/split/reject.list`：Surge 拒绝远程规则集
- `surge/split/proxy.list`：Surge 代理远程规则集
- `surge/rule-set-lines.conf`：可复制到 Surge `[Rule]` 的远程 `RULE-SET` 行
- `surge/inline-rules.conf`：少数不适合 Surge 外部规则集的内联规则，仅按需使用
- `loon/custom.list`：Loon 规则列表
- `quanx/custom.list`：Quantumult X 规则列表
- `sing-box/custom-source.json`：结构化备份/转换源

## 五、Raw 地址

```text
https://raw.githubusercontent.com/25175/dinyue/main/xiugai.yaml
https://raw.githubusercontent.com/25175/dinyue/main/rules/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/clash/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/mihomo/custom.yaml
https://raw.githubusercontent.com/25175/dinyue/main/surge/custom.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/rule-set-lines.conf
https://raw.githubusercontent.com/25175/dinyue/main/surge/split/direct.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/split/reject.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/split/proxy.list
```

## 六、Surge 接入方式

本地配置文件：

```text
/Users/ha/Downloads/Surge.surgeconfig
```

在 `[Rule]` 靠前位置加入以下三条即可，不需要把所有域名一条条写进 Surge：

```text
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/reject.list,REJECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/proxy.list,Proxy
```

Surge 不一定会在规则搜索里展开远程规则集里的具体域名。判断是否生效，主要看连接详情是否命中 `DIRECT` / `REJECT` / `Proxy`，以及对应规则集的使用计数是否增加。

## 七、Surge 策略映射

`xiugai.yaml` 可以继续使用 Clash/Mihomo 的策略名，脚本会自动映射到当前 Surge 策略组。

当前默认映射：

```yaml
surge_policy_map:
  "🎯 全球直连": DIRECT
  "👋 手动选择": Proxy
  SF3: Proxy
```

也就是说：

- `🎯 全球直连` 在 Clash/Mihomo 中保留原名，Surge 输出为 `DIRECT`
- `👋 手动选择` 在 Clash/Mihomo 中保留原名，Surge 输出为 `Proxy`
- `SF3` 在 Clash/Mihomo 中保留原名，Surge 输出为 `Proxy`

## 八、Clash / Mihomo 接入方式

本地配置文件：

```text
/Users/ha/Downloads/26-05-2.yaml
```

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

注意：这里必须用 `behavior: classical`，因为规则源里包含 domain、ip、port、rule-set 等混合类型。

## 九、常见问题

### 1. GitHub 网页改完多久生效？

通常等待 GitHub Actions 完成即可，大约 10 秒到 2 分钟。代理软件还需要手动更新外部资源，或者等待客户端自己的更新间隔。

### 2. Surge 搜索不到具体域名，是不是没生效？

不一定。Surge 规则页通常只显示远程 `RULE-SET` 这一行，不一定展开远程文件里的每个域名。以连接详情和规则集使用计数为准。

### 3. 为什么推荐 `DOMAIN-SUFFIX`？

`DOMAIN-SUFFIX,mtyy1.com` 已经覆盖：

- `mtyy1.com`
- `www.mtyy1.com`
- 任意子域名 `.mtyy1.com`

所以不需要写 `*.mtyy1.com`，也不需要穷举每个子域名。

### 4. Surge 外部规则集解析失败怎么办？

先确认 `surge/split/*.list` 里的规则类型是否为 Surge 外部规则集支持的类型。脚本会尽量把不适合外部规则集的类型放到 `surge/inline-rules.conf`，按需手动补充。

当前启用规则数：69。
