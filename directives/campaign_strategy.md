---
name: campaign-strategy
description: >
  Generate 15-25+ cold outbound campaign ideas with targeting strategies,
  AI personalization approaches, and value propositions. Use when user says
  "plan campaigns", "what campaigns should I run", or after building a lead list.
scripts: []
---

# Campaign Strategy

## When to Use
- After ICP is defined and lead list is built
- User asks "what campaigns should I run?"
- Before writing any cold email copy
- Generates the strategy doc that `/campaign-copywriting` reads

## Core Philosophy

Every campaign operates on two levers:
1. **The List** — Target audience (broad to niche)
2. **The Message** — Value proposition angle

Broad lists need strong AI personalization. Niche lists can reference filtering criteria directly.

### Value Proposition Categories
All offers help people:
- **Make more money** (revenue growth, deal wins)
- **Save time** (automation, streamlining)
- **Save money** (cost reduction, consolidation)
- **Mitigate risk** (compliance, security, error prevention)

### Targeting Levels
- **Broad**: Widest audience; requires strong AI personalization
- **Focused**: One additional filter beyond broad parameters
- **Niche**: Multiple stacked filters creating highly relevant, smaller lists

## Input Requirements

Read from `config/profile.yaml` plus any of:
- Website URL (scrape for case studies, features, customers)
- Lead list data (who was found, from which platforms)
- User-provided constraints or preferences

## Deep Research Protocol

If the user provides a website URL, research it systematically:

1. **Homepage**: Core value prop, primary audience mentions
2. **Customers/Case Studies**: Extract EVERY customer. For each: company name, industry, size, metrics, problem solved
3. **Features/Product**: Capabilities, use cases, differentiators
4. **Pricing**: Target market signals, tiers, buyer personas
5. **About**: Company story, mission

### Customer Discovery Analysis
Analyze patterns from case studies:
- Frequently appearing industries
- Company size distribution
- Buyer titles/roles
- Common problems solved

**Challenge the user's ICP if research suggests a broader or different target.**

## Required Campaign Types (Always Include)

### 1. Creative Ideas Campaign
- AI Strategy: Analyze prospect website for 3 specific use cases
- Structure: "I had an idea for {{company_name}}..." + 3 bullet ideas
- Why: Shows research, provides value, demonstrates capability

### 2. New Hire Campaign
- List Filter: People started in target role within last 90 days
- Why: New leaders seek quick wins, are open to new tools
- AI: Pull start date, previous company, detect inherited problems

### 3. Lookalike Campaign
- List Filter: Companies similar to best case study customers
- Why: If it worked for similar companies, it should work for them
- Requires: Deep case study research
- AI: Reference similar company in outreach

## Creative Stretch Techniques

1. **Quantify the Pain**: Count team members, estimate time waste with math
2. **Detect Unusual Job Titles**: Some titles signal perfect fit
3. **Invert Signals**: Target companies WITHOUT a specific role (carefully — only for reliably detectable signals)
4. **Combine Multiple Signals**: Stack 3-4 filters for hyper-niche lists
5. **Role-Specific Workflows**: Day-in-the-life for target role
6. **Detect Team Structure**: Count people in specific roles via LinkedIn

## AI Strategy Principles

All personalization uses **publicly available data only**:
- Website content, LinkedIn profiles, job postings
- Technology stack, news, press releases
- Funding announcements, hiring patterns
- Podcast appearances, speaking engagements

**Never suggest scraping**: G2/Capterra reviews, private revenue, internal metrics.

### The Manual Research Test
> "If a sales rep had 10 minutes to research a company before reaching out, what would they look for and why?"

## Output Format

### Section 1: Campaign Ideas Table
Ordered from **broadest to most niche**:

| Campaign Name | Targeting Level | List Filters | AI Strategy | Value Proposition | Campaign Overview |

### Section 2: No-AI Campaigns
At least one campaign using zero AI personalization — short, snappy, strong value prop.

### Section 3: Front-End Offer Suggestions
1-3 softer offers converting cold traffic before the main pitch:
- Free audit / assessment
- Industry report / benchmark
- Template / toolkit
- Pilot program / limited trial

## Quality Checklist
- [ ] At least 15-20 campaign ideas
- [ ] Ordered broadest → most niche
- [ ] Creative Ideas, New Hire, Lookalike campaigns included
- [ ] 2-3 Creative Stretch campaigns
- [ ] All AI strategies use public data only
- [ ] At least one no-AI campaign
- [ ] Front-end offer suggestions included
- [ ] Value props tied to: make money, save time, save money, mitigate risk

## What to Do Next
Pick ONE campaign from the table and run the campaign copywriting workflow. Don't write copy for all 20 at once — pick one, test, learn, then advance.

Save output to `.tmp/campaign_strategy.md`.
