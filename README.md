# CITYARRAY SDK

**Autonomous Emergency Communications Intelligence**

CITYARRAY is an open-source platform for deploying intelligent, multilingual emergency communication signs at festivals, events, and public spaces.

![Status](https://img.shields.io/badge/status-active%20development-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)

## 🎯 What is CITYARRAY?

CITYARRAY transforms passive signage into an intelligent communication network that can:

- **Broadcast emergency alerts** in multiple languages simultaneously
- **Detect crowds** using AI-powered cameras
- **Respond to voice queries** via local AI (no cloud required)
- **Operate autonomously** when network connectivity is lost
- **Scale dynamically** from a single sign to hundreds

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CITYARRAY Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐    WebSocket    ┌─────────────────────┐   │
│   │  Dashboard  │◄───────────────►│    Sign Fleet       │   │
│   │  (Operator) │                 │  ┌───┐ ┌───┐ ┌───┐  │   │
│   └─────────────┘                 │  │ π │ │ π │ │ π │  │   │
│         │                         │  └───┘ └───┘ └───┘  │   │
│         │ REST API                └─────────────────────┘   │
│         ▼                                   │               │
│   ┌─────────────┐                          │               │
│   │  Templates  │    Each sign has:        │               │
│   │  Messages   │    • LED Display         │               │
│   │  Zones      │    • AI Camera           │               │
│   │  Events     │    • Speaker/Mic         │               │
│   └─────────────┘    • Local LLM           │               │
│                      • Cellular backup     │               │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Repository Structure

```
cityarray-sdk/
├── cityarray-sdk-v2/     # Core SDK (current version)
│   ├── core/             # Sign management, messaging
│   ├── ai/               # Ollama integration, VLM
│   └── hardware/         # Display, audio, sensors
├── docs/                 # Documentation
├── pi/                   # Raspberry Pi configurations
├── tasks/                # Development tasks
├── city_data.py          # Sample city/venue data
├── demo.py               # Demo scenarios
├── scenarios.py          # Emergency scenario templates
└── venues.py             # Venue definitions
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Raspberry Pi 5 (for hardware deployment)
- Optional: Ollama for local AI

### Installation

```bash
git clone https://github.com/onthedrops/cityarray-sdk.git
cd cityarray-sdk/cityarray-sdk-v2
pip install -r requirements.txt
```

### Run Demo

```bash
python demo.py
```

## 🔗 Related Repositories

| Repository | Description |
|------------|-------------|
| [cityarray-festival](https://github.com/onthedrops/cityarray-festival) | Festival Edition with dashboard & sign client |

## 🛠️ Hardware Components

### Sign Unit (Per-Sign)

| Component | Model | Purpose |
|-----------|-------|---------|
| Computer | Raspberry Pi 5 (4GB+) | Main controller |
| AI Accelerator | Hailo-8L (AI HAT+) | Local inference |
| Display | 64x32 RGB LED Matrix | Visual alerts |
| Display Driver | Matrix Portal S3 | LED control via WiFi |
| Camera | Raspberry Pi AI Camera | Crowd detection |
| Audio | USB Speaker/Mic | Announcements & input |
| Network | Cellular HAT (optional) | Failover connectivity |

### Supported Languages (TTS)

| Language | Engine | Status |
|----------|--------|--------|
| English | Piper | ✅ |
| Spanish | Piper | ✅ |
| Chinese (Mandarin) | Piper | ✅ |
| Vietnamese | Piper | ✅ |
| French | Piper | ✅ |
| Arabic | Piper | ✅ |
| Portuguese | Piper | ✅ |
| Korean | Edge-TTS | ✅ |
| Japanese | Edge-TTS | ✅ |
| Hindi | Edge-TTS | ✅ |

## 🧠 AI Capabilities

### Local AI (Offline-Capable)

- **LLM**: Ollama with Llama 3.2 (3B) for conversational responses
- **VLM**: Moondream2 for camera scene understanding
- **STT**: Whisper.cpp for speech recognition
- **TTS**: Piper for natural voice synthesis

### Cloud AI (Optional)

- Claude API for complex reasoning
- Edge-TTS for additional languages

## 📡 Network Resilience

CITYARRAY is designed to operate in challenging network conditions:

1. **Primary**: WiFi or Ethernet
2. **Failover**: Cellular (4G/5G) via multi-carrier SIM
3. **Offline**: Local operation with cached templates

```
Normal Mode:     Sign ←→ Dashboard ←→ Operator
Degraded Mode:   Sign ←→ Dashboard (cached)
Offline Mode:    Sign operates autonomously
```

## 🎪 Use Cases

- **Music Festivals**: Stage directions, weather alerts, lost & found
- **Conferences**: Session updates, emergency evacuation
- **Public Spaces**: Transit info, community alerts
- **Construction Sites**: Safety warnings, air quality
- **Smart Cities**: Integrated urban communication network

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md).

### Development Setup

```bash
# Clone the repo
git clone https://github.com/onthedrops/cityarray-sdk.git
cd cityarray-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - Fast local text-to-speech
- [Ollama](https://ollama.ai) - Local LLM inference
- [Hailo](https://hailo.ai) - Edge AI acceleration
- [Array of Things](https://arrayofthings.github.io/) - Urban sensing inspiration

## 📬 Contact

- **Project Lead**: Eben
- **GitHub**: [@onthedrops](https://github.com/onthedrops)

---

*"Maternal AI for public safety"* - CITYARRAY embodies caring, protective qualities in emergency communications.
