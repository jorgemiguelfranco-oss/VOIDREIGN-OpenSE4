# VOIDREIGN original soundtrack

These are original, procedurally synthesized science-fiction ambience cues created for
VOIDREIGN on 2026-11-09. No game soundtrack, commercial recording, samples, melodies or
external compositions were used.

## Tracks

| File | Purpose | Duration | Encoding |
|---|---|---:|---|
| VOIDREIGN_Intro.ogg | Intro / title screen | 42 s | Ogg Vorbis, stereo, 44.1 kHz |
| VOIDREIGN_Background.ogg | Exploration / empire management | 104 s | Ogg Vorbis, stereo, 44.1 kHz |
| VOIDREIGN_Combat.ogg | Tactical combat | 92 s | Ogg Vorbis, stereo, 44.1 kHz |

The score is generated from original oscillator layers, chord progressions, slow pad
envelopes, arpeggios, high glass-like tones and restrained synthesized percussion.
Each track is looped by the engine's existing music decoder and cross-faded when the
music director changes context. The three playlists are named in Data/Settings.txt.

## Reproduction

From the repository root, run:

    python tools/audio/generate_original_audio.py

The generator requires NumPy and FFmpeg with the libvorbis encoder. These are authoring
tools only; the shipped game reads the bundled OGG files and has no Python or FFmpeg
runtime dependency. The script writes temporary WAV files and removes them after encoding.
