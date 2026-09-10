# wool_scripts Surge 去广告模块（清洗版）

上游：[fmz200/wool_scripts Surge/module/blockAds.module](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Surge/module/blockAds.module)

本目录为独立镜像，不改动 `surge/generated` / Rabbit-Spec / 自用音乐会员解锁链路。

## Surge 模块订阅

```text
https://raw.githubusercontent.com/25175/dinyue/main/surge/wool_scripts/blockAds.sgmodule
```

## 清洗规则

- 删除所有含排除关键词的改写、Map Local、脚本与注释行
- MITM `hostname` 长行仅剔除冲突主机名，保留其余主机名
- 许可证：GPL-3.0-or-later; full text: LICENSES/fmz200-wool_scripts-GPL-3.0.txt

## 最近一次同步

- Upstream SHA256: `d75a30e3410fccc4269c2749cdc430f2c6ef5b092bca1bc342279642f9918423`
- Upstream lines: `9411`
- Omitted conflicting units: `11`

本地更新：

```bash
python3 scripts/sync_wool_surge_module.py
python3 scripts/sync_wool_surge_module.py --check
```
