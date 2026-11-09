# VOIDREIGN original sound effects

The 18 sound effects in this folder were procedurally synthesized on 2026-11-09 for
VOIDREIGN. No recordings, samples or effects from the original Space Empires series or
other games were used.

The generated mono PCM WAV cues cover the current engine's built-in effect names:
button, cmdbtn, ordbtn, close, endturn, cloakon, cloakoff, openwp, closewp, crtestrm,
deststrm, crteplnt, destplnt, crtesun, destsun, boom1, boom2 and boom3.

The effects use synthesized oscillators, pitch sweeps, decaying envelopes and generated
noise. They are loaded through the engine's existing Sounds/ fallback path, whether the
player selects classic or remastered effects. Runtime requires only the WAV files.

## Reproduction

From the repository root, run:

    python tools/audio/generate_original_audio.py

The generator requires NumPy. It is a build-time authoring tool; FFmpeg is used only to
encode the three OGG music tracks. No additional engine library is introduced.
