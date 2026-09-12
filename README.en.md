# Linlan Skills

> Version: v2.0 | Updated: 2026-09-12
> Repository: https://gitee.com/linlannet/linlan-skills

## Overview

AI-assisted development skill packs extracted from real projects. Each skill includes a complete SKILL.md (procedure guide), reference documents, and executable scripts. Unlike generic AI prompts, these skills come from actual code analysis and lessons learned, ready to be consumed by AI Agents.

## Skill Packs

| Pack | Name | Use Case | Size |
|------|------|----------|------|
| [eframe-skills](./eframe-skills/) | eframe rapid development | Add business modules, generate CRUD, write frontend/backend code on eframe (SpringBoot + MyBatis + Vue3) | 27KB |
| [excel-skills](./excel-skills/) | Excel full-stack toolkit | xlsx create/read/edit, styling, pandas analysis, PDF-to-Excel, Feishu sheets | 17KB |
| [drawio-skills](./drawio-skills/) | DrawIO diagram generation | Architecture, flow, ER, UML sequence, network topology diagrams with personal style preset | 229KB |
| [pdf-skills](./pdf-skills/) | PDF knowledge extraction | PDF text extraction, CJK spacing fix, batch rule extraction, standard document structuring | 26KB |
| [assist-skills](./assist-skills/) | AI pilot setup | Deploy AI-assisted dev workflow in projects, configure Trae/CodeBuddy/Claude Code/opencode rules, 14 templates + 10 Workflows | 124KB |

> Skill name equals directory name: the `name` in `SKILL.md` frontmatter is the directory name, and the ClawHub package is `@linlan/<directory-name>`.

## Quick Start

### Option 1: Clone

```bash
git clone https://gitee.com/linlannet/linlan-skills.git
```

Copy the needed skill directory into your Agent workspace's skills folder.

### Option 2: Install via ClawHub (Recommended)

```bash
npm i -g clawhub
clawhub install @linlan/eframe-skills
clawhub install @linlan/excel-skills
clawhub install @linlan/drawio-skills
clawhub install @linlan/pdf-skills
clawhub install @linlan/assist-skills
```

### Option 3: Search and Install via OpenClaw

```bash
openclaw skills search "eframe"
openclaw skills install eframe-skills
```

## Skill Pack Structure

Each skill pack follows a unified structure:

```
{skill-name}/
  SKILL.md          Main procedure (triggers, steps, checklist)
  README.md         Quick start guide
  scripts/          Executable scripts (Python/Shell)
  references/       Detailed reference docs (code patterns, checklists)
```

SKILL.md uses YAML frontmatter for metadata:

```yaml
---
name: skill-name
description: One-line description. Features: (1)xxx (2)xxx. Use when user needs xxx.
---
```

`name` must match the skill directory name; put the readable name in the first sentence of `description`.

## Contributing

1. Fork this repository
2. Create skill packs on the develop branch
3. Follow the directory structure above
4. Submit a Pull Request

## License

MIT
