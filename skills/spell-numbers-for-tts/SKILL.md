---
name: spell-numbers-for-tts
description: Rewrites numerals in a script as spoken words so text-to-speech reads them correctly. Use when preparing narration, voiceover, or any script for TTS, or when a draft contains digits like 47k, 91%, 4.8%, or 98,380 that a voice model would misread.
---

# Spell numbers for TTS

Text-to-speech models read written numerals badly ("47k" becomes "forty-seven kay").
Convert every numeral in a script to its spoken form before synthesis.

## Quick start

Run the converter on the script text:

```
python scripts/spell.py "47k stars, up 91% this week"
# -> forty-seven thousand stars, up ninety-one percent this week
```

It handles bare integers, decimals (`4.8` -> "four point eight"), percentages,
thousands separators (`98,380`), and `k`/`m`/`b` suffixes.

## When to apply

Run this as the last step before TTS, on the spoken lines only — not on code,
URLs, or anything shown on screen. See [references/edge-cases.md](references/edge-cases.md)
for cases the script does not handle (years, phone numbers, version strings).

## Caveat

Pure-Python, no dependencies — safe on sandboxed runtimes that cannot install packages.
