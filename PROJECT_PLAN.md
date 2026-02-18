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

---

### Phase 5 — Productization & Distribution (Post-Launch)

The goal is to turn ClubDesk from a bespoke Oporto deployment into a product that any Toastmasters club (or similar speaking club) can buy and use with minimal setup.

> **Architecture note (do this before Phase 1):** All Oporto-specific data must live in `club-config.yml`, not hardcoded in workflows or prompts. This makes the entire codebase already parameterized when it's time to package — no refactor needed later.

#### Step 1: Config Abstraction (do before Phase 1 launch)
- [ ] Create `club-config.yml` — single source of truth for all club-specific values:
  - Club name, city, language(s)
  - Meeting day, time, location, format (hybrid/in-person/online)
  - Email address, social handles (Facebook, Instagram, LinkedIn)
  - Registration link, dues, IBAN, bank account name
  - Officer names + roles (for escalation routing)
  - Holiday/closure dates
- [ ] Update all n8n workflows to read values from `club-config.yml` (via n8n variables or environment injection)
- [ ] Update all prompts to use `{{clubName}}`, `{{meetingTime}}`, etc. — no hardcoded "Oporto" anywhere
- [ ] Update `docker-compose.yml` to mount `club-config.yml` as a volume

#### Step 2: Knowledge Base Template
- [ ] Create `knowledge-base/club-knowledge.template.md` — blank version of the knowledge base with clear instructions for each section
- [ ] Add a `setup/onboarding-questionnaire.md` — 20-question form club officers fill out; answers map directly to the template sections
- [ ] Document how to go from questionnaire → populated knowledge base (manual fill or scripted)

#### Step 3: Onboarding Automation
- [ ] Build `scripts/onboard.sh` — interactive CLI that:
  - Prompts for club info (name, email, schedule, social links, etc.)
  - Writes `club-config.yml` automatically
  - Generates a pre-filled `club-knowledge.md` from the template
  - Outputs a checklist of manual steps remaining (OAuth, Meta App, etc.)
- [ ] Build `scripts/validate-config.sh` — checks that all required fields are populated, no placeholder values remain

#### Step 4: Deployment Packaging
- [ ] One-command deploy: `./scripts/setup.sh` handles VPS bootstrap, Docker install, n8n launch, Caddy config
- [ ] Add `docker-compose.yml` health checks and auto-restart for all services
- [ ] Create a `SETUP_GUIDE.md` (non-technical) — step-by-step for club officers with no DevOps experience:
  - What services to sign up for and in what order
  - Screenshots / exact UI steps for Google Cloud, Meta App, n8n credential setup
  - Estimated time per step
- [ ] Create `docs/officer-guide.md` — how to update the knowledge base, handle escalations, read the log sheet

#### Step 5: Choose a Distribution Model

Three viable options (decide based on how much ops work you want):

| Model | Price | You host? | Effort per club | Best for |
|-------|-------|-----------|-----------------|----------|
| **SaaS** | €30-60/mo/club | Yes | Low (automated onboarding) | Scale |
| **Self-hosted license** | €200-500 one-time | No | Medium (support questions) | Tech-savvy clubs |
| **Done-for-you setup** | €300-800 one-time + €20/mo | No | High (manual per club) | Premium, early customers |

Recommendation: Start with **done-for-you** for the first 3-5 clubs (high-touch, gather feedback), then productize into SaaS once the onboarding is proven.

#### Step 6: Legal & Compliance
- [ ] Write `TERMS.md` and `PRIVACY.md` — essential since this handles club member data (GDPR applies, Portugal is EU)
- [ ] Decide on data residency: where is member data stored? (Google Sheets, n8n instance location)
- [ ] Draft a simple Data Processing Agreement (DPA) for clubs — required under GDPR for B2B
- [ ] Clarify IP ownership: the club's knowledge base content is theirs; ClubDesk workflows are yours

#### Step 7: Go-to-Market
- [ ] Identify target channels:
  - Toastmasters District newsletters and Facebook groups
  - Area and Division Director mailing lists (they have direct access to club officers)
  - Toastmasters International convention / regional events
- [ ] Build a 1-page landing page showing the problem → solution → pricing → "get started"
- [ ] Prepare a demo video showing a real conversation (Oporto data, anonymized)
- [ ] Offer first 2-3 clubs a discounted pilot in exchange for testimonials and feedback

#### Step 8: Multi-Club Operations (if SaaS)
- [ ] Decide: one shared n8n instance with tenant isolation, or one n8n instance per club
  - Recommendation: one Docker stack per club (simpler isolation, easier to debug, ~$6/mo per club VPS)
- [ ] Build `scripts/provision-club.sh` — spins up a new club's full stack from a single command
- [ ] Set up centralized uptime monitoring (UptimeRobot) across all club instances
- [ ] Create a private dashboard or Notion page for tracking all active clubs

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

| Phase | Week | Hours | Focus |
|-------|------|-------|-------|
| 0 | Pre-work | 4 | VPS, credentials, knowledge base |
| 1 | 1 | 8-10 | Gmail + social DM workflows |
| 2 | 2 | 6-8 | Retell voice agent, phone forwarding |
| 3 | 3 | 5-6 | RAG, guardrails, full test suite |
| 4 | 4 | 3-4 | Cutover, monitoring, hands-off |
| 5a | 5-6 | 6-8 | Config abstraction, templates, onboarding scripts |
| 5b | 7-8 | 8-12 | Packaging, docs, legal, landing page |
| 5c | 9+ | Ongoing | Selling, onboarding clubs, support |
| **Total** | | **~40-52** | |

## Project Structure

```
ClubDesk/
├── PROJECT_PLAN.md                        # This file — full build plan
├── club-config.yml                        # [Phase 5a] All club-specific values (one per deployment)
├── knowledge-base/
│   ├── club-knowledge.md                  # Populated knowledge base (Oporto instance)
│   └── club-knowledge.template.md         # [Phase 5a] Blank template for new clubs
├── n8n-workflows/                         # Exported n8n workflow JSON files
│   ├── email-responder.json
│   ├── meta-webhook-verify.json
│   ├── messenger-responder.json
│   ├── instagram-responder.json
│   ├── core-brain.json
│   ├── retell-tool-handler.json
│   ├── retell-post-call.json
│   ├── embed-knowledge.json
│   └── weekly-summary.json
├── prompts/                               # Claude system prompts — uses {{variables}}, no hardcoding
│   ├── email-system.md
│   ├── chat-system.md
│   └── voice-system.md
├── docker/
│   └── docker-compose.yml                 # n8n + Caddy deployment (parameterized)
├── scripts/
│   ├── setup.sh                           # VPS bootstrap script
│   ├── onboard.sh                         # [Phase 5a] Interactive new-club setup wizard
│   └── validate-config.sh                 # [Phase 5a] Checks config for missing/placeholder values
├── setup/
│   └── onboarding-questionnaire.md        # [Phase 5a] 20-question form for club officers
├── docs/
│   ├── SETUP_GUIDE.md                     # [Phase 5b] Non-technical setup guide with screenshots
│   └── officer-guide.md                   # [Phase 5b] How to update KB, handle escalations, read logs
├── legal/
│   ├── TERMS.md                           # [Phase 5b] Terms of service
│   ├── PRIVACY.md                         # [Phase 5b] Privacy policy
│   └── DPA.md                             # [Phase 5b] Data Processing Agreement (GDPR)
└── tests/
    └── test-matrix.md                     # Test scenarios and results tracking
```
