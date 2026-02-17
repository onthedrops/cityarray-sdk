# CITYARRAY - City Track

> Last Updated: 2026-02-14

## Track Overview
Permanent smart city deployments with 20+ signs, cellular connectivity, and public safety integration.

---

## Target Use Cases
- Emergency alerts (evacuations, shelter-in-place, active threats)
- Transit information (bus arrivals, service disruptions)
- Public safety messaging (AMBER alerts, weather warnings)
- Wayfinding (parking, events, city services)
- Accessibility (ADA-compliant multilingual messaging)

---

## Deployment Architecture

### Recommended: Individual Cellular (Option A)
Each sign has its own cellular gateway for maximum reliability.

**Per Sign Hardware:**
| Component | Model | Cost |
|-----------|-------|------|
| Compute | Raspberry Pi 5 (8GB) | $80 |
| AI Accelerator | Hailo-8L AI HAT | $70 |
| Camera | Sony IMX500 | $70 |
| Cellular Gateway | Teltonika RUT956 | $275 |
| Audio | Waveshare USB (speaker+mic) | $30 |
| LED Controller | MatrixPortal S3 | $25 |
| LED Panel | Waveshare 64×32 | $35 |
| Enclosure | NEMA 4X (custom) | $150-200 |
| Antennas | LTE MIMO + GPS | $50 |
| Power | PoE injector or grid | $50 |
| **Total** | | **~$835-935** |

**20-Sign Deployment:**
- Hardware: ~$17,000-19,000
- Monthly data: ~$300-400 (multi-carrier SIM)

### Alternative: Hub & Spoke (Option B)
4-6 cellular hubs serving clusters of WiFi signs. Lower cost but less redundant.

---

## Cellular Gateway Selection

### Leading Candidate: Teltonika RUT956
- Price: $275-325
- Cat 4 LTE (150/50 Mbps)
- Dual SIM auto-failover
- GNSS (GPS/GLONASS/BeiDou/Galileo)
- Industrial: -40°C to 75°C, aluminum housing
- AT&T/Verizon/T-Mobile certified
- Remote management via Teltonika RMS

### Alternative: Cradlepoint S700
- Price: $650-900 + $15-25/mo NetCloud
- Better management, higher cost
- Consider for enterprise/government contracts

### Multi-Carrier SIM Providers
| Provider | Notes |
|----------|-------|
| Choice IoT | Verizon/AT&T/T-Mobile, pooled data, no contracts |
| SIMETRY | Tier-1 data, FirstNet support, 24/7 NOC |
| Hologram | $0.40/MB pay-as-you-go, global |
| EIOTCLUB | 24GB/year for $100 |

---

## FirstNet Integration

For public safety priority during emergencies:
- AT&T's dedicated Band 14 (700 MHz)
- Never throttled, priority + preemption
- Requires partnership with city emergency services
- FirstNet IoT Connect for device management
- Higher cost but critical for emergency use case

**Action:** Identify city emergency management contact to explore FirstNet partnership.

---

## Compliance & Procurement

### Technical Requirements
- [ ] ADA compliance (audio announcements, contrast ratios)
- [ ] FCC certification for RF components
- [ ] UL listing for enclosures
- [ ] MUTCD compliance if used for traffic/wayfinding

### Procurement Path
- [ ] Research city RFP processes
- [ ] Identify small-dollar threshold for pilot (often <$25K)
- [ ] GSA Schedule potential for federal/state
- [ ] Cooperative purchasing agreements (NASPO, Sourcewell)

---

## Open Questions (City Track)

- [ ] Which city for first pilot? (Size, contacts, budget cycle)
- [ ] FirstNet vs commercial cellular for pilot?
- [ ] Enclosure vendor selection
- [ ] Maintenance/support model for city contracts
- [ ] Integration with existing city systems (CAD, CAP, 311)

---

## Risks (City Track)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Long procurement cycles | High | Start with small-dollar pilot |
| Integration complexity | High | Standard APIs, CAP support |
| Vandalism/theft | Medium | Tamper alerts, insurance, easy replacement |
| Cellular dead zones | Medium | Multi-carrier SIM, site survey |
| Political turnover | Medium | Multi-department champions |

---

## Next Actions

1. [ ] Order 1x Teltonika RUT956 for bench testing
2. [ ] Test Pi 5 + RUT956 connectivity
3. [ ] Research pilot city candidates
4. [ ] Draft pilot proposal deck
5. [ ] Identify FirstNet partnership path

---

## Related Files
- `PROJECT_MEMORY.md` - Shared hardware/software state
- `HARDWARE_INVENTORY.md` - Component specs
- `NETWORK_MAP.md` - Architecture diagrams
- `../cities/` - City-specific business docs
