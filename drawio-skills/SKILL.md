---
name: drawio-skills
description: DrawIO图表技能。功能：(1)用结构化DSL生成专业架构图/分层图/拓扑图/ER图/流程图（确定性布局，不手写坐标）(2)5套架构模式骨架(C4/分层/数据链路/安全域/调用链) (3)结构lint+视觉自检保证图质量 (4)从.drawio确定性提取个人风格生成preset (5)参考图风格+结构分析。当用户需要画架构图、技术架构图、流程图、拓扑图、ER图、UML时使用此技能。
---

# DrawIO 图表技能

> 技能版本：v2.0（结构化生成升级）
> 依赖：Python 3.8+（脚本零第三方依赖）；导出图片可选 draw.io 桌面版 CLI
> 参考：https://github.com/Agents365-ai/drawio-skill（MIT License）

## 核心原则（v2.0 最重要的一条）

**不要让模型直接手写坐标。** 这是架构图难看的根本原因。

改成：AI 只写一份结构化 JSON spec（谁连谁、哪一层、什么语义角色），坐标由 `build_diagram.py` 确定性计算。这样布局天然对齐、无重叠、风格统一、可复现。

> 只有两种例外可以手写 XML：需要精确还原某张已有图；或需要官方 Mermaid 不支持的特殊形状/图标。

## 生成图的标准工作流（必须遵守）

```
选模式 → 写 spec → 生成 → lint → 视觉自检 → 导出
```

### 1. 选模式

读 `references/architecture-patterns.md`，根据用户需求选一套骨架：

| 用户说 | 模式 |
|--------|------|
| 技术架构图 / 系统架构 | 分层架构 |
| C4 / 容器图 / 给领导看的全景 | C4 Container |
| 数据链路 / 日志管道 / 实时计算 | 数据链路（LR） |
| 网络拓扑 / 等保 / 安全域 | 安全域 |
| 请求流程 / 调用链 | 调用链 |
| 标准流程图 / 思维导图 / 甘特图 | 不走本库，用官方 Mermaid 转换 |

### 2. 写 spec

读 `references/spec-format.md` 了解字段。要点：

- **每个节点给显式 `id`**（稳定语义 ID，后续改图靠它对齐）
- `role` 决定颜色和形状，不要随手换色
- `layer` 决定层级，`group` + `color` 画分层泳道
- 边只连相邻层，跨层边会穿模

示例：`examples/ecommerce-architecture.json`（电商微服务架构，可直接改）。

### 3. 生成

```bash
python scripts/build_diagram.py spec.json -o diagram.drawio
# 默认风格 linlan；换风格用 --style styles/xxx.json
# 默认输出未压缩（可读可 diff）；压缩格式加 --compress
```

### 4. 结构 lint（不可跳过）

```bash
python scripts/validate.py diagram.drawio
# ERROR 必须清零；WARN 是视觉问题的前兆，尽量修掉
# 需要报告：加 --json report.json
```

能抓到：重复 ID、悬空边、缺 geometry、同级节点重叠、字面 `\n`、父容器缺失、字号过小、小数坐标、内容越界、孤立节点、混用字体。

### 5. 视觉自检

读 `references/visual-check.md`。简版：

```bash
drawio -x -f png --width 2000 -o _draft.png diagram.drawio   # 注意：草稿不要 -e
```

读草稿图，按清单检查重叠 / 标签截断 / 穿模 / 边堆叠 / 颜色混乱。修 spec 后重新生成，**最多 2 轮**。无法看图时用 DOM 几何核验降级。

### 6. 导出

```bash
drawio -x -f png -e -s 2 -o diagram.drawio.png diagram.drawio   # 可编辑 PNG
drawio -x -f svg -e --embed-svg-images -o diagram.svg diagram.drawio
drawio -x -f pdf -e -o diagram.pdf diagram.drawio
```

导出后确认文件存在且非空（draw.io CLI 退出码不可信）。

## 风格预设（linlan）

从 15 张老板源图提取并人工复核的个人绘制风格，v2.0 生成器默认套用。

### 风格速查表

| 维度 | 特征 |
|------|------|
| **描边** | 黑色 `#000000` 主导（全量 814 次） |
| **填充** | 留白/透明为主；浅色 `#F5F5F5`、`#FFFAFA`、`#FFFFFF` |
| **分组描边色** | 红 `#EA6B66`、绿 `#00994D`、蓝 `#6666FF`、深红 `#660000` |
| **字体** | `Tahoma`（架构图）/ `Helvetica`（流程图） |
| **字号** | `12` 为主，`10` 次之，`14` 用于标题 |
| **圆角** | 直角矩形为主（圆角仅约 9%） |
| **页面** | 1169×827（A4 横向），grid=1，gridSize=10 |
| **笔宽** | 默认 1 |

### 角色 → 配色（role 语义映射）

| role | 语义 | 填充 | 描边 |
|------|------|------|------|
| `service` | 服务 | `#DAE8FC` | `#000000` |
| `database` | 数据库 | `#D5E8D4` | `#000000` |
| `queue` | 队列 | `#FFF2CC` | `#000000` |
| `gateway` | 网关 | `#FFE6CC` | `#000000` |
| `error` | 错误/告警 | `#F8CECC` | `#000000` |
| `external` | 外部 | `#F5F5F5` | `#000000` |
| `security` | 安全/认证 | `#E1D5E7` | `#000000` |

> preset schema 无法表达"透明填充"，故近似为"黑描边 + 浅色语义填充"。真正的"透明 + 分组彩描边"由 group 的 `color` 字段实现（见 spec 格式）。

## 脚本清单

| 脚本 | 用途 | v2.0 |
|------|------|------|
| `build_diagram.py` | **结构化 spec → .drawio（确定性布局）** | 新增 |
| `validate.py` | **结构 lint，ERROR/WARN 分级** | 新增 |
| `extract_style.py` | 从目录/单文件确定性提取风格 preset（含压缩格式解码） | 保留 |
| `analyze_style.py` | 逐文件风格统计（人工复核用） | 保留 |
| `ref_analyze.py` | 单张参考图分析（风格 + 结构双模板） | 保留 |

### 风格提取（保留能力）

```bash
python scripts/extract_style.py <源文件目录> --name my-style --out styles/my-style.json
python scripts/analyze_style.py <源文件目录>
```

算法：自动解码压缩 drawio → 统计 (fill,stroke) 对取 top7 → 形状类判定 → 角色推断（含中文词表）→ 字体字号众数 → 边样式众数。

> 确定性算法对"每角色固定 fill+stroke"有效，但 linlan 的"黑描边+留白"会让角色→色槽映射失真。故最终 preset 以人工复核为准，脚本用于快速得到底稿。

### 参考图分析（保留能力）

```bash
python scripts/ref_analyze.py <参考图.drawio> -o ref_report.md
```

产出报告含：配色/字体/形状、页面尺寸、分组泳道层级、节点类型分布、边方向、布局模式。默认套 `linlan.json` 风格（`--self` 才单图重提取）。

> 注意：参考图分析给出的是"长什么样"的描述，生成时仍建议走结构化 spec 路径，不要直接照着坐标手写。

## 两条路径怎么选

| 场景 | 路径 |
|------|------|
| 架构图 / 分层图 / 拓扑图 / 需要精细控制 | **结构化 spec → build_diagram.py**（本文主路径） |
| 标准流程图 / 思维导图 / ER / 时序 / 甘特 | 官方 Mermaid 转换（快、自动布局） |
| 参考某张图生成风格一致的新图 | ref_analyze.py 出报告 → 选模式 → 写 spec |
| 精确还原已有图的每个像素 | 手写 XML（唯一合理场景） |

Mermaid 路径示例：

```bash
# 写 xx.mmd 后用 draw.io CLI 转换
drawio -x -f xml -o diagram.drawio diagram.mmd
# 没有桌面版时可用官方脚本（需 Chrome + Node 18+）
node <官方skill>/scripts/mermaid-to-drawio.js diagram.mmd
```

## 目录结构

```
drawio-skills/
├── SKILL.md                       # 技能说明（本文件）
├── README.md                      # 用户文档
├── scripts/
│   ├── build_diagram.py           # 结构化 spec → drawio（确定性布局）  [v2.0]
│   ├── validate.py                # 结构 lint                          [v2.0]
│   ├── extract_style.py           # 风格提取（确定性）
│   ├── analyze_style.py           # 逐文件风格统计
│   └── ref_analyze.py             # 参考图分析（风格+结构）
├── references/
│   ├── spec-format.md             # DSL 字段说明                       [v2.0]
│   ├── architecture-patterns.md   # 5 套架构模式骨架                   [v2.0]
│   └── visual-check.md            # 视觉自检规范                       [v2.0]
├── examples/
│   ├── ecommerce-architecture.json  # 示例 spec
│   └── ecommerce-architecture.drawio# 示例产出
├── styles/
│   ├── schema.json                # preset 结构定义
│   └── linlan.json                # 个人风格预设
└── style_report.json              # 风格分析报告
```

## 已知限制

| 问题 | 原因 | 应对 |
|------|------|------|
| 角色→色槽映射在"黑描边+留白"下失真 | 预设假设每角色固定 fill+stroke | 人工复核 preset |
| "透明填充"无法进 preset | schema 要求 fillColor 为 #RRGGBB | 用 group color 表达分层彩描边 |
| 自定义 stencil 图标无法保留 | 非标准 shape 关键词 | 颜色/标签/边仍可捕获；图标需手工加 |
| 导出需 draw.io 桌面版 | 浏览器自动化不可靠 | 未装则只产出 .drawio |
| 严格时序图不适合 DSL | 缺生命线/消息编号语义 | 用 Mermaid sequenceDiagram |
| 视觉自检需视觉模型 | 纯文本模型看不了 PNG | 用 DOM 几何核验降级（见 visual-check.md） |
