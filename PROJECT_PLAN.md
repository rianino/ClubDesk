# ClubDesk — Toastmasters Autonomous Agent Project Plan

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

Build a fully autonomous agent that handles ALL incoming communications for a local Toastmasters club across email (Gmail), Facebook Messenger, Instagram DMs, and phone calls — with zero ongoing human involvement after launch.

## Architecture Overview

```
                        ┌─────────────────┐
                        │  Knowledge Base  │
                        │ (club-knowledge) │
                        └────────┬────────┘
                                 │ Context
┌──────────┐    ┌────────────────▼───────────────┐    ┌──────────────┐
│  Gmail    │───▶│                                │───▶│ Google Cal   │
│  Meta DMs │───▶│     n8n  (Central Brain)       │───▶│ (RSVP)       │
│  IG DMs   │───▶│                                │───▶│              │
│  Retell   │───▶│  Trigger → Classify → Claude   │    └──────────────┘
└──────────┘    │  → Act → Reply → Log            │    ┌──────────────┐
                │                                │───▶│ Google Sheet  │
                └────────────────────────────────┘    │ (Log)         │
                                                      └──────────────┘
```

## Tech Stack

| Service | Purpose | Cost |
|---------|---------|------|
| n8n self-hosted (Docker) | Orchestration brain | Free (Community Edition) + ~$6/mo VPS |
| Anthropic API (Claude) | LLM reasoning/replies | ~$5-15/mo at low volume |
| Retell AI | Voice agent for phone calls | Free tier / ~$0.10/min |
| Google Cloud (Gmail + Calendar APIs) | Email + RSVP | Free |
| Meta Developer App | FB Messenger + IG DMs | Free |
| Pinecone (optional) | Vector store for RAG | Free tier |
| UptimeRobot | Uptime monitoring | Free |

## Phased Build Plan

### Phase 0 — Foundation (Day 1–2, ~4 hrs)

- [ ] Deploy n8n on VPS via Docker with HTTPS (Cloudflare Tunnel or Caddy)
- [ ] Sign up for all services and collect API keys
- [ ] Write `knowledge-base/club-knowledge.md` with full FAQ, schedule, tone guidelines
- [ ] Create Google Cloud project, enable Gmail + Calendar APIs, create OAuth credentials
- [ ] Create Meta Developer App, add Messenger + Instagram products
- [ ] Initialize git repo, project structure

#### n8n Docker Deploy Command
```bash
docker run -d --restart unless-stopped \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=<strong-password> \
  -e WEBHOOK_URL=https://your-domain.com/ \
  n8nio/n8n
```

### Phase 1 — Week 1: Text Channels MVP (~8-10 hrs)

#### Day 1-2: Gmail Auto-Responder (3 hrs)
- [ ] Build n8n workflow: Gmail Trigger → Extract → RAG Lookup → Claude → Parse → Route → Reply/RSVP/Escalate → Log
- [ ] Configure Gmail OAuth in n8n
- [ ] Test with 10 sample emails covering all scenarios
- [ ] Tune Claude system prompt based on results

#### Day 3-4: Facebook Messenger (3 hrs)
- [ ] Set up Meta webhook verification workflow in n8n
- [ ] Build n8n workflow: Webhook → Extract → Claude → Reply via Meta API → Log
- [ ] Generate long-lived Page Access Token
- [ ] Test with sample messages

#### Day 4-5: Instagram DMs (2 hrs)
- [ ] Connect IG Professional account to Meta App
- [ ] Subscribe to IG messages webhook
- [ ] Extend or duplicate Messenger workflow for IG
- [ ] Test with sample DMs

#### Day 5: Unified Workflow Refactor (1 hr)
- [ ] Create `Core Brain` sub-workflow: normalize → Claude → parse → route
- [ ] Each channel workflow handles only intake + channel-specific reply delivery

### Phase 2 — Week 2: Voice Agent (~6-8 hrs)

#### Day 8-9: Retell AI Setup (3 hrs)
- [ ] Create Retell agent with warm voice, custom LLM pointing to n8n webhook
- [ ] Configure system prompt for natural phone conversation
- [ ] Enable function calling: `rsvp_guest`, `escalate`, `get_next_meeting`
- [ ] Build n8n webhook workflow for Retell tool calls

#### Day 10: Phone Number & Forwarding (1 hr)
- [ ] Buy Retell phone number or set up call forwarding from existing club number

#### Day 11: Post-Call Processing (2 hrs)
- [ ] Build n8n workflow: Retell post-call webhook → Claude summarize → Log → Follow-up email

#### Day 12: Voice Testing (2 hrs)
- [ ] Test 10+ call scenarios: basic inquiry, RSVP, rambling, wrong number, silence
- [ ] Tune interruption sensitivity (medium) and responsiveness (600-800ms)

### Phase 3 — Week 3: Hardening (~6 hrs)

#### Day 15-16: Knowledge Base Optimization (3 hrs)
- [ ] Decision: full-context (paste entire KB in system prompt) vs. RAG (Pinecone)
- [ ] Recommendation: Start with full-context if KB < 8,000 words, add RAG later if needed
- [ ] If RAG: chunk docs → embed → upsert to Pinecone → query at runtime

#### Day 17: Guardrails & Edge Cases (2 hrs)
- [ ] Add guardrails to Claude prompt: off-topic, abuse, scope limits, no PII sharing
- [ ] Add rate limiter in n8n: >5 msgs/hr from same sender → stop replying, log
- [ ] Add dedup: hash message body, skip if identical in last 24h

#### Day 18-19: End-to-End Testing (2 hrs)
- [ ] Run full test matrix (15 scenarios across all channels)
- [ ] Target: 14/15 pass (93%+) before launch

### Phase 4 — Week 4: Go Live (~3-4 hrs)

#### Day 22: Cutover Checklist
- [ ] Gmail polling active, personal notifications disabled
- [ ] Facebook webhook verified and receiving
- [ ] Instagram DM webhook active
- [ ] Phone forwarding to Retell active
- [ ] Google Calendar read/write working
- [ ] Google Sheet logging working
- [ ] All n8n workflows set to Active
- [ ] UptimeRobot pinging n8n instance
- [ ] Docker auto-restart configured

#### Day 23-25: Soft Launch (2 hrs)
- [ ] Go live on all channels
- [ ] Check Google Sheet log once daily for 3 days (15 min/day)
- [ ] Fix any issues found

#### Day 26-28: Full Hands-Off
- [ ] Stop checking
- [ ] Optional: weekly summary workflow (Cron Sunday 9am → read logs → Claude summarize → email)

## Key n8n Workflows

1. **`email-responder`** — Gmail Trigger → Extract → Claude → Reply/RSVP/Escalate → Log
2. **`meta-webhook-verify`** — GET webhook verification for Meta
3. **`messenger-responder`** — Webhook POST → Extract → Claude → Meta API Reply → Log
4. **`instagram-responder`** — Webhook POST → Extract → Claude → Meta API Reply → Log
5. **`core-brain`** — Sub-workflow: normalize → Claude → parse → route (shared by all channels)
6. **`retell-tool-handler`** — Webhook for Retell function calls → execute action → return result
7. **`retell-post-call`** — Post-call webhook → summarize → log → follow-up email
8. **`embed-knowledge`** — Manual trigger → chunk docs → embed → upsert to Pinecone
9. **`weekly-summary`** — Cron → read logs → Claude summarize → email to owner

## Claude System Prompt Guidelines

- **Structure**: Identity → Rules → Knowledge → Actions → Tone → Guardrails (priority order)
- **Temperature**: 0.3–0.4 for consistency
- **Max tokens**: 300 for chat, 500 for email
- **Tone**: Warm, encouraging, supportive, professional — classic Toastmasters spirit
- **Sign-off**: "[Club Name] Toastmasters" or "Your friends at [Club Name] Toastmasters"
- **Never**: Reveal AI nature, invent facts, share officer PII, engage with abuse
- **Action format**: Structured JSON block (`---META---`) for routing decisions

## Known Gotchas

| Issue | Fix |
|-------|-----|
| Meta webhook verification timeout | Dedicated lightweight GET workflow, respond within 3s |
| Gmail OAuth token expiry | Use Service Account or ensure n8n token refresh; check every 60 days |
| n8n crash / VPS restart | Docker `--restart unless-stopped` + UptimeRobot |
| Voice interruption issues | Retell `interruptionSensitivity`: medium, `responsiveness`: 600-800ms |
| Claude hallucinating meeting times | Put facts FIRST in system prompt; add "escalate if unsure" rule |
| Duplicate replies from webhook retries | Dedup by messageId in n8n static data |
| "Are you a bot?" questions | Prompt: deflect naturally, offer to connect with officers |
| Stale knowledge base | Single Google Doc as source of truth; manual-trigger re-embed workflow |

## Estimated Time

| Week | Hours | Focus |
|------|-------|-------|
| 1 | 8-10 | n8n deploy, Gmail + social DM workflows |
| 2 | 6-8 | Retell voice agent, phone forwarding |
| 3 | 5-6 | RAG, guardrails, full test suite |
| 4 | 3-4 | Cutover, brief monitoring, hands-off |
| 5+ | 0-0.5 | Optional weekly summary glance |
| **Total** | **~22-28** | |

## Project Structure

```
ClubDesk/
├── PROJECT_PLAN.md          # This file — full build plan
├── knowledge-base/
│   └── club-knowledge.md    # Club FAQ, schedule, tone guide (THE critical asset)
├── n8n-workflows/           # Exported n8n workflow JSON files
│   ├── email-responder.json
│   ├── meta-webhook-verify.json
│   ├── messenger-responder.json
│   ├── instagram-responder.json
│   ├── core-brain.json
│   ├── retell-tool-handler.json
│   ├── retell-post-call.json
│   ├── embed-knowledge.json
│   └── weekly-summary.json
├── prompts/                 # Claude system prompts (version-controlled)
│   ├── email-system.md
│   ├── chat-system.md
│   └── voice-system.md
├── docker/
│   └── docker-compose.yml   # n8n + reverse proxy deployment
├── scripts/
│   └── setup.sh             # VPS bootstrap script
└── tests/
    └── test-matrix.md       # Test scenarios and results tracking
```
