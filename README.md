# ClubDesk

Fully autonomous communication agent for **Oporto Toastmasters Club** (Porto, Portugal). Handles all incoming communications across Gmail, Facebook Messenger, and Instagram DMs — with zero ongoing human involvement after launch.

## Architecture

```
                        ┌─────────────────┐
                        │  Knowledge Base  │
                        │ (club-knowledge) │
                        └────────┬────────┘
                                 │
┌──────────┐    ┌────────────────▼───────────────┐    ┌──────────────┐
│  Gmail    │───▶│                                │───▶│ Google Cal   │
│  Meta DMs │───▶│     n8n  (Central Brain)       │───▶│ (RSVP)       │
│  IG DMs   │───▶│                                │    └──────────────┘
└──────────┘    │  Trigger → Classify → Claude   │    ┌──────────────┐
                │  → Act → Reply → Log            │───▶│ Google Sheet  │
                └────────────────────────────────┘    │ (Log)         │
                                                      └──────────────┘
```

## Tech Stack

| Service | Purpose |
|---------|---------|
| [n8n](https://n8n.io) (self-hosted) | Workflow orchestration |
| [Anthropic Claude API](https://docs.anthropic.com) | LLM reasoning & replies |
| Google Cloud (Gmail + Calendar) | Email intake & RSVP management |
| Meta Developer App | Facebook Messenger + Instagram DMs |
| [Caddy](https://caddyserver.com) | Reverse proxy with auto HTTPS |
| Docker Compose | Deployment |

## Project Structure

```
ClubDesk/
├── knowledge-base/
│   └── club-knowledge.md       # Club FAQ, schedule, tone guide
├── n8n-workflows/              # Exported n8n workflow JSON files
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
    └── test-matrix.md          # Test scenarios
```

## Getting Started

### Prerequisites

- A Linux VPS (Ubuntu 22.04+ recommended)
- Docker and Docker Compose
- A domain name pointed at your VPS
- API credentials for: Anthropic, Google Cloud, Meta Developer

### Deployment

1. Clone the repo and navigate to the docker directory:

   ```bash
   git clone <repo-url> && cd ClubDesk/docker
   ```

2. Copy the environment template and fill in your values:

   ```bash
   cp .env.example .env
   ```

3. Start the services:

   ```bash
   docker compose up -d
   ```

4. Import the workflow JSON files from `n8n-workflows/` into the n8n UI.

5. Configure API credentials in n8n for Gmail, Meta, and Anthropic.

See `PROJECT_PLAN.md` for the full phased build plan.

## Key Workflows

| Workflow | Description |
|----------|-------------|
| `email-responder` | Gmail trigger → Claude → reply/RSVP/escalate → log |
| `messenger-responder` | Meta webhook → Claude → Messenger reply → log |
| `meta-webhook-verify` | GET verification endpoint for Meta webhooks |

## License

Private project — not for redistribution.
