# ClubDesk — Production Setup Checklist

Step-by-step guide to go from zero to a live production test where you
can contact Oporto Toastmasters as a member of the public and get a real
automated reply.

**Estimated time:** 2–3 hours (most of it is waiting for OAuth approvals)

---

## Before You Start — Prepare These

Do these in advance, not during the session:

- [ ] **Anthropic API key** — get one at console.anthropic.com if you don't already have one
- [ ] **Oracle Cloud account** — sign up free at cloud.oracle.com (use a personal email, one account per person)
- [ ] **A domain or subdomain** for n8n. Options:
  - Free: sign up at [DuckDNS](https://www.duckdns.org/) → create a subdomain like `oporto-clubdesk.duckdns.org`
  - Cheap: buy a `.me` or `.site` domain (~€1–3/year on Namecheap)
- [ ] **Build the production workflows** (run once now, re-run if prompts change):
  ```bash
  python3 scripts/build-workflows.py
  ```
  This creates `n8n-workflows/dist/email-responder.json` and `dist/messenger-responder.json` with the real prompts embedded.

---

## Step 1 — Provision Oracle Cloud VM

1. Log in to cloud.oracle.com → **Compute → Instances → Create Instance**
2. Settings:
   - **Name**: `clubdesk`
   - **Image**: Ubuntu 22.04 (Canonical)
   - **Shape**: `VM.Standard.A1.Flex` (ARM) — select **4 OCPUs / 24 GB RAM** (this is the free tier)
   - **Networking**: default VCN is fine; ensure **Assign public IP** is checked
3. Under **Add SSH keys**: paste your public SSH key (or download the generated one)
4. Click **Create** — VM will be ready in ~2 min
5. **Open ports in the firewall** (Oracle calls this Security List):
   - Go to VCN → Security Lists → Default Security List → Add Ingress Rules:
   - Port 80 (HTTP), Source: `0.0.0.0/0`
   - Port 443 (HTTPS), Source: `0.0.0.0/0`
   - Port 22 (SSH) is already open
6. Also run this on the VM after SSH in (Oracle's internal firewall):
   ```bash
   sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
   sudo netfilter-persistent save
   ```

---

## Step 2 — Point Your Domain to the VM

1. Copy the VM's **public IP address** from the Oracle console
2. In your DNS provider (DuckDNS, Namecheap, etc.):
   - Create an **A record** pointing your domain/subdomain to the VM IP
   - DuckDNS: paste the IP into the update field and click "Update IP"
3. Wait 1–5 min for DNS to propagate. Test: `ping yourdomain.com` — should resolve to the Oracle IP

---

## Step 3 — Deploy n8n on the VM

SSH into the VM:
```bash
ssh ubuntu@<your-vm-ip>
```

Clone the repo and run the bootstrap script:
```bash
git clone https://github.com/rianino/ClubDesk.git /opt/clubdesk
cd /opt/clubdesk
sudo bash scripts/setup.sh
```

Create and fill in the `.env` file:
```bash
cp docker/.env.example docker/.env
nano docker/.env
```

Fill in these values:
```
N8N_USER=admin
N8N_PASSWORD=<choose a strong password>
WEBHOOK_URL=https://<your-domain>/
TIMEZONE=Europe/Lisbon
ANTHROPIC_API_KEY=sk-ant-<your-key>
```

Update the Caddyfile with your domain:
```bash
nano docker/Caddyfile
# Replace n8n.yourdomain.com with your actual domain
```

Start the stack:
```bash
cd docker && docker compose up -d
```

Verify n8n is running:
```bash
docker compose ps   # both n8n and caddy should be "Up"
```

Open your browser: `https://<your-domain>` — you should see the n8n login screen.
Log in with the user/password from your `.env`.

---

## Step 4 — Google Cloud Setup (Gmail + Calendar)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. **Create a new project**: name it `ClubDesk`
3. **Enable APIs**:
   - Search "Gmail API" → Enable
   - Search "Google Calendar API" → Enable
   - Search "Google Sheets API" → Enable
4. **Create OAuth credentials**:
   - Go to APIs & Services → Credentials → Create Credentials → **OAuth client ID**
   - Application type: **Web application**
   - Name: `ClubDesk n8n`
   - Authorised redirect URIs: `https://<your-domain>/rest/oauth2-credential/callback`
   - Download the JSON — note the **Client ID** and **Client Secret**
5. **OAuth consent screen**:
   - User type: External
   - App name: ClubDesk
   - Add your own Gmail as a test user
   - Scopes: add Gmail (send + read), Calendar (read + write), Sheets (read + write)

---

## Step 5 — Meta Developer App (Messenger + Instagram)

1. Go to [developers.facebook.com](https://developers.facebook.com) → **My Apps → Create App**
2. App type: **Business**
3. Add products: **Messenger** and **Instagram Graph API**
4. **Messenger setup**:
   - Connect the Oporto Toastmasters Facebook Page
   - Generate a **Page Access Token** — save it
5. **Webhook setup**:
   - Callback URL: `https://<your-domain>/webhook/meta-messenger`
   - Verify token: choose any string (e.g. `clubdesk-verify-2026`) — you'll need this in n8n
   - Subscribe to: `messages`, `messaging_postbacks`
6. **Instagram setup**:
   - Connect the Oporto Instagram account
   - Subscribe to `messages` webhook (same callback URL)

> **Note:** The Meta webhook verification workflow must be active in n8n BEFORE you click "Verify" in the Meta dashboard. Do Step 6 first, then come back here to verify.

---

## Step 6 — Import Workflows into n8n

In the n8n UI (`https://<your-domain>`):

1. Go to **Workflows → Import from file**
2. Import these files (from your local machine):
   - `n8n-workflows/meta-webhook-verify.json` — import and **activate immediately**
   - `n8n-workflows/dist/email-responder.json`
   - `n8n-workflows/dist/messenger-responder.json`

> Import `meta-webhook-verify` first and activate it before going back to Step 5 Meta dashboard to click Verify.

---

## Step 7 — Configure Credentials in n8n

In n8n → **Settings → Credentials → Add Credential**:

| Credential name | Type | Values |
|-----------------|------|--------|
| `Anthropic API Key` | HTTP Header Auth | Header name: `x-api-key`, Value: your Anthropic key |
| `Gmail Account` | Gmail OAuth2 | Use Client ID + Secret from Step 4, authenticate with club Gmail |
| `Google Calendar Account` | Google Calendar OAuth2 | Same OAuth app, authenticate with club Gmail |
| `Google Sheets Account` | Google Sheets OAuth2 | Same OAuth app, authenticate with club Gmail |
| `Meta Page Access Token` | HTTP Query Auth | Query parameter: `access_token`, Value: token from Step 5 |

After adding each credential, go into the relevant workflow node and select the matching credential from the dropdown.

---

## Step 8 — Create the Google Sheet Log

1. Go to [sheets.google.com](https://sheets.google.com) → create a new sheet called **ClubDesk Log**
2. In the first row, add these column headers:
   - Email sheet: `Timestamp | From | Subject | Action | Reply Snippet`
   - Chat sheet (new tab): `timestamp | channel | sender_id | incoming_message | reply | action | event_name | escalate_reason`
3. Copy the Sheet ID from the URL: `docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`
4. In n8n, open each **Log Interaction** node and paste the Sheet ID

---

## Step 9 — Activate Workflows

In n8n, toggle **Active** on:
- [ ] `meta-webhook-verify`
- [ ] `Toastmasters Email Auto-Responder`
- [ ] `Messenger Responder (FB + IG)`

---

## Step 10 — Smoke Test (Before Real Test)

Before messaging as a real contact, do a quick sanity check:

**Email:**
1. From a personal email (not the club email), send to `oporto.toastmasters.club@gmail.com`:
   - Subject: `Test`
   - Body: `What time do you meet?`
2. Wait up to 2 minutes (Gmail trigger polls every 2 min)
3. Check: did you get a reply? Check n8n execution log for errors.

**Messenger:**
1. From your personal Facebook account, send a DM to the Oporto Toastmasters page: `hey is this toastmasters?`
2. Should reply within 10 seconds
3. Check n8n execution log

**Google Sheet:**
- Open ClubDesk Log — both interactions should appear as new rows

---

## Step 11 — Full Production Test

Now test as if you are a real person contacting the club for the first time:

| # | What to do | Channel |
|---|-----------|---------|
| 1 | Send email: `A que horas se reúnem?` | Gmail |
| 2 | Send email: `Hi, I'd like to visit next Monday. My name is [Name].` | Gmail |
| 3 | DM the Facebook page: `where do u meet` | Messenger |
| 4 | DM Instagram: `I'm scared of public speaking, is this for me?` | Instagram |
| 5 | Send email in French: `Combien ça coûte pour s'inscrire ?` | Gmail |

For each: check the reply you receive, check the n8n execution log, check the Google Sheet row.

**Pass criteria:**
- Reply received ✓
- Reply is in the correct language ✓
- Facts are correct ✓
- No mention of AI ✓
- RSVP link included when relevant ✓

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| n8n not loading | `docker compose ps` — is n8n Up? Check `docker compose logs n8n` |
| Caddy not serving HTTPS | DNS not propagated yet? Check `docker compose logs caddy` |
| Gmail trigger not firing | Check Gmail OAuth credential is valid; check n8n execution log |
| Meta webhook not verified | Is `meta-webhook-verify` workflow Active in n8n? |
| Claude not responding | Check Anthropic API key credential; check n8n execution log for HTTP errors |
| Wrong replies | Re-run `python3 scripts/build-workflows.py`, re-import the dist/ workflows |

---

## Cost Reminder

| Item | Cost |
|------|------|
| Oracle VM | €0 |
| Domain (DuckDNS) | €0 |
| Anthropic API (Haiku + caching) | ~€0.50–1/mo at Oporto volume |
| Everything else | €0 |
| **Total** | **~€1/mo** |
