# Felo Skills Install on Windows — Path Pitfall

## Symptom

After running `install-hermes.sh` from Felo, skills appear in `~/.hermes/skills/felo/`
but `hermes skills list` shows nothing.

## Root Cause

The install script uses `$HOME/.hermes/skills/` as the Hermes home, but on **Windows**
the actual Hermes home is `~/AppData/Local/hermes/skills/` (or `%USERPROFILE%\AppData\Local\hermes\skills\`).

## Fix

Copy the skills directory to the correct path:

```bash
cp -r ~/.hermes/skills/felo ~/AppData/Local/hermes/skills/felo
```

Then reload skills:

```bash
hermes skills list          # Verify they appear
```

## Prevention

When using any install script that targets `~/.hermes/`:
1. Check `hermes config path` to confirm the real Hermes home
2. The redirect script may install to `~/.hermes/` instead — always verify with `hermes skills list`
3. On Windows, `~/.hermes/` may be created as a separate directory (not a symlink)
