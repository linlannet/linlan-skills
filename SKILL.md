---
name: linlan-skills
description: 麟览技能包仓库总览。包含5个技能包：(1)eframe-skills - eframe框架快速开发 (2)excel-skills - Excel全栈处理 (3)drawio-skills - DrawIO图表生成 (4)pdf-skills - PDF知识提取 (5)assist-skills - AI开发助手接入。当用户询问技能包整体情况或需要跨技能协作时使用。具体技能请进入对应子目录读取其SKILL.md。
---

# Linlan Skills - 麟览技能包

> 仓库：https://gitee.com/linlannet/linlan-skills

## 技能包索引

本仓库包含 5 个独立技能包，每个有完整的 SKILL.md + 参考文档 + 可执行脚本。

| 技能包 | 路径 | 触发场景 |
|--------|------|----------|
| eframe 框架快速开发 | `eframe-skills/SKILL.md` | 在 eframe（SpringBoot + MyBatis + Vue3）上新增业务模块、CRUD、前后端代码 |
| Excel 全栈处理 | `excel-skills/SKILL.md` | xlsx 创建/读取/编辑、样式、pandas、PDF 转 Excel、飞书表格 |
| DrawIO 图表生成 | `drawio-skills/SKILL.md` | 架构图、流程图、ER 图、UML、拓扑图，个人风格 preset |
| PDF 知识提取 | `pdf-skills/SKILL.md` | PDF 文本提取、CJK 间距修复、知识规则提取、标准文档结构化 |
| AI 开发助手接入 | `assist-skills/SKILL.md` | 项目部署 AI 辅助开发流程、配置工具规则、14 模板 + 10 Workflow |

## 使用方式

Agent 收到匹配任务时，读取对应子目录的 SKILL.md 获取完整过程指南。不要在本文件中重复子技能的内容。

### 跨技能协作示例

- "从 PDF 提取数据写入 Excel"：先读 `pdf-skills/SKILL.md` 提取文本，再读 `excel-skills/SKILL.md` 写入 xlsx
- "画一个 eframe 架构图"：先读 `eframe-skills/SKILL.md` 理解架构，再读 `drawio-skills/SKILL.md` 生成图表
- "生成项目报告 Excel + PDF"：先读 `excel-skills/SKILL.md` 生成数据表，再按需转 PDF

## 附属资源

| 目录 | 内容 |
|------|------|
| `references/` | 代码审查参考文档（SOLID/安全/质量/部署检查清单） |
| `config/` | 项目配置 |
| `scripts/` | 辅助脚本 |

## 技能包规范

每个技能包遵循统一结构：

```
{skill-name}/
  SKILL.md          技能主过程（YAML frontmatter: name + description）
  README.md         快速上手
  scripts/          可执行脚本
  references/       详细参考文档
```

SKILL.md frontmatter 格式：

```yaml
---
name: skill-name
description: 一句话描述。功能：(1)xxx (2)xxx。当用户需要xxx时使用此技能。
---
```

`name` 必须与技能目录名完全一致（如 `eframe-skills/` 对应 `name: eframe-skills`），可读的中文名称写进 `description` 首句；ClawHub 包名即 `@linlan/<目录名>`。

description 要求：前 60 字符内包含触发关键词，之后展开功能列表和适用场景。
