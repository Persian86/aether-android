# Aether Android

Mobile version of the Aether AI Assistant (inspired by Mark-LVI and Brahma-Echo).

## Features
- Holographic animated core
- Text + voice chat (Android speech recognition)
- Gemini 2.0 Flash AI
- Settings for API key
- Modern dark UI

## Run on desktop (for testing)
```bash
pip install -r requirements.txt
python main.py
```

## Build Android APK

### Prerequisites
- Linux or WSL2 (Buildozer works best on Linux)
- `buildozer` and Android SDK/NDK

### Steps
1. Install Buildozer:
   ```bash
   pip install buildozer
   ```
2. Copy a logo image as `logo.png` into this folder.
3. Build:
   ```bash
   buildozer android debug
   ```
4. The APK will be in `bin/`.

### Notes
- Set your free Gemini API key in the app settings.
- Microphone permission is requested for voice input.
- First build takes a while (downloads SDK/NDK).

## License
MIT
