# Linlan Skills - 麟览技能包

> 版本：v2.0 | 更新日期：2026-09-12
> 仓库：https://gitee.com/linlannet/linlan-skills

## 定位

从实际项目中提炼的 AI 辅助开发技能包，每个技能包含完整的 SKILL.md（过程指南）、参考文档和可执行脚本。与通用 AI 提示词不同，这些技能来自真实项目的代码分析和踩坑经验，可直接被 AI Agent 消费。

## 技能包清单

| 技能包 | 名称 | 适用场景 | 大小 |
|--------|------|----------|------|
| [eframe-skills](./eframe-skills/) | eframe 框架快速开发 | 在 eframe（SpringBoot + MyBatis + Vue3）上新增业务模块、生成 CRUD、写前后端代码 | 27KB |
| [excel-skills](./excel-skills/) | Excel 全栈处理 | xlsx 创建/读取/编辑、样式格式化、pandas 数据分析、PDF 转 Excel、飞书表格 | 17KB |
| [drawio-skills](./drawio-skills/) | DrawIO 图表生成 | 架构图、流程图、ER 图、UML 时序图、网络拓扑图，支持个人风格 preset | 229KB |
| [pdf-skills](./pdf-skills/) | PDF 知识提取 | PDF 文本提取、CJK 间距修复、知识规则批量提取、行业标准文档结构化 | 26KB |
| [assist-skills](./assist-skills/) | AI 开发助手接入 | 项目中部署 AI 辅助开发流程、配置 Trae/CodeBuddy/Claude Code/opencode 规则、14 个标准模板 + 10 个 Workflow | 124KB |

> 技能名与目录名一致：`SKILL.md` frontmatter 的 `name` 即目录名，ClawHub 包名为 `@linlan/<目录名>`。

### eframe-skills -- eframe 框架快速开发

基于 [linlan-eframe](https://gitee.com/linlannet/linlan-eframe) 框架提炼，解决"如何在框架上快速新增一个业务模块并端到端跑通"的问题。

核心内容：
- **8 步端到端开发流程**：建表 -> model 层 -> view 层 -> api 层 -> 权限 -> 前端 api -> 前端 views -> 联调
- **三层代码范式**：model（entity/dto/param/dao/service）-> view（vo/voParam/manager）-> api（Controller）
- **读写分离约定**：Entry（读接口）/ Op（写接口）分离组织
- **module-generator 代码生成器**：从数据库表一键生成全链路代码
- 所有范式提取自框架数据字典模块真实代码，非通用 Spring Boot 建议

### excel-skills -- Excel 全栈处理

整合 6 个分散技能 + 踩坑经验，提供 `excel_toolkit.py` 统一工具集。

核心内容：
- 工作簿 CRUD、样式格式化（含 openpyxl 类型陷阱规避：每种样式独立构造、独立赋值）
- pandas 数据导入导出与清洗、多 Sheet 管理
- PDF 表格转 Excel、爬虫数据导出、飞书云端表格
- 42 个端到端测试全部通过

### drawio-skills -- DrawIO 图表生成

从个人绘制作品中提取风格 preset，按"linlan"风格（黑描边 #000000 + 浅色填充 + Tahoma + 直角矩形）生成专业图表。

核心内容：
- 架构图、流程图、ER 图、UML 时序图、网络拓扑、ML 模型图
- 从已有 .drawio 文件确定性提取个人绘制风格
- 导出 PNG / SVG / PDF

### pdf-skills -- PDF 知识提取

解决 PDF 文本提取中的常见问题（CJK 字符间距、编码乱码、表格结构丢失），支持行业标准文档结构化处理。

核心内容：
- PDF 文本提取为 Markdown，CJK 字符间距自动修复
- 知识规则批量提取（实体 -> 规则 -> 关联）
- 行业标准文档结构化处理

### assist-skills -- AI 开发助手接入

为项目快速接入 AI 辅助开发流程，适配 Trae、CodeBuddy、Claude Code 和 opencode 四款工具。

核心内容：
- 项目级 AGENTS.md 配置模板 + CLAUDE.md 桥接文件
- 14 个标准模板（需求/设计/API/数据库/测试/审查/发版/记录）
- 10 个快捷指令 Workflow（初始化项目 -> 开始任务 -> 准备需求/设计/测试 -> 编码 -> 测试 -> 审查 -> 完成 -> 总结）
- 1WEEK/3DAY/1DAY 三级任务复杂度分级
- 度量口径定义 + Prompt 编写指南

## 目录结构

```
linlan-skills/
  eframe-skills/          eframe 框架快速开发技能
  excel-skills/           Excel 全栈处理技能
  drawio-skills/          DrawIO 图表生成技能
  pdf-skills/             PDF 知识提取技能
  assist-skills/          AI 开发助手接入技能（适配 Trae/CodeBuddy/Claude Code/opencode）
  references/             代码审查参考文档（SOLID/安全/质量/部署检查清单）
  config/                 项目配置
  scripts/                辅助脚本
```

## 安装使用

### 方式一：直接克隆

```bash
git clone https://gitee.com/linlannet/linlan-skills.git
```

将需要的技能目录复制到你的 Agent 工作区 skills 目录下即可。

### 方式二：通过 ClawHub 安装（推荐）

```bash
npm i -g clawhub
clawhub install @linlan/eframe-skills
clawhub install @linlan/excel-skills
clawhub install @linlan/drawio-skills
clawhub install @linlan/pdf-skills
clawhub install @linlan/assist-skills
```

### 方式三：通过 OpenClaw 搜索安装

```bash
openclaw skills search "eframe"
openclaw skills install eframe-skills
```

## 技能包规范

每个技能包遵循统一结构：

```
{skill-name}/
  SKILL.md          技能主过程（触发条件、步骤、检查清单）
  README.md         快速上手说明
  scripts/          可执行脚本（Python/Shell）
  references/       详细参考文档（代码范式、检查清单）
```

SKILL.md 采用 YAML frontmatter 声明元数据：

```yaml
---
name: skill-name
description: 一句话描述。功能：(1)xxx (2)xxx。当用户需要xxx时使用此技能。
---
```

`name` 与技能目录名保持一致，可读名称写进 `description` 首句。

## 贡献

1. Fork 本仓库
2. 在 develop 分支创建技能包
3. 遵循上述目录规范
4. 提交 Pull Request

## 许可证

MIT
