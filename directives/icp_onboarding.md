---
name: icp-onboarding
description: >
  Conversational ICP intake. Use when user hasn't filled out profile.yaml yet,
  or says "help me define my ICP", or when profile is empty/incomplete.
  Walks through structured questions to build a complete ICP.
scripts: []
---

# ICP Onboarding

## When to Use
- `config/profile.yaml` is empty or has blank fields
- User asks "who should I target?" or "help me define my ICP"
- Before a first-ever list build

## Conversational Flow

### Phase 1: Business Context
Ask these (adapt based on what you already know):

1. "What does your company do? Give me the 30-second pitch."
2. "Who are your best customers right now? Name 2-3 if you can."
3. "What problem do you solve for them?"
4. "What's your price point / deal size? (helps determine company size targeting)"

### Phase 2: Decision Maker Profile
1. "Who typically buys your product/service? (job title, seniority)"
2. "Who else is involved in the buying decision?"
3. "What department does the buyer sit in?"

### Phase 3: Company Filters
1. "What company size is your sweet spot? (employees or revenue)"
2. "Any industries that are especially good or bad fits?"
3. "What geographies do you sell in?"

### Phase 4: Qualification Signals
1. "What makes a company a GREAT fit vs. just okay?"
2. "Any disqualifiers? (too small, wrong industry, already has competing solution)"
3. "Any tech stack, funding status, or hiring signals that indicate readiness?"

### Phase 5: Platform Check
1. "Which lead sourcing platforms do you have API keys for?"
   - Prospeo, Apollo, Blitz, RapidAPI (Google Maps), Apify, MillionVerifier
2. Verify by checking `.env` for the relevant keys

## Output
After the conversation, update `config/profile.yaml` with the answers.
Confirm the profile back to the user before saving.

## Scraping the User's Website
If the user gives you their website URL, you can scrape it to pre-fill some fields:
- Company description and value proposition
- Industry context
- Case studies / social proof
This gives you a head start before asking questions.
