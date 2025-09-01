# Livekit Plugins

This repository contains custom plugin implementations for [Livekit Agents](https://github.com/livekit/agents) to enable integration with proprietary or third-party Speech-to-Text (STT) and Text-to-Speech (TTS) services.

## Included Plugins

- **Piper TTS**: Integration with a Piper-based TTS API.
- **Trebe TTS**: Integration with the Trebe TTS API (supports multiple voices).
- **Trebe STT**: Integration with the Trebe real-time STT API.

## Requirements

- Python 3.9+
- `aiohttp`
- `livekit-agents` (or compatible API)
- (For Trebe plugins) A valid Trebe API key

## Installation

Clone this repository and install the dependencies in your Python environment:

```bash
git clone https://github.com/irontec-comms/livekit-plugins.git
cd livekit-plugins
pip install -r requirements.txt
```

> **Note:** You may need to install `livekit-agents` and other dependencies manually if not provided.

## Instalación desde GitHub

Agrega esto a tu `requirements.txt` o ejecuta:

```
pip install git+ssh://git@github.com/irontec-comms/livekit-plugins.git
```

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.