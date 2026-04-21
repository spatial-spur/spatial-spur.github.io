# Get Started

`spur-skills` is distributed as a `uv` tool.


To get started, just point your agent at the install section:

```bash
codex --dangerously-bypass-approvals-and-sandbox "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install"
```

```bash
claude --dangerously-skip-permissions "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install"
```

## Install

If you haven't already, install `uv` with:

```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you run into issues setting up `uv`, you may want to check the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

Then, install `spur-skills` from PyPI with:

```bash
uv tool install spur-skills
spur-skills install
```

Update tool and skills:

```bash
spur-skills update
```

After install, you will see a short summary like this:

```text
╭─────── spur-skills installed ───────╮
│ Installed skills: spatial-analysis  │
│ In harnesses: claude, codex, hermes │
│ Reference: ~/.spur-skills/skills    │
╰─────────────────────────────────────╯
```

## Useful commands

Install skills into all supported agent folders that already exist:

```bash
spur-skills install
```

Install and auto-accept overwrites:

```bash
spur-skills install --yes
```

To fetch the latest version of the skill and tool:

```bash
spur-skills update
```

Update and auto-accept overwrites:

```bash
spur-skills update --yes
```

Remove installed skill entries from all supported agent folders and remove the
shared skill folder:

```bash
spur-skills uninstall
```

Remove installed skill entries only from selected agents:

```bash
spur-skills uninstall codex claude
```

Then uninstall the tool with 

```bash
uv tool uninstall spur-skills
```