# Dinyue Surge Family 生成目录

- `Surge-Family.conf`：基于 Rabbit-Spec 上游配置生成，已插入 Dinyue 自定义规则区块。
- `Rules/`：Rabbit 上游规则镜像 + Dinyue 自定义规则集 + 平台缝合规则集。
- `Rules/X.list` / `Reddit.list` / `Discord.list` / `Meta.list`：平台分流规则，由 scripts/sync_platform_rules.py 从 blackmatrix7 缝合，原始镜像在 `surge/上游/blackmatrix7/Rules/`。
- `Dinyue-inline-rules.conf`：少数需要手动内联的规则。
- 上游原始备份在 `surge/上游/Rabbit-Spec/`。
