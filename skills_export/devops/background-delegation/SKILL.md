---
name: background-delegation
description: "Run tasks in the background while continuing the main conversation — spawn subagents, background Hermes instances, or cron jobs without blocking the user."
version: 1.0.0
author: Agent (derived from session)
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [delegation, background, parallel, multitasking, non-blocking]
    related_skills: [subagent-driven-development, hermes-agent]
---

# Background Delegation

## When to Use

Use this skill when the user wants to do something **while continuing to chat** — not wait for one task to finish before starting the next.

**Trigger signals from the user:**
- "делай отдельный чат пока ты работаешь" / "make a separate chat while you work"
- "где второй чат" / "where is the second chat"
- "пока ты занят" / "while you're busy"
- Asking to start something without blocking the conversation
- Expressing frustration about waiting for long tasks

**Do NOT use for:**
- Code implementation tasks that depend on each other (use `subagent-driven-development`)
- Quick single-tool calls (just call the tool directly)
- Tasks requiring user interaction mid-execution (subagents can't use `clarify`)

## Core Principle

**Never make the user wait.** If a task takes more than ~15 seconds and doesn't strictly require the user's attention, run it in the background and deliver the result when done.

## Three Patterns

### Pattern 1: Hermes Subagent (delegate_task)

Best for: reasoning-heavy tasks that need isolated context (research, analysis, comparison).

```python
delegate_task(
    goal="<what to accomplish>",
    context="<all context the subagent needs — file paths, URLs, constraints>",
    toolsets=['terminal', 'file', 'web']  # as needed
)
```

**Caveats:**
- Runs **synchronously** — the parent turn blocks until the child returns a summary
- If the parent is interrupted (user sends new message), the child is **cancelled**
- Use `session_search` afterward to recover child work if needed
- Subagents cannot use: `clarify`, `memory`, `send_message`, `execute_code`

### Pattern 2: Background Hermes Process (terminal + notify_on_complete)

Best for: truly independent long-running tasks that MUST NOT be interrupted.

```bash
# Fire-and-forget. User gets notified on completion.
terminal(
    command="hermes chat -Q -s <skills> -q '<task>'",
    background=True,
    notify_on_complete=True
)

# User continues chatting here while the agent works.
# When done, system delivers the result.
```

**Key learnings (Windows):**
- Use `-Q` flag to suppress banner/spinner output
- Use `-s <skill>` to load relevant skills for the task
- The background agent gets a **completely separate session** — no memory of the current conversation context
- Pass ALL context (URLs, file paths, requirements) explicitly in the `-q` query string
- The agent works independently; its output is delivered as a notification
- On Windows, always set `HERMES_HOME` and use the venv Python path:
  ```bash
  cd /c/Users/<user>/AppData/Local/hermes/hermes-agent && \
  HERMES_HOME="/c/Users/<user>/AppData/Local/hermes" \
  venv/Scripts/python.exe -m hermes_cli.main chat -Q -q "task"
  ```

### Pattern 3: Cron Job (cronjob tool)

Best for: recurring or scheduled tasks (daily digests, monitoring, cleanup).

```python
cronjob(action='create', schedule='every 2h', prompt='...', no_agent=True, script='...')
```

See `cronjob` tool documentation for full API.

## Expected Behavior

When the user asks for something while an agent is already working:

1. **First option**: "Я отправлю отдельного агента в фон, а мы пока можем поговорить здесь" / "I'll send a separate agent in the background, we can keep talking here"
2. Use Pattern 2 (background Hermes process) for maximum independence
3. Tell the user they'll get notified when the result is ready
4. Continue the main conversation immediately — don't wait

## Which Pattern When

| Scenario | Pattern | Why |
|----------|---------|-----|
| "Найди информацию о X" (research) | 1 (delegate_task) | Reasoning-heavy, needs context |
| "Зайди на сайт, опиши что там" (browse) | 2 (terminal bg) | Browser tools, can't be interrupted |
| "Проверяй сайт каждые 2 часа" (monitor) | 3 (cron) | Recurring |
| "Сделай ментальную карту" (generate) | 1 (delegate_task) | Quick, needs context |
| "Напиши код для фичи" (code) | 1 (delegate_task) + subagent-driven-dev | Multi-step, needs review |
| "Сделай отчёт и пришли" (report) | 2 (terminal bg) | Long task, can't block |
| "Ищи пока я пишу" (parallel) | 2 (terminal bg) | Truly parallel |

## User Expectations (DO NOT VIOLATE)

- **"перезагружайся когда остановка"** — spells out "restart on stall" as expected behavior. If a background agent is detected stuck (no `response ready` within 5 minutes), restart it. Do not wait to be asked.
- **"где второй чат"** — the user should NOT have to ask where the background task result is. Ensure delivery is set up properly (`notify_on_complete`, cron delivery target).
- The user wants to **continue chatting immediately** — the longest acceptable delay is ~5 seconds to set up the background task.

## Windows-Specific Notes

- `hermes` CLI may not be in PATH in git-bash — use the venv Python directly
- `uvx` / `npx` MCP commands may not work in git-bash without full PATH
- Always test `hermes chat -Q` in a terminal before relying on it in background
- PowerShell commands in git-bash need special quoting (see `gateway-ops` skill for quoting rules)
