
---

# HoloEcho

## Overview

**HoloEcho** is a thread-safe, modular orchestrator for voice, sound, and keyboard-driven interaction in Python applications.
It unifies text-to-speech, speech recognition, audio signaling, and multi-modal input/output management—making it ideal for next-generation AI assistants, agent frameworks, and productivity tools.

**Highlights:**

* **Modular design:** Seamlessly integrates HoloTTS (text-to-speech), HoloSTT (speech input), and HoloWave (sound playback).
* **Multi-modal input/output:** Switch instantly between voice, keyboard, and ambient interaction.
* **Custom command mapping:** Flexible phrase recognition and user-definable command sets.
* **Thread-safe singleton:** Robust for multi-threaded, event-driven, and long-running applications.
* **Production-ready:** Centralized error handling, channel management, and extensible APIs.

---

## Why HoloEcho?

Voice-first and multi-modal applications demand more than simple speech-to-text or TTS.
**HoloEcho** brings together advanced voice recognition, TTS, audio feedback, and stateful input management—enabling:

* Natural switching between voice and keyboard modes.
* Real-time audio cues and contextual feedback.
* Easy addition of new commands and phrase triggers.
* Seamless orchestration of all sound and voice resources.

---

## Key Features

* **Unified Input Management:**
  Handle active/ambient voice, keyboard input, and quick mode switches from a single class.

* **Custom Command Mapping:**
  Map any phrase to custom actions or mode changes—user commands are merged with defaults for maximum flexibility.

* **Integrated Audio Feedback:**
  Play sound cues and synthesize voice output using HoloTTS and HoloWave.

* **Stateful Operation:**
  Tracks activation, standby, pause, and mode status for robust agent-like interaction.

* **Thread-Safe Singleton:**
  Safe for concurrent access and automation workflows.

---

## How It Works

1. **Instantiate HoloEcho** in your application.
2. **Configure commands and phrases** as needed (or use the built-in defaults).
3. **Handle input and output** via integrated methods (`voiceInput`, `ambientInput`, `keyboardInput`, `synthesize`, `getSound`).
4. **Switch modes** and manage agent state using built-in command recognition.

---

## FAQ

**Q: Do I need to manage TTS, speech recognition, and sound playback separately?**
A: No. HoloEcho wraps and orchestrates HoloTTS, HoloSTT, and HoloWave for you.

**Q: Can I add or override commands and phrases?**
A: Yes. Pass your own command dictionary or phrases; HoloEcho will merge them with defaults.

**Q: Is HoloEcho thread-safe and suitable for production?**
A: Yes. The singleton and locking mechanisms make it robust for advanced apps.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Authors
- Tristan McBride Sr.
- Sybil
