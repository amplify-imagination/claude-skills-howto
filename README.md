# Build Your Own Claude Skill — and Audit Anyone Else's

Companion repo for the video. Three real, working skills you build up from scratch, plus a
field guide to writing skills that actually trigger — and checking that someone else's skill is safe
before you run it.

A **Skill** is just a folder with a `SKILL.md` (YAML frontmatter + Markdown instructions) and optional
bundled scripts. Claude loads it **on demand**, only when your task matches the skill's description.

> ⚠️ **Heads-up:** the document skills in this repo are demo/educational. Treat any third-party skill
> like installing software — read every script first (see [`safety/AUDITING.md`](safety/AUDITING.md)).

---

## The three skills (built in order)

| Skill | What it teaches | What it does |
|---|---|---|
| [`hello-world`](skills/hello-world) | A skill is *just instructions* that load on a match | Replies "hello world" when you say hi — no code |
| [`get-the-time`](skills/get-the-time) | Skills can **run code**; the code never enters context | Runs `scripts/now.py` and reports the current time |
| [`spell-numbers-for-tts`](skills/spell-numbers-for-tts) | The real pattern: a script + a tight description + a reference doc | Rewrites numerals as spoken words so TTS reads them right (`47k` → "forty-seven thousand") |

### Install (Claude Code)

Drop any of them into your skills folder — no build step, no upload:

```bash
cp -r skills/spell-numbers-for-tts ~/.claude/skills/   # personal, every project
# or  .claude/skills/   inside a repo for project-only scope
```

Then just ask Claude something that matches the description and watch it load (`Skill(...)` →
*Successfully loaded skill*). Editing an existing skill takes effect mid-session; a brand-new
top-level skills dir needs a Claude Code restart.

---

## How to build a skill that actually triggers

Each skill is a folder. Only `name` + `description` are required in the frontmatter:

```markdown
---
name: spell-numbers-for-tts
description: Rewrites numerals in a script as spoken words so text-to-speech reads them correctly.
  Use when preparing narration, voiceover, or any script for TTS, or when a draft contains digits
  like 47k, 91%, or 98,380 that a voice model would misread.
---

# Spell numbers for TTS
## Quick start
Run scripts/spell.py on the script text:
    python scripts/spell.py "47k stars, up 91%"
## When to apply
See references/edge-cases.md for the cases it doesn't handle.
```

**1. The description is the make-or-break field.** It's the only thing Claude sees before deciding to
load your skill. Write it in third person, say *what it does* **and** *when to use it*, with the real
trigger words. Vague descriptions fire about half the time; specific, slightly "pushy" ones fire almost
always. Keep it tight (~150 chars, triggers front-loaded) — long descriptions also eat your budget
(see below).

**2. Lean body, push exact work into a script.** Claude already knows a lot — only tell it what it
can't guess. Anything that must be deterministic goes in a script the body points to. `Run scripts/x.py`
= execute (the code never enters context, only its output does). `See references/y.md` = read on demand.
Keep references one level deep.

**3. `version:` is rejected by the validator.** Anthropic ships an optional validator with `skill-creator`
that checks your `SKILL.md` before you *share* a skill — you never need it just to make one. Its
allowed frontmatter fields are `name, description, license, allowed-tools, metadata, compatibility`.
`version:` is **not** one of them; leave it out if you'll ever package or upload.

**4. Skills don't sync across surfaces.** A Claude Code skill isn't on claude.ai or the API — upload to
each separately. On **claude.ai** you must turn on *"Code execution and file creation"* first, or skills
are silently inert.

---

## The #1 reason a skill silently won't fire: the listing budget

Claude Code 2.1.129 added a **skill-listing budget** (undocumented on Anthropic's site as of writing).
Only ~1% of the context window is spent listing skill descriptions; past that, the lowest-priority
skills get their descriptions **dropped entirely** — they still work if you invoke them directly, but
Claude won't auto-trigger them. A brand-new skill is low-priority by recency, so it's the first to go
dark. Run `/doctor` to see the casualties.

**Two settings** (verified against the 2.1.129 binary):

```jsonc
// ~/.claude/settings.json
{
  "skillListingBudgetFraction": 0.02,   // decimal 0–1 (NOT a percent). default 0.01 = 1% of context
  "skillListingMaxDescChars": 2048       // per-description cap before truncation. default 1536
}
```

**Three fixes, ranked:**
1. **`/skills` — disable what you don't use.** Free, the default recommendation. Most people have skills
   they tried once.
2. **Tighten descriptions** — front-load trigger keywords, ~150 chars. Free and sustainable; it both
   triggers better and costs less budget.
3. **Raise the budget** — `skillListingBudgetFraction`, or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var
   (a raw char count). Costs ~3k+ tokens **every session** — reserve it for 50+ genuinely useful skills
   or a 1M-context model.

> **Cowork note (undocumented):** the `settings.json` key is read by the Claude Code **CLI**, not the
> Cowork desktop harness. On Cowork, set the env var app-wide so the desktop process inherits it:
> `launchctl setenv SLASH_COMMAND_TOOL_CHAR_BUDGET 60000`, then fully quit and reopen Claude. Make it
> persist across reboots with a `~/Library/LaunchAgents/*.plist` that runs the same command at load.

---

## Is *this* third-party skill safe?

A skill runs code and calls tools **with your privileges** — treat it like installing software. The
December 2025 Cato CTRL research took Anthropic's own GIF Creator skill, added one helper function
(`post_save`), and showed it pull down and run MedusaLocker ransomware from a single approval — the
malicious code ran via bash without ever appearing in the transcript. At scale, one peer-reviewed study
of 98,380 skills found 157 confirmed malicious, the majority from a single actor using brand
impersonation.

Before you run someone else's skill: **read every script, grep for the tells, then cage it.** See
[`safety/AUDITING.md`](safety/AUDITING.md) for the checklist and the macOS sandbox profile
([`safety/deny.sb`](safety/deny.sb)).

---

## Sources

- Anthropic — [Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) ·
  [best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) ·
  [engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) ·
  [skills explained](https://claude.com/blog/skills-explained)
- [`anthropics/skills`](https://github.com/anthropics/skills) — official examples + `skill-creator` (validator, packager)
- Security: [Cato CTRL — Weaponizing Claude Skills with MedusaLocker](https://www.catonetworks.com/blog/cato-ctrl-weaponizing-claude-skills-with-medusalocker/) ·
  [Axios coverage](https://www.axios.com/2025/12/02/anthropic-claude-skills-medusalocker-ransomware) ·
  ["Malicious Agent Skills in the Wild" (arXiv)](https://arxiv.org/abs/2602.06547)
- [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) · [skill-listing budget writeup](https://claudefa.st/blog/guide/mechanics/skill-listing-budget)

## License

MIT — see [`LICENSE`](LICENSE). Provided for demonstration and educational purposes; test any skill in
your own environment before trusting it.
