---
name: assist-skills
description: AI开发助手项目接入技能。功能：(1)在目标项目中部署AI开发助手参考资料包 (2)配置Trae/CodeBuddy/Claude Code/opencode四款工具规则 (3)生成需求/设计/测试/审查标准模板 (4)10个快捷指令Workflow覆盖全流程 (5)1WEEK/3DAY/1DAY三级任务复杂度分级。当用户需要在项目中接入AI辅助开发流程、配置AI工具规则、生成标准化模板时使用此技能。
---

# AI 开发助手项目接入技能

> 技能版本：v1.0
> 整理日期：2026-09-12
> 适配工具：Trae / CodeBuddy / Claude Code / opencode

## 定位

本技能解决"如何在项目中快速接入 AI 辅助开发流程"的问题。核心产出是一套标准化的参考资料包，包含项目级 AI 助手配置、需求/设计/测试/审查模板和快捷指令 Workflow，帮助团队在不改变既有研发流程的前提下降低 AI 开发助手的上下文准备成本。

## 1. 部署流程（3步）

### 1.1 复制参考资料包到目标项目

```powershell
Copy-Item -Path "assist-skills\*" -Destination "D:\your-project" -Recurse -Force
```

部署后目标项目新增以下目录和文件：

```
your-project/
  AGENTS.md                          项目级AI助手配置（opencode原生读取）
  CLAUDE.md                          Claude Code引用桥接
  VERSION.md                         版本与分发说明
  .trae/rules/poc-rule.md            Trae项目规则
  .codebuddy/rules/poc-rule.md       CodeBuddy项目规则
  ai-pilot/
    README.md                        使用说明
    standards/                       14个标准模板
    reference/
      workflows/                     10个快捷指令Workflow
      metrics-definition.md          度量口径定义
      quick-commands.md              快捷命令参考
```

### 1.2 初始化项目

在 AI 对话中输入"初始化项目"，AI 扫描项目并预填 `AGENTS.md` 第 1-4 节（项目概览、技术栈、目录结构、构建与测试命令）。

### 1.3 补充确认

人工补充业务背景、确认 AI 推断结果后，开始使用 AI 工具。

## 2. 标准模板体系（14个）

`ai-pilot/standards/` 目录下，按研发流程排列：

| 编号 | 模板 | 用途 |
|------|------|------|
| 00 | ai-usage-rule | AI 使用规范（总纲） |
| 01 | requirement-spec-template | 需求规格模板 |
| 02 | design-template | 设计文档模板 |
| 03 | api-design-template | API 设计模板 |
| 04 | db-design-template | 数据库设计模板 |
| 05 | test-case-template | 测试用例模板 |
| 06 | code-review-template | 代码审查模板 |
| 07 | release-note-template | 发版说明模板 |
| 08 | ai-usage-record-template | AI 使用记录模板 |
| 09 | poc-evaluation-template | POC 评估模板 |
| 10 | prompt-guide | Prompt 编写指南 |
| 11 | context-1week-template | 1周任务上下文模板 |
| 12 | context-3day-template | 3天任务上下文模板 |
| 13 | context-1day-template | 1天任务上下文模板 |
| 14 | test-execution-log-template | 测试执行日志模板 |

## 3. 快捷指令 Workflow（10个）

`ai-pilot/reference/workflows/` 目录下，覆盖从项目初始化到任务完成的全流程：

| 编号 | 指令 | 触发词 |
|------|------|--------|
| 00 | init-project | 初始化项目 |
| 01 | start-task | 开始任务 |
| 02 | prepare-requirement | 准备需求 |
| 03 | prepare-design | 准备设计 |
| 04 | prepare-test-cases | 准备测试用例 |
| 05 | start-coding | 开始编码 |
| 06 | run-tests | 运行测试 |
| 07 | code-review | 代码审查 |
| 08 | finish-task | 完成任务 |
| 09 | generate-summary | 生成总结 |

## 4. 任务复杂度分级

按任务周期选择对应的上下文模板，避免过度或不足的文档产出：

| 级别 | 周期 | 适用场景 | 模板 |
|------|------|----------|------|
| 1WEEK | 1周+ | 大型功能、架构改造、跨模块重构 | context-1week-template |
| 3DAY | 2-3天 | 中等功能、接口开发、组件封装 | context-3day-template |
| 1DAY | 1天内 | Bug修复、小功能、配置调整 | context-1day-template |

## 5. 工具适配

| AI 工具 | 规则入口 | 说明 |
|---------|----------|------|
| Trae | `.trae/rules/poc-rule.md` | 自动读取项目规则 |
| CodeBuddy | `.codebuddy/rules/poc-rule.md` | 自动读取项目规则 |
| Claude Code | `CLAUDE.md` | 引用桥接文件，指向 AGENTS.md |
| opencode | `AGENTS.md` | 原生读取项目级配置 |

## 6. 检查清单

- [ ] 参考资料包已复制到目标项目根目录
- [ ] AGENTS.md 第 1-4 节已预填并确认
- [ ] 业务背景已补充
- [ ] 对应 AI 工具的规则文件已就位
- [ ] 团队成员已了解快捷指令用法
- [ ] 度量口径（`metrics-definition.md`）已阅读

## 核心文件

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 项目级 AI 助手配置模板（12KB，含完整填写指引） |
| `ai-pilot/standards/` | 14 个标准模板（需求/设计/测试/审查/记录） |
| `ai-pilot/reference/workflows/` | 10 个快捷指令 Workflow |
| `ai-pilot/reference/metrics-definition.md` | AI 辅助研发度量口径定义（17KB） |
