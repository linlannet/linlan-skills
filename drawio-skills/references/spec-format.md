# drawio DSL spec 格式说明

`build_diagram.py` 的输入格式。目标：**AI 只描述结构和语义，坐标由脚本确定性计算**。

## 最小示例

```json
{
  "title": "简单登录流程",
  "layout": "layered",
  "direction": "TB",
  "nodes": [
    {"id": "user", "label": "用户", "role": "external", "layer": 0},
    {"id": "gw",   "label": "API 网关", "role": "gateway", "layer": 1},
    {"id": "db",   "label": "用户库", "role": "database", "layer": 2}
  ],
  "edges": [
    {"from": "user", "to": "gw", "label": "登录请求"},
    {"from": "gw", "to": "db", "label": "查询"}
  ]
}
```

运行：

```bash
python scripts/build_diagram.py spec.json -o out.drawio
python scripts/validate.py out.drawio
```

## 顶层字段

| 字段 | 必填 | 取值 | 说明 |
|------|------|------|------|
| `title` | 否 | 字符串 | 图名，用于文件名与 diagram name |
| `layout` | 否 | `layered` / `grid` / `free` | 默认 `layered`（分层） |
| `direction` | 否 | `TB` / `LR` | 仅 layered 有效，默认 `TB` |
| `cols` | 否 | 整数 | 仅 grid 有效，默认 3 |
| `nodes` | **是** | 数组 | 节点列表，至少一个 |
| `groups` | 否 | 数组 | 语义分组 / 泳道 |
| `edges` | 否 | 数组 | 边列表 |

## node 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 否 | 稳定语义 ID（英文/数字）。**强烈建议显式给出**——后续增量修改靠它对齐。省略时从 label 生成 slug。不能是 `0` 或 `1`。 |
| `label` | 否 | 显示文字，支持中文 |
| `role` | 否 | 语义角色，决定配色和形状。见下表。默认 `service`。 |
| `layer` | 否 | 层号（整数，从 0 起）。layered 布局下同一 layer 的节点横向排列。 |
| `group` | 否 | 所属分组 id，对应 `groups[].id` |
| `shape` | 否 | 覆盖预设形状，如 `shape=cylinder3` |
| `w` / `h` | 否 | 覆盖默认尺寸（默认 140×60） |
| `dashed` | 否 | `true` 画虚线边框（外部系统常用） |
| `x` / `y` | 否 | 仅 `layout=free` 时生效 |
| `style_extra` | 否 | 追加到 style 字符串的裸键值，如 `fontStyle=1` |

### 可用 role（对应 linlan preset）

| role | 语义 | 填充 | 形状 |
|------|------|------|------|
| `service` | 服务 / 应用 | `#DAE8FC` 蓝 | 直角矩形 |
| `database` | 数据库 / 存储 | `#D5E8D4` 绿 | 圆柱 |
| `queue` | 队列 / 消息 | `#FFF2CC` 黄 | 直角矩形 |
| `gateway` | 网关 / 入口 | `#FFE6CC` 橙 | 直角矩形 |
| `error` | 错误 / 告警 | `#F8CECC` 红 | 直角矩形 |
| `external` | 外部系统 | `#F5F5F5` 灰 | 直角矩形 + 建议 `dashed:true` |
| `security` | 认证 / 安全 | `#E1D5E7` 紫 | 直角矩形 |

决策节点用 `shape: "rhombus"`；起止节点用 `shape: "ellipse"`。

## group 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 否 | 分组 ID，节点通过 `group` 引用 |
| `label` | 否 | 分组标题 |
| `layer` | 否 | 层号（仅作记录，实际位置由成员节点决定） |
| `color` | 否 | 分组描边色：`default` / `red` / `green` / `blue` / `darkred`，对应 linlan 分层签名色 |

分组画成 swimlane（泳道），成员节点的坐标会自动换算为相对父容器，**你不用自己算**。

## edge 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `from` / `to` | **是** | 节点 id，必须存在 |
| `label` | 否 | 连线标签，如 `HTTPS`、`订单事件` |
| `kind` | 否 | `sync`（默认，实线）/ `async`（虚线）/ `data` |
| `style_extra` | 否 | 追加 style |

边统一使用正交路由（orthogonalEdgeStyle）+ 实心箭头，由 preset 决定。

## 布局规则说明

- **layered + TB**（最常用）：layer 小的在上，同层节点水平居中对齐、均匀间隔（水平 60px，层间 80px）。分组自动包住成员。
- **layered + LR**：layer 小的在左，同层节点纵向排列。适合数据流、流水线。
- **grid**：按 `cols` 逐行排列，适合无明确流向的节点清单、矩阵。
- **free**：完全用节点的 `x`/`y`，仅在需要精确还原某张图时使用。

所有坐标吸附到 10px 网格，页面自动扩展（最小 A4 横向 1169×827）。

## 设计约束（为什么要这样）

1. **不让 AI 写坐标**：坐标算错是"图差"的首要原因。DSL 只表达"谁连谁、哪一层、什么角色"，坐标由脚本算，天然对齐、无重叠。
2. **稳定语义 ID**：`id` 由你显式给出，后续改图时脚本能按 ID 对齐，不丢失手工调整（这是增量同步的基础）。
3. **role 驱动样式**：颜色不是随手选的，而是语义映射。看图的人能靠颜色立刻分辨服务、数据、外部依赖。
