---
name: personalization-subagent
description: >
  Scale per-lead personalization using parallel sub-agents. Use when a campaign
  needs custom variables for each lead (situation_line, value_line, etc.).
  Approval loop: 1 lead → batch of 10 → scale.
scripts: []
---

# Personalization Sub-Agent Pattern

## When to Use
- Campaign copy uses AI variables that need per-lead customization
- User says "personalize for each lead" or "add custom first lines"
- After copywriting, before upload to Smartlead

## Core Pattern: Approval Loop

1. **Single lead sample** → user reviews → corrections
2. **Batch of 10** → user reviews → corrections
3. **Repeat** until 2 consecutive rounds with zero edits
4. **Scale** to remaining leads using tuned prompt

## Data Requirements

Each lead record needs:
- `lead_id`, `first_name`, `last_name`, `email`
- `company_name`, `company_domain`
- `company_description` (1-3 sentences — this drives quality)
- `title`
- Optional: `linkedin_url`, enrichment signals

**If company_description is missing, skip the lead** — don't fabricate.

## Output Schema (Max 3 Fields)

Recommended fields:
- `situation_line`: Observation about their business
- `value_line`: Connection between their context and your offer
- `cta_soft`: Soft call-to-action

Simpler = fewer failure points.

## A/B/C Variant Testing

Generate multiple variants per lead to test angles:
- **Variant A**: Pain observation angle
- **Variant B**: Compliment + transition angle
- **Variant C**: Question-based opening

3 variants × 10 leads = 30 data points per batch.

## Batch Sizing

- 10-20 leads per sub-agent batch
- For 100 leads: 10 batches of 10
- For 1000+: Process in rounds to manage context

## Sub-Agent Prompt Template

Each agent receives:
1. **Context**: What you sell, ICP, tone
2. **Field definitions** with good/bad examples
3. **Rules**: No em dashes, no buzzwords ("leverage", "synergy"), no hedging
4. **Lead batch** as JSON
5. **Output format**: JSON array matching schema

## Smartlead Variable Naming
- `{{situation_line_a}}`, `{{situation_line_b}}`, `{{situation_line_c}}`
- Each campaign variant maps to its corresponding personalization set

## Quality Checks

Before upload, spot-check 5 random leads per variant:
- No repetition across records (cookie-cutter detection)
- No factual inaccuracies
- No unnatural phrasing
- No hedging language ("it seems like", "I believe")

## Error Handling

- Missing `company_description` → skip lead, use static copy fallback
- Invalid JSON from sub-agent → retry once with stricter instructions
- Unpersonalizable lead → mark as "skipped", default to generic copy
