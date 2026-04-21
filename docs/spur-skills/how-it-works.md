# How It Works

`spur-skills` installs skills in two layers.

### 1. Shared skill files

First, it writes the full skill files into a shared directory:

```text
~/.spur-skills/skills/
```

This is the canonical copy of the installed skills.

### 2. Agent-specific pointers

Then it writes small `SKILL.md` pointer files into agent-specific skill folders,
for example:

```text
~/.codex/skills/
~/.claude/skills/
~/.hermes/skills/
~/.agents/skills/
~/.config/opencode/skills/
```

Those pointer files do not duplicate the full skill content. Instead, they tell
the agent to read the shared copy in `~/.spur-skills/skills/`.

