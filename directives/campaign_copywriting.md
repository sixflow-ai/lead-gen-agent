---
name: campaign-copywriting
description: >
  Write cold email copy for a specific campaign. Stepwise process: confirm direction,
  subject lines, body structure, then output final variants + YAML. Use after
  campaign-strategy has been run, or when user says "write the emails".
scripts:
  - execution/spam_word_checker.py
---

# Campaign Copywriting

## When to Use
- After campaign strategy is defined
- User says "write the emails", "draft copy", "create the sequence"
- Takes a single campaign idea and produces send-ready copy

## Core Process (4 Steps)

### Step 1: Confirm Campaign Direction
Before writing anything, confirm with the user:
- Target audience and pain points
- Value proposition angle
- Proof points / case studies to reference
- Available AI variables (if using personalization)
- Tone: direct, casual, authoritative?

### Step 2: Confirm Subject Line + First Line Strategy
Present 2-3 approaches:
- **Approach A (2-4 words)**: Intrigue via research — e.g., "question for {{first_name}}"
- **Approach B (Whole Offer)**: Self-selecting — put entire value prop in subject + preview
- **Approach C (Problem Indicator)**: Research-based signal — e.g., "Looked you up on ChatGPT"

Get user sign-off before proceeding.

### Step 3: Confirm Body Structure
Lock in:
- Value prop angle
- Case study / proof point
- AI variables (if applicable)
- CTA style (confirmation, value-exchange, or resource offer)
- PS line (optional)

### Step 4: Output Final Copy
Deliver all variants + follow-ups + `variants.yaml` for Smartlead upload.

## Hard Rules

- **No em dashes** — use periods or commas
- Company variable is always `{{company_name}}`
- Never use "Curious" as a subject line
- Personalized subjects use lowercase: "question for {{first_name}}"
- Every email must stand alone — no "following up on my last note"
- Preview text should contain the most compelling phrase
- Target 50-90 words; extend to 125 only when AI adds genuine value
- Maintain at least 3:1 recipient-to-sender sentence ratio
- CTA must be answerable in 5 words or fewer

## Email Structure Template

**Line 1:** Situation recognition (describe their exact scenario)
**Line 2:** Value prop + proof (what you do, backed by metric)
**Optional:** The "Specifically" line (for variable use cases with AI)
**Line 3:** Low-effort CTA (binary question or simple offer)
**Optional:** PS line (additional hook or AI specificity)

## Follow-Up Sequence

| Step | Timing | Strategy |
|------|--------|----------|
| Email 1 | Day 0 | Strongest signal, best case study |
| Email 2 | Day 3-4 | Threaded reply; rotate value prop; no weak openers |
| Email 3 | Day 7-8 | New thread; consider dropping AI; must stand completely alone |
| Email 4 | Day 11-12 | Redirect to another person, offer resources, or value bomb |

## CTA Patterns

- **Confirmation (earn reply):** "Is this still the case?" / "Worth exploring?"
- **Value-exchange (why meet):** "So I can understand the situation and..."
- **Resource offer (low commitment):** "Could I send you access?"

## AI Personalization Decision Tree

Use AI variables (mission, customer type, product type) **only when** your product's value changes based on what they do. If the use case is identical regardless of business type, skip AI and lean on situation recognition.

**Works:** "So you can focus on {{ai_company_mission}} instead of worrying about [category]."
**Doesn't work:** Generic product where context doesn't change the pitch.

## Output Format

1. Markdown email variants (3+ per step in the sequence)
2. `variants.yaml` file for Smartlead upload — body must match markdown exactly

## QA Checklist

- [ ] First line has specific signal (not generic)
- [ ] No hallucinations; all facts verifiable
- [ ] Variables formatted `{{correctly}}`
- [ ] No banned phrases (run spam word checker)
- [ ] Recipient:sender ratio >= 3:1
- [ ] Word count 50-90 (or justified to 125)
- [ ] CTA answerable in 5 words or fewer
- [ ] Reads naturally in under 20 seconds
- [ ] No em dashes
- [ ] Subject line is 2-4 words or whole offer

**Scoring:** 85+ = ship it. 70-84 = one more pass. <70 = restart.

## What to Do Next
1. Run spam word checker: `python execution/spam_word_checker.py --input .tmp/email_copy.md`
2. Add spintax for deliverability
3. Upload to Smartlead

Save output to `.tmp/campaign_copy.md` and `.tmp/variants.yaml`.
