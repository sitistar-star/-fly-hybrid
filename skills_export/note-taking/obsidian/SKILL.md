---
name: obsidian
description: "Read, search, create, and edit notes in the Obsidian vault. Also: install, log in, discover vaults, and configure CLI on Windows."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, notes, knowledge-management, windows]
---

# Obsidian Vault

Use this skill for Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

---

## Windows: Installation

### Latest version
```bash
curl -sL "https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest" | grep -i "browser_download_url.*exe\""
curl -L -o Obsidian.exe "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.12.7/Obsidian-1.12.7.exe"
./Obsidian.exe /S
```

Installed to: `C:\Users\<USER>\AppData\Local\Programs\Obsidian\Obsidian.exe`

### Launch
```bash
start "" "C:\Users\<USER>\AppData\Local\Programs\Obsidian\Obsidian.exe"
```

## Windows: Vault discovery

Vault registry at `%APPDATA%\obsidian\obsidian.json`:
```json
{"vaults":{"<UUID>":{"path":"C:\\Users\\<USER>\\OneDrive\\Документы\\Obsidian Vault","ts":...}}}
```

### Resolve vault path
```bash
# First check env var
echo $OBSIDIAN_VAULT_PATH
# Fallback: read the vault registry
cat "$APPDATA/obsidian/obsidian.json"
```

Common vault paths on Windows:
- `C:\Users\<USER>\OneDrive\Документы\Obsidian Vault` (OneDrive-synced)
- `C:\Users\<USER>\OneDrive\Desktop\<vault-name>`
- `C:\Users\<USER>\Documents\Obsidian Vault`

## Windows: Account login

Login page: `https://obsidian.md/account/` (click **Account** in navbar)

The form has:
- Email field + Password field + Sign in button
- "Forgot password?" link
- "Create an account" link

**Login fails with "Login failed, please double check your email and password"** means wrong Obsidian password. Obsidian credentials are SEPARATE from Google — the user must have created an Obsidian account previously with the same (or different) email.

**Forgot password flow:** Click "Forgot password?" → enter email → "Reset password" → email sent → user creates new password.

### SPA login automation via browser_console (when snapshot is empty)

Obsidian uses Gatsby/React SPA for its account pages. The `browser_snapshot` may appear empty while the form actually exists in the DOM. Use `browser_console` to verify and interact:

```javascript
// Check if form loaded
document.querySelector('h1')?.innerText  // "Sign in to your account"

// Find elements
document.getElementById('labeled-input-email')
document.getElementById('labeled-input-password')
document.querySelectorAll('button')[1]  // "Sign in" button

// Fill and submit
document.getElementById('labeled-input-email').value = 'user@example.com';
document.getElementById('labeled-input-password').value = 'password';
document.querySelectorAll('button')[1].click();

// Verify — h1 should become null if login succeeded
// body should show "Profile / Billing / Sync / Publish ..."
```

## Windows: CLI

Enable: **Settings → General → Advanced → Command line interface** (GUI only, cannot be enabled from terminal).

Once enabled:
```bash
"C:\Users\<USER>\AppData\Local\Programs\Obsidian\Obsidian.exe" --version
```

Without GUI enable, any CLI invocation prints:
```
Command line interface is not enabled. Please turn it on in Settings > General > Advanced.
```

## Gmail IMAP Account Recovery

When the user forgot their Obsidian password, you can retrieve the reset email via Gmail IMAP.

See `references/gmail-imap-recovery.md` for the full flow: get an App Password, fetch the reset email, extract the reset link, and log in via browser JavaScript.

## Windows: Config files

| File | Purpose |
|------|---------|
| `%APPDATA%\obsidian\obsidian.json` | Vault registry |
| `%APPDATA%\obsidian\<UUID>.json` | Per-vault metadata |
| `%APPDATA%\obsidian\Preferences` | Editor preferences |
| `%APPDATA%\obsidian\Local Storage\` | Electron session data |
| `%APPDATA%\obsidian\obsidian.log` | Application logs |

## Pitfalls

- **Obsidian window may not appear on launch** — `Start-Process Obsidian.exe` often produces child processes (CefSharp.BrowserSubprocess) with `MainWindowHandle = 0`. The main window PID and handle become available only after the vault renders, which can take 15-30 seconds on first launch. Retry `Get-Process | Where-Object MainWindowHandle -ne 0` in a loop.
- **Do NOT use `--config` flag** — Obsidian doesn't support config path override
- **CLI must be enabled in GUI first** — no workaround from terminal
- **Most operations require the GUI** — login, plugin install, settings changes
- **Vault paths may use OneDrive** — search both `OneDrive\\Documents\\Obsidian Vault` AND `Documents\\Obsidian Vault`
- **Vaults can be nested** — the vault registry (`obsidian.json`) may list a vault inside another vault's directory (e.g. `...Desktop\\гермес\\нермес`). Check for nested vault entries when the user says vault is "empty" after copying files.
- **Stale vault entries in obsidian.json** — deleted vaults may still appear until manually removed
- **Google blocks the Hermes headless browser** — if a Google login is needed (e.g., Gmail for reset email), tell the user to check their email manually; the headless browser can't pass Google's bot detection
- **SendKeys automation is unreliable** — Obsidian's Electron GUI doesn't respond reliably to `[System.Windows.Forms.SendKeys]` because the window may not have keyboard focus even after `SetForegroundWindow`. Prefer browser_console JS for the web account page, and user self-service for the desktop app.
