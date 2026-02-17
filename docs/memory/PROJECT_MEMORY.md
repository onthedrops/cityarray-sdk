# CITYARRAY Project Memory

> Last Updated: 2026-02-17

## Project Overview
- **Name**: CITYARRAY
- **Description**: Autonomous emergency communications platform with LED signs, edge AI, environmental sensors, cameras, and two-way audio
- **Stage**: Working prototype (1 sign), two parallel tracks

---

## Development Tracks

| Track | Focus | File |
|-------|-------|------|
| **City** | Permanent 20+ sign deployments, cellular, FirstNet | `CITY_TRACK.md` |
| **Festival** | Temporary 5-10 signs, WiFi, sponsors, mobile demos | `FESTIVAL_TRACK.md` |

**This file** covers shared hardware, software, and infrastructure.

---

## Current Objective
1. **City Track**: Scale to 20-sign cellular deployment
2. **Festival Track**: Mobile demo capability, sponsor integration

---

## Shared Hardware (Prototype)

### Raspberry Pi 5 (192.168.1.112)
- Hailo-8L AI HAT (13 TOPS)
- Sony IMX500 AI Camera (on-sensor processing)
- Waveshare USB Audio (speaker + microphone)

### MatrixPortal S3 (192.168.1.239)
- Waveshare 64×32 RGB LED Matrix
- CircuitPython firmware
- HTTP API for display control

### Development Machines
- M1 Mac Mini (192.168.1.80) - Primary dev server
- M4 MacBook - Mobile demos

---

## Shared Software

### Dashboard (Flask)
- Location: `~/cityarray-sdk/cityarray-festival/dashboard/`
- WebSocket communication to signs
- REST API for messages, signs, zones
- Templates: messages.html, signs.html

### Sign Client (Pi 5)
- Location: `~/cityarray/sign-client/sign_client.py`
- Bridges dashboard ↔ MatrixPortal
- Bilingual messaging (EN/ES) with Ollama translation
- Piper TTS for audio announcements

### LED Sign API
- Display types: text, scroll, flash, pulse, progress, gradient
- 20+ icons (wayfinding, alerts, sponsors)
- 7 colors + 5 gradients

---

## Key Decisions (Shared)

| Decision | Rationale | Date |
|----------|-----------|------|
| Hailo-8L over Coral | Better Pi 5 integration | Pre-2026 |
| IMX500 camera | On-sensor AI reduces Pi load | Pre-2026 |
| Piper TTS (local) | Privacy, offline capability | Pre-2026 |
| Ollama for translation | Local LLM, works offline | Pre-2026 |
| Bilingual EN/ES first | Largest US language pair | 2026-02 |
| Teltonika RUT956 | Best price/performance for city deployments | 2026-02 |

---

## Documentation Structure

```
docs/
├── memory/
│   ├── PROJECT_MEMORY.md      ← This file (shared)
│   ├── CITY_TRACK.md          ← City-specific
│   ├── FESTIVAL_TRACK.md      ← Festival-specific
│   ├── HARDWARE_INVENTORY.md
│   ├── NETWORK_MAP.md
│   ├── CONFIGURATION.md
│   └── TROUBLESHOOTING.md
├── prompts/                    ← Session management prompts
├── sessions/                   ← Per-session logs
├── cities/                     ← City business docs
├── festivals/                  ← Festival business docs
└── shared/                     ← Shared business docs
```

---

## Session Workflow

### Starting a Session
1. Upload `PROJECT_MEMORY.md` (always)
2. Upload track file (`CITY_TRACK.md` or `FESTIVAL_TRACK.md`) based on focus
3. Optionally upload `TODO.md`
4. Tell Claude what you want to work on

### Ending a Session
1. Ask Claude to update the relevant memory/track files
2. Save updated files locally
3. Commit to GitHub

---

## Session History

### 2026-02-17
- Created track-based documentation approach (CITY_TRACK.md, FESTIVAL_TRACK.md)
- Updated PROJECT_MEMORY.md to reference tracks

### 2026-02-14
- Researched cellular gateways: Cradlepoint, Teltonika, Digi, Sierra Wireless
- Researched multi-carrier SIM providers
- Defined three deployment architecture options with costs
- Created documentation framework
- Captured hardware inventory in Claude's permanent memory
- Dashboard UI updates: display types, progress bars, gradients, icons
