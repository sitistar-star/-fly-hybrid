# Gmail IMAP Account Recovery for Obsidian

When the user has forgotten their Obsidian password and needs to retrieve the password-reset email, use this Gmail IMAP flow.

## Prerequisites

- Gmail account with **2FA enabled** → requires an **App Password**
- Python `imaplib` (stdlib — no install needed)

## Get a Gmail App Password

1. User opens: https://myaccount.google.com/apppasswords
2. Creates a named app password (e.g., "Hermes")
3. Copies the 16-character password (format: `xxxx xxxx xxxx xxxx`)

## Fetch the Obsidian Password-Reset Email

```python
import imaplib, email, re

mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
mail.login("user@gmail.com", "apppasswordwithoutspaces")
mail.select("INBOX")

# Search for Obsidian emails
status, messages = mail.search(None, 'FROM', 'obsidian')
msg_ids = messages[0].split()
latest_id = msg_ids[-1]

status, data = mail.fetch(latest_id, "(RFC822)")
msg = email.message_from_bytes(data[0][1])

# Extract body
body = ""
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
            break
else:
    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

# Find reset link
links = re.findall(r'https?://[^\s<>"\']+', body)
reset_link = [l for l in links if 'reset' in l.lower() or 'password' in l.lower()]
print(reset_link[0] if reset_link else "No reset link found")
```

## Reset link format

Obsidian reset links look like:
```
https://obsidian.md/account#forgetpw&id=<id>&key=<key>
```

## Browser login via JavaScript

Obsidian uses a Gatsby/React SPA that may not render in the browser's accessibility tree. When the snapshot is empty, use `browser_console` to interact:

```javascript
// Set email
document.getElementById('labeled-input-email').value = 'user@example.com';
// Set password
document.getElementById('labeled-input-password').value = 'newpassword';
// Click Sign in (second button)
document.querySelectorAll('button')[1].click();
```

Wait ~3s, then check success:
```javascript
document.querySelector('h1')?.innerText  // null if login succeeded
document.body.innerText.substring(0, 500) // should show "Profile / Billing / Sync..."
```

## Pitfalls

- **Google blocks headless browsers** — the Hermes browser (Comet) will fail at the Google sign-in page with "This browser or app may not be secure." Use IMAP instead.
- **App passwords require 2FA** — if the user doesn't have 2FA, Gmail allows direct IMAP login with the regular password (still may be blocked for "less secure apps").
- **Reset link in email uses `#` hash** — Obsidian's SPA reads `window.location.hash`, not query params. Opening `obsidian.md/account#forgetpw&id=X` in a headless browser may strip params; use the email link in a real browser instead.
- **Password reset sends duplicate emails** — each click of "Forgot password?" sends a new email. Always use the most recent one.
