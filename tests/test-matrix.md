# ClubDesk — Test Matrix

Run through all scenarios before go-live. Target: 14/15 pass (93%+).

## Email Tests

| # | Scenario | Input | Expected Reply | Expected Action | Pass? | Notes |
|---|----------|-------|----------------|-----------------|-------|-------|
| 1 | Meeting time inquiry | "What time do you meet?" | Reply with day/time/location | reply_only | [ ] | |
| 2 | RSVP request | "I'd like to visit next Tuesday, my name is Alex" | Enthusiastic confirmation with details | rsvp (calendar add) | [ ] | |
| 3 | Cost question | "How much does it cost to join?" | Reply with dues breakdown | reply_only | [ ] | |
| 4 | Vendor spam | "We offer SEO services for your club..." | Polite deflection | reply_only | [ ] | |
| 5 | Complaint/escalation | "I have an issue with a member" | Warm escalation reply | escalate (forward to officers) | [ ] | |
| 6 | Thread reply | Reply to a previous auto-reply | Contextual follow-up in same thread | reply_only | [ ] | |

## Facebook Messenger Tests

| # | Scenario | Input | Expected Reply | Expected Action | Pass? | Notes |
|---|----------|-------|----------------|-----------------|-------|-------|
| 7 | Basic inquiry | "hey is this toastmasters?" | Short friendly yes + club info | reply_only | [ ] | |
| 8 | Location question | "where do u meet" | Location + time, casual tone | reply_only | [ ] | |
| 9 | Visit request | "Can I come this week?" | Yes + details + RSVP offer | reply_only or rsvp | [ ] | |

## Instagram DM Tests

| # | Scenario | Input | Expected Reply | Expected Action | Pass? | Notes |
|---|----------|-------|----------------|-----------------|-------|-------|
| 10 | General inquiry | "Tell me about your club!" | Brief club description | reply_only | [ ] | |
| 11 | Nervous first-timer | "I'm scared of public speaking, is this for me?" | Encouraging, relatable reply | reply_only | [ ] | |

## Phone Call Tests (Retell AI)

| # | Scenario | Caller Says | Expected Agent Behavior | Pass? | Notes |
|---|----------|-------------|------------------------|-------|-------|
| 12 | Basic inquiry | "When do you guys meet?" | Natural answer with time/location | [ ] | |
| 13 | Full RSVP flow | "I'd like to come visit" | Collect name + email, confirm, add to calendar | [ ] | |
| 14 | Silence / hangup | [silence for 10s] | "Are you still there?" then end gracefully | [ ] | |
| 15 | "Are you real?" | "Am I talking to a real person?" | Natural deflection, offer to connect with officer | [ ] | |

## Edge Case Tests

| # | Scenario | Channel | Input | Expected Behavior | Pass? | Notes |
|---|----------|---------|-------|-------------------|-------|-------|
| 16 | Non-English | Any | "Cuantas veces se reunen?" | Attempt reply or polite escalation | [ ] | |
| 17 | Rapid-fire spam | Messenger | 10 messages in 1 minute | Rate-limit after 5, log | [ ] | |
| 18 | Different club | Email | "Is this the Downtown Speakers club?" | Redirect to toastmasters.org/find | [ ] | |
| 19 | "Unsubscribe" | Email | "Please stop emailing me" | Acknowledge, log, stop | [ ] | |
| 20 | Emoji-only | Messenger | "👋🎤❓" | Friendly greeting + ask how to help | [ ] | |

## Results Summary

- **Date tested**: ___________
- **Total pass**: ___ / 20
- **Pass rate**: ___%
- **Blocking issues found**: ___________
- **Ready for launch**: [ ] Yes  [ ] No — fix items: ___________
