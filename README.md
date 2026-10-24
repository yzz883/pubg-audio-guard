# PUBG Audio Guard

**Night-mode hearing protection for PUBG** — a per-app audio processor that tames gunshots, explosions and grenade "boomy" effects while lifting footsteps, so you can turn your system volume down and still hear everything. Only PUBG's audio is processed; every other app (voice chat, notifications, music) is untouched.

`English` | [简体中文](README_zh-CN.md) | [Русский](README_ru-RU.md) | [Español](README_es-ES.md) | [日本語](README_ja-JP.md)

![screenshot](docs/screenshot.png)

## Why

In PUBG you keep the volume high to hear quiet footsteps — then a grenade lands and the explosion blasts your ears. The damage comes from *peaks* (gunshots, explosions), not the average level. This tool reshapes PUBG's audio in real time:

- **Compressor + limiter** — caps every peak at a fixed ceiling (nothing can ever blast you), lifts quiet sounds
- **Equalizer** — cuts the low-frequency "chest punch" of grenades/explosions and the high-frequency "tinnitus" whine the game plays after explosions
- **Per-app routing** — PUBG is routed through a virtual audio cable; all other apps bypass the processor completely
- **~70 ms added latency** — imperceptible, does not affect positioning

## How it works

```
PUBG ──> virtual cable (CABLE Input) ──> this app (capture → pre-gain → EQ → compressor → limiter → soft clip) ──> headphones
every other app ──────────────────────────────────────────────────────────────────────────────────────────────────┘ direct, untouched
```

A virtual audio cable (VB-Cable, free) acts as a middle station: you point PUBG's output at it, this app picks the audio up, processes it, and plays it to your real headphones.

## Requirements

- Windows 10/11
- Python 3.9+ with `numpy`, `sounddevice`, `scipy`
- [VB-Cable](https://vb-audio.com/Cable/) (free virtual audio cable)

## Installation

1. **Install VB-Cable**: download from [vb-audio.com/Cable](https://vb-audio.com/Cable/), right-click `VBCABLE_Setup_x64.exe` → *Run as administrator* → **reboot**.
2. **Install Python packages**:
   ```
   python -m pip install numpy sounddevice scipy
   ```
3. **Run the GUI**:
   ```
   python pubg_audio_gui.py
   ```
   (or double-click `start_gui.bat`)

## Route PUBG's audio into the processor

The GUI shows a green banner when the cable is detected. Then, **with the game running and making sound**:

1. `Alt+Tab` to the desktop (leave the game open)
2. Right-click the speaker icon in the taskbar → **Open Volume mixer** (or Windows Settings → System → Sound → Volume mixer)
3. Find PUBG in the app list → set its **Output device** to **CABLE Input (VB-Audio Virtual Cable)**

Windows remembers this per-app setting. Every other app keeps using your default output.

> If a game has no sound: make sure this app is running first — PUBG pointed at the cable is silent unless the processor is active.

## Using the GUI

- **Start / Stop** — starts/stops the processing chain
- **Test sound** — plays a synthetic "footsteps + gunshot" signal through the whole chain (no need to launch the game); keep system volume at ~30% first
- **Bypass compare** — instantly switch between processed and raw audio (A/B)
- **Presets** — Light (keeps distance cues) / Balanced / Strong (night mode)
- **Live meters** — input/output level, how many dB the compressor and limiter are removing right now
- **Hover any slider** — a detailed explanation with tuning advice appears below
- **Language** — top-right dropdown: 简体中文 / English / Русский / Español / 日本語
- **Save settings** — writes `config.json` (loaded on next start)

## Command line (optional)

`python pubg_audio.py` runs the same processor without a GUI (its messages are Chinese-only). In-console commands: `g+`/`g-` (pre-gain), `t+`/`t-` (threshold), `r+`/`r-` (ratio), `b` (bypass), `s` (status), `save`, `q`. Extra flags: `--list`, `--selftest` (DSP self-test without a sound card), `--input`, `--output`, `--gain`, `--threshold`, `--ratio`.

## Parameter reference

| Parameter | Default | What it does | Tuning |
|---|---|---|---|
| Pre-gain | +3 dB | Lifts quiet sounds before processing | Noisy hiss / dull → back off 1–2 dB |
| Threshold | -18 dBFS | Loudness line where compression starts | Shots still scary → lower; distance cues blurry → raise |
| Ratio | 2.5:1 | How much of the excess is pushed back | Higher = stronger night mode, worse distance cues |
| Low cut | -8 dB | Removes the boomy "chest punch" of grenades/explosions | Still boomy → -12; sounds thin → toward 0 |
| High cut | -4 dB | Tames the "tinnitus" whine and harshness | Still piercing → -8; muffled → toward 0 |
| Limiter ceiling | -3 dBFS | Hard red line no peak may ever cross | Keep at -3; a constantly full limiter meter means compress harder instead |
| Attack / Release | 10 / 150 ms | Compressor reaction / recovery times | Leave as-is |
| Auto makeup | on | Restores loudness removed by compression | Keep on |

## FAQ

- **All system sound disappeared after installing VB-Cable** — the installer sets the cable as the system default device. Run `set_audio_default.ps1` (bundled) or manually set your headphone/mic back as default in Windows Sound settings. The GUI also warns about this.
- **Crackle / dropouts** — increase buffering: `python pubg_audio.py --target 6 --blocksize 960` (adds latency).
- **Wrong output device** — pick it in the GUI's "Playback" dropdown or `--output "name"`.
- **Is this a cheat / will I get banned?** No. The app only reads your system's audio stream and plays a processed copy — it never touches the game process, memory or network. BattlEye is not involved. It is the same class of tool as any system-wide equalizer.
- **PUBG and KRAFTON are trademarks of their respective owners.** This project is unofficial and not affiliated with them.

## Adding a language

GUI translations live in [`i18n.py`](i18n.py) — append a `STRINGS["xx_XX"]` dict (76 keys; missing keys fall back to English) and register it in `SUPPORTED`. Translations for new languages are very welcome.

## License

[MIT](LICENSE)
