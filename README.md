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
- `DOMAIN-SUFFIX,example.com` 是域名后缀/子域匹配，可命中 `example.com`、`www.example.com`、`a.b.example.com`；它不是关键词包含匹配。
- 如果只是想让 Surge 远程 `split/direct.list` 命中某个站点，优先写 `DOMAIN` 或 `DOMAIN-SUFFIX`；`DOMAIN-KEYWORD` 会保留到 `surge/inline-rules.conf`。

## 二、自动部署方式

在 GitHub 网页直接修改 `xiugai.yaml` 并提交后，仓库会自动运行：

```text
.github/workflows/generate-rules.yml
.github/workflows/sync-surge-family.yml
.github/workflows/sync-qx-adblock.yml
.github/workflows/sync-wool-surge-module.yml
```

自动流程：

1. 读取 `xiugai.yaml`
2. 生成各客户端规则文件
3. 同步 Rabbit-Spec Surge Family 上游配置和规则
4. 把 Dinyue 自定义规则插入到生成版 Surge Family 配置的上游规则前面
5. 同步清洗版 QX 广告规则与 wool_scripts Surge 去广告模块
6. 校验 YAML / JSON / Surge 拆分规则
7. 自动提交生成结果到仓库

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
- `surge/上游/Rabbit-Spec/`：Rabbit-Spec Surge Family 原始上游备份，包含原始配置和规则列表
- `surge/generated/Surge-Family.conf`：推荐给 Surge 使用的完整生成配置，已把 Dinyue 自定义规则放在 Rabbit 上游规则前面
- `surge/generated/Rules/`：生成版 Surge Family 使用的规则集，包含上游镜像和 Dinyue 自定义规则集
- `surge/generated/Dinyue-inline-rules.conf`：少数仍需手动内联的特殊规则
- `surge/wool_scripts/blockAds.sgmodule`：独立目录镜像的 fmz200/wool_scripts 去广告合集（已去除会干扰音乐会员解锁的内容），供 Surge 模块订阅
- `QuantumultX/`：清洗版 QX 广告规则镜像（NobyDa / blackmatrix7）
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
https://raw.githubusercontent.com/25175/dinyue/main/surge/generated/Rules/Apple-AI.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/split/proxy.list
https://raw.githubusercontent.com/25175/dinyue/main/surge/wool_scripts/blockAds.sgmodule
```

Surge 直接安装 wool_scripts 去广告合集（独立文件夹，清洗版，不影响自用音乐会员解锁）：

```text
https://raw.githubusercontent.com/25175/dinyue/main/surge/wool_scripts/blockAds.sgmodule
```

Apple Intelligence / Siri / Relay 规则由 `scripts/sync_surge_family.py` 从 RocM301/Apple-Rule 上游同步，生成 Surge 可直接引用的无策略规则集：

```text
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/generated/Rules/Apple-AI.list,Apple,extended-matching
```

同步工作流每 6 小时运行一次，也会在相关源文件推送后立即更新。`Apple` 是生成版 Surge Family 中已有的策略组；如使用自己的 Surge 配置，请把最后的 `Apple` 改成实际策略组名称。

## 六、规则类型兼容性说明

### Clash / Mihomo

`clash/custom.yaml` 与 `mihomo/custom.yaml` 供 `rule-providers` 使用，必须配置 `behavior: classical`。classical 支持混合规则类型，所以本仓库可以把 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`、`IP-CIDR6`、`DST-PORT`、`RULE-SET` 等放在同一个 payload 里。

### Surge

Surge 的普通 `[Rule]` 内联规则和远程外部 `RULE-SET` 不是同一套限制：

| 类型 | Clash/Mihomo classical | Surge 远程 split RULE-SET | Surge inline-rules.conf |
| --- | --- | --- | --- |
| `DOMAIN` | 支持 | 支持，进入 `surge/split/*.list` | 支持 |
| `DOMAIN-SUFFIX` | 支持 | 支持，进入 `surge/split/*.list` | 支持 |
| `DOMAIN-KEYWORD` | 支持 | 已实测支持，可进入 `surge/generated/Rules/Dinyue-*.list`；旧版 `surge/split` 仍按脚本设置生成 | 支持 |
| `IP-CIDR` / `IP-CIDR6` / `GEOIP` | 支持 | 支持，进入 `surge/split/*.list` | 支持 |
| `DST-PORT` | 支持 | 不放入远程 split | 支持，进入 `surge/inline-rules.conf` |
| `RULE-SET` | 支持 | 不嵌套放入远程 split | 支持，进入 `surge/inline-rules.conf` |
| `SRC-IP-CIDR` / `PROCESS-NAME` / 其他扩展类型 | classical 中按客户端支持情况处理 | 不放入远程 split | 如 Surge 当前版本支持，可手动内联 |

因此：关键词 `mtyy` 走 `DIRECT` 时，Clash/Mihomo 可由 `DOMAIN-KEYWORD,mtyy,DIRECT` 在 classical provider 中生效；Surge 生成版 `surge/generated/Surge-Family.conf` 会把它自动放进 `Dinyue-DIRECT.list` 这类远程规则集。

如果使用旧版 `surge/split/*.list` 接入方式，仍以 `scripts/generate.py` 的输出为准；如遇特殊规则未进入远程列表，请查看 `surge/inline-rules.conf`。

如果想让 Surge 远程规则更精确，推荐为真实的具体域名写 `DOMAIN` 或 `DOMAIN-SUFFIX`，例如：

```yaml
- {type: DOMAIN-SUFFIX, value: example.com, policy: DIRECT, comment: "example.com 及所有子域名直连"}
```

## 七、Surge 接入方式

### 推荐：使用生成版 Surge Family 完整配置

推荐直接使用本仓库生成的完整配置：

```text
https://raw.githubusercontent.com/25175/dinyue/main/surge/generated/Surge-Family.conf
```

这个文件基于 Rabbit-Spec 的 `Surge-Family.conf` 自动生成：

- `surge/上游/Rabbit-Spec/` 保存 Rabbit-Spec 原始上游备份。
- `surge/generated/Rules/` 保存最终规则集，所有 Rabbit 上游规则 URL 已改写到本仓库。
- `[Rule]` 里会先出现视觉分隔明显的 `Dinyue 自定义规则（优先匹配）` 区块。
- 后面再出现 `Rabbit-Spec 上游规则` 区块，方便定位哪些是自己加的、哪些来自上游。
- `xiugai.yaml` 中可进入远程规则集的自定义规则会自动生成到 `surge/generated/Rules/Dinyue-*.list`。
- 少数特殊规则会生成到 `surge/generated/Dinyue-inline-rules.conf`，如需完整生效请按需复制到 `[Rule]` 靠前。

注意：这是公共仓库，生成配置中不要写入真实机场订阅地址、token 或其它私密信息。上游模板里的 `policy-path=你的订阅地址` 应保持占位，真实订阅地址建议只在本地 Surge 配置中维护。

### 旧方式：只接入 Dinyue 自定义远程规则

本地配置文件：

```text
/Users/ha/Downloads/Surge.surgeconfig
```

在 `[Rule]` 靠前位置加入 `surge/rule-set-lines.conf` 里的远程规则集行即可，不需要把所有域名一条条写进 Surge。当前示例：

```text
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/direct.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/日本节点.list,日本节点
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/reject.list,REJECT
RULE-SET,https://raw.githubusercontent.com/25175/dinyue/main/surge/split/proxy.list,Proxy
```

如需让 `DOMAIN-KEYWORD`、`DST-PORT` 等 inline 规则也在 Surge 生效，再把 `surge/inline-rules.conf` 里的对应行复制到这些 `RULE-SET` 前面。

Surge 不一定会在规则搜索里展开远程规则集里的具体域名。判断是否生效，主要看连接详情是否命中 `DIRECT` / `REJECT` / `Proxy`，以及对应规则集的使用计数是否增加。

## 八、Surge 策略映射

`xiugai.yaml` 可以继续使用 Clash/Mihomo 的策略名，脚本会自动映射到当前 Surge 策略组。

当前默认映射：

```yaml
surge_policy_map:
  "🎯 全球直连": DIRECT
  "👋 手动选择": Proxy
  SF3: "🇯🇵 日本节点"
```

也就是说：

- `🎯 全球直连` 在 Clash/Mihomo 中保留原名，Surge 输出为 `DIRECT`
- `👋 手动选择` 在 Clash/Mihomo 中保留原名，Surge 输出为 `Proxy`
- `SF3` 在 Clash/Mihomo 中保留原名，Surge Family 输出为 `🇯🇵 日本节点`；必须和 `[Proxy Group]` 里的策略组名称完全一致，如果你的 Surge 策略组名称不同，请在 `xiugai.yaml` 改成实际策略组名

## 九、Clash / Mihomo 接入方式

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

## 十、常见问题

### 1. GitHub 网页改完多久生效？

通常等待 GitHub Actions 完成即可，大约 10 秒到 2 分钟。代理软件还需要手动更新外部资源，或者等待客户端自己的更新间隔。

### 2. Surge 搜索不到具体域名，是不是没生效？

不一定。Surge 规则页通常只显示远程 `RULE-SET` 这一行，不一定展开远程文件里的每个域名。以连接详情和规则集使用计数为准。

### 3. 为什么推荐 `DOMAIN-SUFFIX`？

`DOMAIN-SUFFIX,example.com` 已经覆盖：

- `example.com`
- `www.example.com`
- 任意子域名 `.example.com`

所以不需要写 `*.example.com`，也不需要穷举每个子域名。

### 4. Surge 外部规则集解析失败怎么办？

先确认 `surge/split/*.list` 里的规则类型是否为 Surge 外部规则集支持的类型。脚本会尽量把不适合外部规则集的类型放到 `surge/inline-rules.conf`，按需手动补充。

当前启用规则数：69。
