# ClubDesk — CLAUDE.md

## Project Overview
ClubDesk is a fully autonomous communication agent for **Oporto Toastmasters Club** (Porto, Portugal). It handles all incoming communications across email (Gmail), Facebook Messenger, and Instagram DMs — with zero ongoing human involvement after launch.

## Tech Stack
- **n8n** (self-hosted Docker) — workflow orchestration
- **Anthropic Claude API** — LLM for intelligent responses
- **Google Cloud APIs** — Gmail, Calendar, Sheets
- **Meta Developer App** — Facebook Messenger + Instagram DMs
- **Caddy** — reverse proxy with auto HTTPS
- **Docker Compose** — deployment

## Project Structure
```
ClubDesk/
├── CLAUDE.md                   # This file
├── PROJECT_PLAN.md             # 4-week phased build plan
├── knowledge-base/
│   └── club-knowledge.md       # Club FAQ, schedule, tone — THE critical asset
├── n8n-workflows/              # Exported n8n workflow JSON files
│   ├── email-responder.json
│   ├── messenger-responder.json
│   └── meta-webhook-verify.json
├── prompts/                    # Claude system prompts (version-controlled)
│   ├── email-system.md
│   └── chat-system.md
├── docker/
│   ├── docker-compose.yml
│   ├── Caddyfile
│   └── .env.example
├── scripts/
│   └── setup.sh                # VPS bootstrap script
└── tests/
    └── test-matrix.md          # 20 test scenarios
```

## Key Conventions
- **Language**: The club operates bilingually — Portuguese and English. The agent should reply in the language the person writes in.
- **Club name**: Always "Oporto Toastmasters Club" (never abbreviate to "OTC")
- **Placeholders**: Any `[bracketed text]` in prompts/knowledge-base means it needs real data filled in
- **System prompts** use structured output with `---REPLY---` and `---META---` markers for action routing
- **n8n workflows** are exported JSON — import directly into n8n UI

## Workflow
- `main` is the primary branch
- Keep knowledge base and prompts in sync — if club info changes, update both
- Test changes against `tests/test-matrix.md` scenarios before deploying
