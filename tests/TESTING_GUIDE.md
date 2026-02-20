# ClubDesk — Testing Guide

There are two testing phases. You can do Phase 1 today with no setup at all.

---

## Phase 1 — Prompt Testing (No infrastructure needed)

This tests the brain of the system: do the prompts + knowledge base produce correct, on-brand AI responses? This covers ~80% of what matters.

**What you need:** A browser. That's it.

---

### Step 1 — Build your test prompt

You'll create a combined system prompt by pasting two files together. Open both of these:
- `prompts/email-system.md` (for email tests)
- `knowledge-base/club-knowledge.md`

Combine them like this:

```
[paste the full contents of email-system.md]

---

## Knowledge Base

[paste the full contents of club-knowledge.md]
```

Do the same with `prompts/chat-system.md` for Messenger/Instagram tests.

---

### Step 2 — Open a Claude conversation

Go to [claude.ai](https://claude.ai) and start a new conversation.

You cannot set a system prompt directly in the UI, so instead **start your first message with the combined prompt**, then add a separator, then the test input. Like this:

```
[your combined system prompt + knowledge base]

---

Incoming message to respond to:
"What time do you meet?"
```

Send it. Claude will respond as if it were the agent.

---

### Step 3 — Evaluate the response

Check each response against this checklist:

**Content**
- [ ] Answer is factually correct (matches knowledge base — meeting time, location, price, etc.)
- [ ] No invented facts (hallucinated dates, prices, names)
- [ ] If the question is unanswerable, it escalates instead of guessing

**Format**
- [ ] Contains `---REPLY---` and `---META---` markers
- [ ] Action block is valid JSON: `{"action": "reply_only"}` / `{"action": "rsvp", ...}` / `{"action": "escalate", ...}`
- [ ] Reply length is within limits (email: max ~200 words / chat: max ~100 words)

**Tone**
- [ ] Warm and encouraging, not robotic or corporate
- [ ] Uses "we" and "our club" — not "the club" or "they"
- [ ] Signs off correctly ("Oporto Toastmasters" or "Your friends at Oporto Toastmasters")
- [ ] Does NOT say it is an AI, bot, or assistant

**Language**
- [ ] Replies in the same language as the incoming message
- [ ] Test both Portuguese and English inputs

---

### Step 4 — Run all test scenarios

Work through the test matrix in `tests/test-matrix.md`. Below are the exact inputs to copy-paste.

#### Email tests (use email-system prompt)

| # | Paste this as the incoming message |
|---|------------------------------------|
| 1 | `What time do you meet?` |
| 2 | `Hi, I'd like to visit next Monday. My name is Alex.` |
| 3 | `How much does it cost to join?` |
| 4 | `Hello, we offer professional SEO services that could help grow your club's online presence.` |
| 5 | `I have an issue with one of your members and I'd like to speak to someone about it.` |
| 6 | `(Pretend this is a reply to a previous message that said "We meet every Monday at 8:45pm") Thanks! Is it in person or online?` |

#### Chat tests (use chat-system prompt)

| # | Paste this as the incoming message |
|---|------------------------------------|
| 7 | `hey is this toastmasters?` |
| 8 | `where do u meet` |
| 9 | `Can I come this week?` |
| 10 | `Tell me about your club!` |
| 11 | `I'm scared of public speaking, is this for me?` |

#### Edge case tests (use either prompt)

| # | Channel | Paste this as the incoming message |
|---|---------|-------------------------------------|
| 16 | Email | `Cuantas veces se reunen?` |
| 18 | Email | `Is this the Downtown Speakers club?` |
| 19 | Email | `Please stop emailing me` |
| 20 | Chat | `👋🎤❓` |

#### RSVP link tests (critical — the link must appear)

| Input | What to check |
|-------|---------------|
| `I'd like to come visit next Monday` | Reply includes the RSVP link |
| `Como posso confirmar presença?` | Portuguese reply includes the RSVP link |
| `Can I just show up or do I need to register?` | Mentions both options (just show up OR use the RSVP link) |

#### Portuguese language tests (critical — run these)

| Input (Portuguese) | What to check |
|--------------------|---------------|
| `A que horas se reúnem?` | Replies entirely in Portuguese |
| `Quanto custa para entrar?` | Portuguese reply, correct prices |
| `Tenho muito medo de falar em público, este clube é para mim?` | Portuguese, warm/encouraging tone |
| `Quero visitar na próxima semana. Chamo-me Maria.` | Portuguese, RSVP action in META block |

---

### Step 5 — Record results

Open `tests/test-matrix.md` and mark each scenario as pass or fail. Add notes on anything that looked wrong.

**Common issues to watch for:**
- Agent invents a meeting date ("our next meeting is on February 24th") — **fail**, it should not guess specific future dates
- Reply is too long — **fail**
- No META block, or malformed JSON — **fail**
- Replies in English to a Portuguese message — **fail**
- Mentions being an AI — **fail**
- Shares a real officer's personal contact details — **fail** (it shouldn't know any, but check)

---

## Phase 2 — Integration Testing (Needs infrastructure)

Do this after n8n is running and all credentials are configured.

### Step 1 — Send a real test email

Send an email to `oporto.toastmasters.club@gmail.com` from a personal/throwaway account with the subject "Test inquiry" and body "What time do you meet?"

Watch the n8n execution log. Verify:
- [ ] Gmail trigger fired
- [ ] Claude API call was made with the correct system prompt
- [ ] Response parsed correctly (REPLY and META blocks extracted)
- [ ] Reply was sent back to your test email
- [ ] Row added to the Google Sheet log

### Step 2 — Send a real Facebook Messenger DM

Go to the club's Facebook page and send a DM: "Hey, where do you guys meet?"

Verify:
- [ ] Webhook received the message in n8n
- [ ] Claude responded
- [ ] Reply appeared in Messenger within 30 seconds

### Step 3 — Send a real Instagram DM

From a personal Instagram account, DM `@oporto.toastmasters`: "Tell me about your club!"

Same verification as Messenger.

### Step 4 — Trigger an RSVP flow

Email: "Hi, I'd like to come visit on Monday. My name is Test Person."

Verify:
- [ ] Agent replies with confirmation + details
- [ ] META block contains `{"action": "rsvp", "name": "Test Person", ...}`
- [ ] n8n creates a Google Calendar event for the next Monday
- [ ] Row logged in Google Sheet with action = rsvp

### Step 5 — Trigger an escalation

Email: "I have a complaint about a member."

Verify:
- [ ] Agent replies warmly ("let me connect you with our team")
- [ ] META block contains `{"action": "escalate", ...}`
- [ ] n8n forwards the original email to the club officer email (or logs it for manual review)

### Step 6 — Stress test: rapid messages

Using a Messenger test account, send 6 messages within one minute.

Verify:
- [ ] First 5 get replies
- [ ] 6th message is rate-limited (no reply sent, logged only)

---

## Pass Criteria

| Result | Decision |
|--------|----------|
| 18+ / 20 pass (90%+) | Ready to go live |
| 15-17 / 20 | Fix failing scenarios, retest before launch |
| Under 15 / 20 | Do not launch — review prompts and knowledge base |

---

## Quick Reference: What Each File Does

| File | What it controls |
|------|-----------------|
| `prompts/email-system.md` | How the agent thinks and replies to emails |
| `prompts/chat-system.md` | How the agent replies to Messenger/Instagram DMs |
| `prompts/voice-system.md` | How the phone agent handles calls |
| `knowledge-base/club-knowledge.md` | All facts the agent is allowed to use |
| `tests/test-matrix.md` | Track your pass/fail results here |
