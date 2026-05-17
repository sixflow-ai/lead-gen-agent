---
name: spintax-generation
description: >
  Add Smartlead spintax variations to email copy for deliverability.
  Use after copywriting, before uploading to Smartlead. Reduces spam filter
  pattern detection by randomizing text.
scripts: []
---

# Spintax Generation

## When to Use
- After campaign copy is finalized
- Before uploading to Smartlead
- User says "add spintax" or "add variations"

## Syntax
Smartlead uses `{option1|option2|option3}` — platform randomly selects one per send.

## Golden Rule
> "Every possible combination that Smartlead could randomly assemble MUST read as a natural, grammatically correct, complete sentence."

Each spintax block must be **self-contained** so options are interchangeable independently. No broken combinations where adjacent blocks create bad grammar.

## What to Spin

**Always safe:**
- Greetings: `{Hey|Hi|Hello}`
- CTA phrasings: `{Worth exploring?|Open to a quick chat?|Make sense to connect?}`
- Transition words: `{Specifically|In particular|For example}`
- Unsubscribe lines: `{Not interested? Just let me know.|If this isn't relevant, no worries.}`
- Sign-offs: `{Best|Cheers|Talk soon}`

**Never touch:**
- Smartlead variables: `{{first_name}}`, `{{company_name}}`
- Signature placeholders
- Specific numbers, brand names, product names
- Case study details or metrics

## Process

1. Take finalized email copy
2. Identify safe spin targets
3. Add 2-3 variations per block
4. Walk through ALL adjacent block combinations mentally
5. Confirm "All combos clean"
6. Preserve original tone across all variations

## For HTML Input
Parse text content, add spintax, return complete HTML preserving all tags and structure.

## Verification
Before outputting, mentally expand 3-4 random combinations and read them aloud. If any sound unnatural, fix the block.
