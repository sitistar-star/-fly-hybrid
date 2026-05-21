# Google OAuth Credential Creation — UI Walkthrough

Created from a session (May 2026) where the user kept asking the agent to "open on PC" but
Google blocks the Hermes browser tool. This reference helps the agent guide the user step
by step through their own browser.

## Why the browser tool won't work

Google's sign-in detects the Hermes headless/automated browser and shows:
> "Не удалось войти в аккаунт. Возможно, этот браузер или приложение небезопасны."
> ("Couldn't sign in. This browser or app may not be secure.")

**Do NOT attempt Google login via browser tool** — it will always be blocked.
Always guide the user to open URLs in their own Chrome/Edge/Safari/Firefox (phone or PC).

## Quick-start message template

When the user asks you to "open in browser" for Google OAuth:

```
Google blocks my automated browser — it detects it as "not secure."
You need to open this link in YOUR browser (Chrome or Edge on your PC):

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find the OAuth 2.0 Client ID entry (named "Hermes" or similar)
3. Click ⋮ (three dots) → Download OAuth client → Download JSON
4. Send me the file path, e.g.:
   C:\Users\sitis\Downloads\client_secret_....json
```

## Full walkthrough (from scratch)

### Step 1: Create or select a project

URL: https://console.cloud.google.com/projectselector2/home/dashboard

| UI Element | Action |
|---|---|
| Top bar dropdown | Select existing project or click "NEW PROJECT" |
| Project name | Suggest something like "Hermes" or "Hermes Agent" |
| Wait for creation | May take 30-60 seconds. Refresh and select the project. |

### Step 2: Enable required APIs

URL: https://console.cloud.google.com/apis/library

Search and ENABLE each of these:
- Gmail API
- Google Calendar API
- Google Drive API
- Google Sheets API
- Google Docs API
- People API (optional, needed for contacts)

The button is in the top bar of each API's page — big blue "ENABLE" button.

### Step 3: Configure OAuth consent screen

URL: https://console.cloud.google.com/auth/consent

| Prompt | Choice |
|---|---|
| User Type | "External" (unless using Google Workspace) |
| App name | "Hermes" |
| User support email | User's own email |
| Developer contact | User's own email |
| Scopes | Add scopes matching the APIs enabled in Step 2 |
| Test users | Add the user's own Google email address |
| Publish status | "Testing" is fine — no need to publish |

If the user gets **Error 403: access_denied** during auth, send them directly to:
https://console.cloud.google.com/auth/audience
→ Add their email as a test user.

### Step 4: Create OAuth 2.0 Client ID

URL: https://console.cloud.google.com/apis/credentials

| UI Element | Action |
|---|---|
| "Create Credentials" button | Top of page, blue |
| "OAuth 2.0 Client ID" | Select this type |
| Application type | "Desktop app" |
| Name | "Hermes" |
| "CREATE" button | Blue, bottom of form |

After creation, a modal appears with the client ID and client secret.
→ Click "DOWNLOAD JSON" (the important part!)
→ The file saves to `C:\Users\<user>\Downloads\client_secret_....json`

### Step 5: Handle user input variations

| User sends | What to do |
|---|---|
| File path (e.g. `C:\Users\sitis\Downloads\client_secret_....json`) | Use the setup script with `--client-secret <path>` |
| Raw client ID (e.g. `524884129189-....apps.googleusercontent.com`) | They only copied the Client ID, not the JSON. Tell them: "I need the entire JSON file, not just the Client ID. Click DOWNLOAD JSON on the OAuth creation popup, or find your credential and click ⋮ → Download OAuth client → Download JSON." |
| API key (e.g. `AIzaSyD-....`) | That's an API key, not OAuth. Direct back to Step 4 to create a Desktop OAuth Client. |
| Raw client secret | If they somehow provide both ID + secret, construct the JSON file yourself and save it, then use the setup script. |

### If they can't find the download button

Some users see the OAuth client in the list but don't notice the ⋮ menu:

```
On the credentials page (https://console.cloud.google.com/apis/credentials):

1. Look for your OAuth 2.0 Client ID in the list
2. On the RIGHT side of that row, click ⋮ (three vertical dots)
3. In the dropdown, click "Download OAuth client" or "Download JSON"
4. The file saves to your Downloads folder
```

### CLI safety note

On the Hermes CLI, **do NOT send the file path `C:\...` as a bare message** —
a path starting with `/` could be mistaken for a slash command.
Always wrap it in a sentence, e.g.:
> The JSON file path is: C:\Users\sitis\Downloads\client_secret_524....json
