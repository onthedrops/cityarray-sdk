# CITYARRAY - Festival Track

> Last Updated: 2026-02-14

## Track Overview
Temporary deployments for festivals, concerts, sporting events, and venues. Focus on sponsor integration, mobile demos, and fast setup/teardown.

---

## Target Use Cases
- Wayfinding (stages, restrooms, water, first aid, exits)
- Crowd management (capacity, wait times, flow direction)
- Schedule/lineup updates (now playing, up next)
- Sponsor messaging (branded content, activations)
- Safety alerts (weather, evacuations, lost children)
- Rideshare coordination (pickup zones, wait times)

---

## Deployment Architecture

### Festival Setup (5-10 Signs)
WiFi-based with M4 MacBook as mobile dashboard server.

**Per Sign Hardware:**
| Component | Model | Cost |
|-----------|-------|------|
| Compute | Raspberry Pi 5 (8GB) | $80 |
| AI Accelerator | Hailo-8L AI HAT | $70 |
| Camera | Sony IMX500 | $70 |
| Audio | Waveshare USB (speaker+mic) | $30 |
| LED Controller | MatrixPortal S3 | $25 |
| LED Panel | Waveshare 64×32 | $35 |
| Battery | USB-C power bank (optional) | $50 |
| Mounting | Tripod/clamp | $30 |
| **Total** | | **~$390-440** |

**10-Sign Festival Kit:**
- Hardware: ~$4,000-4,500
- No monthly data cost (WiFi)

### Network Options
1. **Venue WiFi** - Use existing infrastructure
2. **M4 Hotspot** - MacBook creates network, signs connect
3. **Portable Router** - GL.iNet or similar travel router
4. **Cellular Hub** - Single RUT956 for backup/remote locations

---

## Mobile Demo Setup

### Hardware Checklist
- [ ] M4 MacBook (charged)
- [ ] Pi 5 + power supply (27W USB-C)
- [ ] MatrixPortal S3 + LED panel
- [ ] Waveshare USB audio
- [ ] Camera (IMX500)
- [ ] USB-C cables
- [ ] Power strip / extension cord
- [ ] Tripod or mounting solution

### Software Checklist
- [ ] Dashboard running on M4
- [ ] sign_client.py configured for M4's IP
- [ ] MatrixPortal WiFi configured for demo network
- [ ] Ollama running on Pi 5
- [ ] Test messages prepared

### Network Modes

**Mode A: M4 Hotspot**
```
M4 MacBook (hotspot: "CITYARRAY-Demo")
├── Dashboard: http://192.168.x.1:8000
├── Pi 5 connects to hotspot
└── MatrixPortal connects to hotspot
```

**Mode B: Venue WiFi**
```
Venue WiFi Router
├── M4 MacBook: Get assigned IP
├── Pi 5: Get assigned IP
├── MatrixPortal: Get assigned IP
└── Update DASHBOARD_HOST in sign_client.py
```

### Demo Script
1. Show dashboard UI on M4
2. Send "WELCOME" message → LED displays
3. Show bilingual toggle (EN → ES)
4. Send emergency alert → Flash + TTS audio
5. Show icons (water, restroom, exit)
6. Show progress bar (capacity 75%)
7. Explain crowd detection (camera) and audio (mic)

---

## Sponsor Integration

### Sponsored Message Types
- Logo display (bitmap icons)
- Branded wayfinding ("Coca-Cola Hydration Station →")
- Activation callouts ("Visit the Samsung Tent!")
- Schedule sponsorship ("Main Stage presented by Budweiser")

### Pricing Ideas (Per Event)
| Tier | Includes | Price Range |
|------|----------|-------------|
| Bronze | Logo in rotation, 1 zone | $500-1,000 |
| Silver | Branded wayfinding, 3 zones | $2,000-5,000 |
| Gold | Dedicated sign, custom content | $5,000-10,000 |
| Presenting | All signs, headline placement | $15,000-25,000 |

### Technical Needs
- [ ] Bitmap icon upload for sponsor logos
- [ ] Scheduled message rotation
- [ ] Zone-based content targeting
- [ ] Analytics (impressions, dwell time)

---

## Event Types & Fit

| Event Type | Signs | Key Features | Complexity |
|------------|-------|--------------|------------|
| Music Festival | 8-15 | Stages, sponsors, crowds | High |
| Food Festival | 5-10 | Vendors, wayfinding | Medium |
| Sporting Event | 5-10 | Scores, concessions | Medium |
| Conference | 3-5 | Sessions, rooms | Low |
| Corporate Event | 2-5 | Branding, wayfinding | Low |
| Farmers Market | 2-3 | Vendors, specials | Low |

---

## Open Questions (Festival Track)

- [ ] Battery runtime testing (full day operation?)
- [ ] Weather protection for temporary deployment (pop-up tents? quick covers?)
- [ ] Rapid setup process (< 30 min per sign?)
- [ ] Content management for non-technical event staff
- [ ] Sponsor logo format/upload workflow

---

## Risks (Festival Track)

| Risk | Severity | Mitigation |
|------|----------|------------|
| WiFi congestion | High | Dedicated SSID, 5GHz, cellular backup |
| Weather (rain/wind) | High | Quick covers, weighted bases |
| Power availability | Medium | Battery backup, generator coordination |
| Theft during event | Medium | Staff supervision, GPS tracking |
| Last-minute changes | Medium | Simple dashboard UI, templates |

---

## Next Actions

1. [ ] Document M4 hotspot demo setup step-by-step
2. [ ] Create demo script with talking points
3. [ ] Test battery runtime (Pi 5 + MatrixPortal)
4. [ ] Design simple sponsor logo upload flow
5. [ ] Build event template library (festival, conference, etc.)
6. [ ] Identify first festival/venue partner

---

## Related Files
- `PROJECT_MEMORY.md` - Shared hardware/software state
- `HARDWARE_INVENTORY.md` - Component specs
- `CONFIGURATION.md` - Paths and settings
- `../festivals/` - Festival-specific business docs
