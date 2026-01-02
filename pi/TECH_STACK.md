# CITYARRAY Tech Stack

## Hardware

| Component | Model |
|-----------|-------|
| Computer | Raspberry Pi 5 (4GB+) |
| AI Accelerator | Hailo-8L (13 TOPS) |
| Camera | OV5647 Pi Camera |
| Audio | USB Audio Adapter |
| Display (current) | Pygame LED Simulator |
| Display (pending) | 64x32 RGB LED Matrix + Pico 2 |

## AI / ML

| Function | Technology | Speed |
|----------|------------|-------|
| Object Detection | YOLOv8s on Hailo | 35ms |
| Scene Understanding | Moondream VLM | 60s |
| Reasoning | Ollama + Phi3:mini | 30-60s |
| Speech-to-Text | OpenAI Whisper (tiny) | 3-5s |
| Text-to-Speech | espeak | instant |

## APIs

| Service | Provider | Data |
|---------|----------|------|
| Weather | OpenWeatherMap | Temp, conditions, humidity |
| Air Quality | OpenWeatherMap | AQI, PM2.5 |
| Alerts | National Weather Service | Real-time emergency alerts |

## Languages & Libraries

| Purpose | Technology |
|---------|------------|
| Core | Python 3.13 |
| Display | Pygame |
| Database | SQLite |
| HTTP | Requests |
| AI Runtime | hailo_platform |
| Vision | PIL, OpenCV |
| Audio Record | arecord (ALSA) |
| Audio Play | aplay (ALSA) |

## Supported Languages

| Code | Language | Script |
|------|----------|--------|
| en | English | Native |
| es | Spanish | Native |
| zh | Chinese | Pinyin (romanized) |
| ko | Korean | Romanized |
| vi | Vietnamese | Native |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CITYARRAY AGENT                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Camera  │───►│ Hailo   │───►│Database │            │
│  │ OV5647  │    │ YOLOv8  │    │ SQLite  │            │
│  └─────────┘    │ (35ms)  │    └────┬────┘            │
│                 └─────────┘         │                  │
│                                     ▼                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │   Mic   │───►│ Whisper │───►│ Query   │            │
│  │   USB   │    │  STT    │    │ Handler │            │
│  └─────────┘    └─────────┘    └────┬────┘            │
│                                     │                  │
│       ┌─────────────────────────────┼──────────┐      │
│       │                             │          │      │
│       ▼                             ▼          ▼      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│  │ Weather │    │   AQI   │    │   NWS   │           │
│  │   API   │    │   API   │    │ Alerts  │           │
│  └─────────┘    └─────────┘    └─────────┘           │
│       │              │              │                 │
│       └──────────────┴──────────────┘                 │
│                      │                                │
│                      ▼                                │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│  │ Display │◄───│Response │───►│ Speaker │           │
│  │64x32 LED│    │Generator│    │   TTS   │           │
│  └─────────┘    └─────────┘    └─────────┘           │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## Voice Commands

| Command | Action |
|---------|--------|
| "City, what do you see?" | Hailo object detection |
| "City, how many people?" | Count persons |
| "City, what time is it?" | Local time |
| "City, time in Tokyo?" | Tokyo local time |
| "City, weather?" | LA weather |
| "City, weather in Paris?" | Paris weather |
| "City, air quality?" | LA AQI |
| "City, air quality in Beijing?" | Beijing AQI |
| "City, any alerts?" | NWS alerts |
| "City, is it safe?" | Safety check |

## File Structure

```
~/pi/
├── Core
│   ├── agent.py              # Original agent loop
│   ├── agent_hailo.py        # Hailo-accelerated agent
│   └── database.py           # SQLite logging
│
├── Detection
│   ├── detect.py             # CPU detection
│   ├── hailo_detect.py       # Hailo detection (35ms)
│   ├── vlm_detect.py         # VLM scene understanding
│   └── hybrid_detect.py      # YOLO + VLM hybrid
│
├── Voice
│   ├── audio.py              # TTS module
│   ├── voice_input.py        # Whisper STT
│   └── voice_assistant.py    # Voice assistant loop
│
├── Display
│   ├── led_simulator.py      # Pygame LED simulator
│   └── templates.py          # Multilingual messages
│
├── Data
│   ├── city_data.py          # Weather/AQI/NWS APIs
│   ├── venues.py             # Venue context
│   └── scenarios.py          # Emergency scenarios
│
├── Demos
│   ├── demo.py               # Visual-only demo
│   ├── demo_audio.py         # Demo with audio
│   └── demo_full.py          # Full demo + voice assistant
│
├── AI
│   ├── reasoning.py          # LLM reasoning
│   └── query.py              # Query handler
│
└── Docs
    └── README.md             # Project readme
```

## Performance

| Operation | Speed |
|-----------|-------|
| Hailo detection | 35ms |
| CPU detection (old) | 325ms |
| VLM scene analysis | 60-90s |
| LLM reasoning | 30-60s |
| Whisper transcription | 3-5s |
| Weather API | <1s |
| Database query | <10ms |

## Security Architecture

- Trust No Edge: Edge devices untrusted
- Cryptographic authorization for emergency alerts
- Tiered alert system:
  - Informational: Autonomous
  - Advisory: Autonomous
  - Warning: Requires authorization
  - Emergency: Requires cryptographic signature

## Pending Hardware

| Item | Purpose |
|------|---------|
| Raspberry Pi Pico 2 | USB display controller |
| 64x32 RGB LED Matrix | Physical display |
| HUB75 cable | Matrix connection |

---

*Updated December 2024*
