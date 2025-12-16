# CITYARRAY Virtual LED Simulator

## Project Goal
Build a pygame-based LED matrix simulator that integrates with the SDK v2 security modules. This allows testing the full detection → decision → display pipeline without physical hardware.

---

## Todo List

### Phase 1: Core Simulator
- [ ] 1.1 Create `led_simulator.py` - pygame window that renders an LED matrix grid
- [ ] 1.2 Add pixel-level control (set individual LED colors)
- [ ] 1.3 Add text rendering (convert text to LED pixel patterns)
- [ ] 1.4 Add color support (red, green, amber, white for emergencies)

### Phase 2: SDK Integration
- [ ] 2.1 Create `SimulatorDisplayBackend` class implementing `SecureDisplayBackend` interface
- [ ] 2.2 Connect to existing `SecureDisplayEngine` from SDK v2
- [ ] 2.3 Verify only signed messages can display (test rejection of unsigned)

### Phase 3: Demo Application
- [ ] 3.1 Create `demo_simulator.py` that shows:
  - Informational message (autonomous, displays immediately)
  - Warning message (rejected without authorization)
  - Simulated detection event triggering alert
- [ ] 3.2 Add keyboard controls (1=info, 2=advisory, 3=warning, ESC=quit)

### Phase 4: Polish
- [ ] 4.1 Add LED "glow" effect for realism
- [ ] 4.2 Add scrolling text for long messages
- [ ] 4.3 Add timestamp display in corner

---

## File Changes Summary

| File | Action | Location |
|------|--------|----------|
| `led_simulator.py` | Create | `cityarray-sdk-v2/src/cityarray/display/` |
| `demo_simulator.py` | Create | `cityarray-sdk-v2/examples/` |

---

## Technical Approach

**Display Size:** 64x32 pixels (matches P3 LED panel from hardware spec)

**Dependencies:** 
- pygame (already in optional dependencies)
- Existing SDK security modules (no changes needed)

**Architecture:**
```
┌─────────────────────────────────────────┐
│            demo_simulator.py            │
│         (keyboard input, demo flow)     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          SecureDisplayEngine            │
│    (signature verification - existing)  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       SimulatorDisplayBackend           │
│            (NEW - pygame)               │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│           LEDSimulator                  │
│     (NEW - pixel grid rendering)        │
└─────────────────────────────────────────┘
```

---

## Review

*To be completed after implementation*

### Changes Made
- [ ] List of files created/modified

### Testing Results
- [ ] Demo runs successfully
- [ ] Signed messages display
- [ ] Unsigned messages rejected

### Notes
- 
