# Auditing a third-party skill before you run it

A skill runs code and calls tools **with your privileges** — your files, your keys, your network are all
in reach. Treat installing a skill like installing software from a stranger. Two steps: **read it**, then
**cage it**.

## 1. Read every script — grep for the tells

Before a downloaded skill ever runs, scan every file for danger signals:

```bash
grep -rnE "urllib|requests|curl|wget|os\.system|subprocess|\.ssh|\.env|post_save|eval|exec|pickle" downloaded-skill/
```

What each tell means:

| Pattern | Why it's a red flag |
|---|---|
| `urllib` / `requests` / `curl` / `wget` | reaching out to the network — possible exfiltration or payload fetch |
| `os.system` / `subprocess` / `eval` / `exec` | running arbitrary shell / code |
| `.ssh` / `.env` / `id_rsa` / `credentials` | grabbing your secrets |
| `post_save` / hidden helper functions | code that runs *after* the visible task — the documented exploitation path (a helper runs via bash without entering the transcript, and only the top-level command is approval-gated) |
| bundled `.mcp.json`, `--dangerously-skip-permissions` | silently widening what the skill can do |
| obfuscated blobs, base64, `pickle` | hiding intent |

Other checks: prefer first-party (`anthropics/*`) or named partners; read the **full** `SKILL.md`;
confirm a real license; prefer small, single-purpose skills (easier to audit); re-audit after updates
(a clean skill can be poisoned later via dependency drift).

## 2. Cage it — let the OS hold the walls

On a Mac you have two options: a container cage, or the **macOS built-in** sandbox. The built-in one is
one command. The wall is a tiny profile that denies the network and denies reading your secrets:

```scheme
; deny.sb
(version 1)
(allow default)
(deny network*)
(deny file-read* (subpath "/absolute/path/to/your/secrets"))
```

Run the skill's script *inside* it — the operating system enforces the rules, the script can't opt out:

```bash
sandbox-exec -f deny.sb python3 suspicious_script.py
# network call  -> BLOCKED (URLError)
# read .env     -> BLOCKED (PermissionError)
```

Uncaged, a malicious helper reaches the network and reads your `.env`. Caged, the same script, same run,
both are blocked — nothing leaves the box. That's the wall that would have stopped the weaponized GIF
Creator skill cold.

> Claude Code also has `/sandbox`, built on the same macOS Seatbelt (and Linux bubblewrap) primitives.
> Don't run untrusted skills under `-p` non-interactive mode — trust verification is off there.

See [`deny.sb`](deny.sb) in this folder for the profile.
