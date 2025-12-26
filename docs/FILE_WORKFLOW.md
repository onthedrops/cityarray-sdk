# CITYARRAY File Workflow Guide

A simple guide to keep files organized and pushed to GitHub.

---

## Repository Structure

```
cityarray-sdk/                      ← Your repo root
├── cityarray-sdk-v2/               ← Main SDK code
│   ├── src/cityarray/
│   │   ├── security/               ← Signing, audit, tiers, keys
│   │   ├── display/                ← LED simulator, secure engine
│   │   ├── detection/              ← (future) YOLOv8
│   │   ├── decision/               ← (future) Rules engine
│   │   └── tts/                    ← (future) Text-to-speech
│   ├── examples/                   ← Demo scripts
│   └── tests/                      ← Test files
├── docs/                           ← Documentation
│   ├── activity.md                 ← Development log
│   ├── SOVEREIGN_SDK.md            ← Architecture spec
│   ├── CITYARRAY_Security_Design.docx
│   └── CITYARRAY_Sovereign_AI_Analysis.docx
└── tasks/                          ← Project tracking
    └── todo.md                     ← Current tasks
```

---

## Where Files Go

| File Type | Location |
|-----------|----------|
| Python modules (`.py`) | `cityarray-sdk-v2/src/cityarray/{module}/` |
| Demo scripts | `cityarray-sdk-v2/examples/` |
| Tests | `cityarray-sdk-v2/tests/` |
| Documentation (`.md`, `.docx`) | `docs/` |
| Task tracking | `tasks/` |

---

## Step-by-Step: Download → Place → Push

### Step 1: Download from Claude

Click the file links in chat to download. Files go to `~/Downloads/`.

### Step 2: Check Downloads

```bash
ls ~/Downloads/*.py ~/Downloads/*.md 2>/dev/null
```

### Step 3: Move Files to Correct Location

**For Python files:**
```bash
# Display module files
mv ~/Downloads/led_simulator.py cityarray-sdk-v2/src/cityarray/display/
mv ~/Downloads/simulator_backend.py cityarray-sdk-v2/src/cityarray/display/

# Example scripts
mv ~/Downloads/demo_simulator.py cityarray-sdk-v2/examples/

# If it's an __init__.py replacement
mv ~/Downloads/display_init.py cityarray-sdk-v2/src/cityarray/display/__init__.py
```

**For documentation:**
```bash
mv ~/Downloads/activity.md docs/
mv ~/Downloads/todo.md tasks/
mv ~/Downloads/SOME_DOC.md docs/
```

### Step 4: Add, Commit, Push

```bash
git add .
git commit -m "Your message here"
git push
```

---

## Quick Reference Commands

### Check what needs to be committed
```bash
git status
```

### See current folder
```bash
pwd
```

### List files
```bash
ls -la
```

### Go to repo root
```bash
cd ~/cityarray-sdk
```

### Go to SDK source
```bash
cd ~/cityarray-sdk/cityarray-sdk-v2/src/cityarray
```

---

## Common Issues

### "No such file or directory"
The file isn't where you think. Check:
```bash
ls ~/Downloads/
ls .
```

### "pathspec did not match any files"
The folder doesn't exist. Create it:
```bash
mkdir -p cityarray-sdk-v2/src/cityarray/display
```

### "fatal: not a git repository"
You're not in the repo. Navigate to it:
```bash
cd ~/cityarray-sdk
```

---

## VS Code Alternative

Instead of terminal commands:

1. **Drag and drop** files from Finder into VS Code folder tree
2. **Source Control panel** (Cmd+Shift+G):
   - Click `+` to stage files
   - Type commit message
   - Click ✓ to commit
   - Click "Sync Changes" to push

---

## Checklist Before Ending Session

- [ ] All downloaded files moved to correct locations
- [ ] `git status` shows no uncommitted changes
- [ ] `git push` completed successfully
- [ ] `activity.md` updated with session work
- [ ] `todo.md` reflects current progress

---

## File Naming from Claude

When I create files, I'll tell you:
- **Filename** — exact name to save as
- **Location** — where it goes in the repo

Example:
> `simulator_backend.py` → `cityarray-sdk-v2/src/cityarray/display/`

This means:
```bash
mv ~/Downloads/simulator_backend.py cityarray-sdk-v2/src/cityarray/display/
```

---

*Last updated: 2024-12-15*
