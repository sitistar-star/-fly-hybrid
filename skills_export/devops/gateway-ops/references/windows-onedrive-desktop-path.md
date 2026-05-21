# Windows Desktop Path (OneDrive)

## The Problem

On Windows with OneDrive Desktop sync, `C:\Users\<user>\Desktop` is NOT the real
Desktop. The Desktop is at `C:\Users\<user>\OneDrive\Desktop`. Writing files to
`~/Desktop/` or `C:\Users\user\Desktop/` makes them invisible to the user.

## The Fix

Always resolve the Desktop path via PowerShell:

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
```

From git-bash/terminal:

```bash
desktop=$(powershell.exe -Command "[Environment]::GetFolderPath('Desktop')")
echo "$desktop"
# C:\Users\user\OneDrive\Desktop
```

## When To Use This

- Creating Desktop shortcuts (.bat, .lnk)
- Copying project files for easy access
- Any user-facing file delivery

## How To Detect

Check `OneDrive\Desktop` exists:
```bash
if [ -d "/c/Users/$USER/OneDrive/Desktop" ]; then
  DESKTOP="/c/Users/$USER/OneDrive/Desktop"
else
  DESKTOP="/c/Users/$USER/Desktop"
fi
```

Or use the definitive PowerShell approach (preferred):
```powershell
[Environment]::GetFolderPath('Desktop')
```

## Why This Happens

Windows 10/11 with OneDrive enabled redirects known folders (Desktop, Documents,
Pictures) to OneDrive. The local `C:\Users\<user>\Desktop` folder may exist but
contain only synced metadata or be empty.
