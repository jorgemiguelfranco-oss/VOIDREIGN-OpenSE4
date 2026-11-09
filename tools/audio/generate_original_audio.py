from __future__ import annotations

"""Generate original VOIDREIGN ambient music and synthetic game effects.

No samples or third-party compositions are used. Music is synthesized from oscillators,
envelopes and deterministic note sequences, then encoded as Ogg Vorbis with FFmpeg.
Effects are synthesized as short PCM WAV files. Runtime requires only the bundled files.
"""

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MUSIC_DIR = ROOT / "game-data" / "Music"
SOUNDS_DIR = ROOT / "game-data" / "Sounds"
SAMPLE_RATE = 44100
CHUNK = 131072
TAU = 2.0 * math.pi

# MIDI note progressions: open fifths, suspended seconds and minor sevenths give
# the score its own restrained, exploratory VOIDREIGN identity.
PROGRESSIONS = {
    "intro": [(38, 45, 50, 52), (34, 41, 46, 50), (41, 48, 53, 55), (36, 43, 48, 50)],
    "background": [(38, 45, 50, 53), (43, 50, 53, 57), (34, 41, 46, 50), (36, 43, 48, 52)],
    "combat": [(38, 45, 50, 53), (34, 41, 46, 50), (41, 48, 53, 56), (33, 40, 45, 49)],
}
TRACKS = {
    "intro": ("VOIDREIGN_Intro.ogg", 72.0, 42.0, 0x101),
    "background": ("VOIDREIGN_Background.ogg", 78.0, 104.0, 0x202),
    "combat": ("VOIDREIGN_Combat.ogg", 112.0, 92.0, 0x303),
}


def midi_hz(note: np.ndarray | float) -> np.ndarray:
    return 440.0 * np.power(2.0, (np.asarray(note, dtype=np.float64) - 69.0) / 12.0)


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def write_pcm16(path: Path, data: np.ndarray, rate: int, channels: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(data))) if data.size else 0.0
    if peak > 0:
        data = data / max(1.0, peak / 0.94)
    encoded = np.clip(data * 32767.0, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(encoded.tobytes())


def render_music(kind: str, wav_path: Path) -> None:
    filename, bpm, duration, seed = TRACKS[kind]
    progression = PROGRESSIONS[kind]
    total = int(SAMPLE_RATE * duration)
    beat = 60.0 / bpm
    chord_duration = beat * (8.0 if kind != "combat" else 4.0)
    transition = min(2.8, chord_duration * 0.34)
    step_duration = beat * 0.5
    rng = np.random.default_rng(seed)

    with wave.open(str(wav_path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        for start in range(0, total, CHUNK):
            count = min(CHUNK, total - start)
            t = (start + np.arange(count, dtype=np.float64)) / SAMPLE_RATE
            chord_position = np.floor(t / chord_duration).astype(np.int64)
            # Use the same integer step for position and phase. np.mod can round
            # an exact boundary to zero while floor(t / duration) rounds it down.
            chord_age = t - chord_position * chord_duration
            chord_index = chord_position % len(progression)
            previous_index = (chord_index - 1) % len(progression)
            blend = smoothstep(chord_age / transition)
            previous_weight = 1.0 - blend
            current_weight = blend

            left = np.zeros(count, dtype=np.float64)
            right = np.zeros(count, dtype=np.float64)

            # Slowly moving, detuned pad. Each chord crossfades rather than cutting.
            for voice in range(4):
                current_note = np.array([progression[i][voice] for i in chord_index], dtype=np.float64)
                previous_note = np.array([progression[i][voice] for i in previous_index], dtype=np.float64)
                f_now = midi_hz(current_note)
                f_old = midi_hz(previous_note)
                phase_mod = 0.10 * np.sin(TAU * t * (0.035 + voice * 0.004))
                now = np.sin(TAU * f_now * t + phase_mod + voice * 0.71)
                now += 0.22 * np.sin(TAU * (f_now * 2.003) * t + voice * 0.2)
                old = np.sin(TAU * f_old * t + phase_mod + voice * 0.71)
                old += 0.22 * np.sin(TAU * (f_old * 2.003) * t + voice * 0.2)
                layer = now * current_weight + old * previous_weight
                amount = 0.105 if kind == "intro" else 0.090
                if kind == "combat":
                    amount = 0.078
                pan = -0.62 + voice * 0.41
                left += layer * amount * math.sqrt((1.0 - pan) * 0.5)
                right += layer * amount * math.sqrt((1.0 + pan) * 0.5)

            # Deep root drone with a gentle breathing pulse.
            root_now = np.array([progression[i][0] for i in chord_index], dtype=np.float64) - 12.0
            root_old = np.array([progression[i][0] for i in previous_index], dtype=np.float64) - 12.0
            sub = np.sin(TAU * midi_hz(root_now) * t) * current_weight
            sub += np.sin(TAU * midi_hz(root_old) * t) * previous_weight
            breathing = 0.78 + 0.22 * np.sin(TAU * t / (7.0 if kind != "combat" else 3.5))
            sub *= breathing
            left += sub * 0.17
            right += sub * 0.17

            # A restrained eighth-note arpeggio, with longer tails on the title music.
            step_index = np.floor(t / step_duration).astype(np.int64)
            step_age = t - step_index * step_duration
            pattern = np.array([0, 2, 1, 3, 2, 1, 3, 2], dtype=np.int64)
            selected = np.array(
                [progression[i][0] for i in chord_index], dtype=np.float64
            )
            # The pattern is voiced from chord intervals, not from a fixed melody.
            chord_array = np.asarray(progression, dtype=np.float64)
            selected = chord_array[chord_index, pattern[step_index % len(pattern)]]
            selected += np.where((step_index % 4) == 3, 12.0, 0.0)
            arp_freq = midi_hz(selected)
            # Fade the arpeggio in and out within each step. A sharp note
            # reset can create a click when the pattern cycles on a chord change.
            arp_env = np.exp(-step_age / (step_duration * (0.72 if kind == "intro" else 0.53)))
            arp_env *= smoothstep(step_age / 0.035)
            arp_env *= smoothstep((step_duration - step_age) / 0.035)
            arp = np.sin(TAU * arp_freq * t) + 0.28 * np.sin(TAU * arp_freq * 2.01 * t)
            arp_level = 0.070 if kind == "intro" else (0.048 if kind == "background" else 0.062)
            pan = np.sin(TAU * t / 19.0) * 0.32
            left += arp * arp_env * arp_level * np.sqrt((1.0 - pan) * 0.5)
            right += arp * arp_env * arp_level * np.sqrt((1.0 + pan) * 0.5)

            # Occasional high glass tones mark phrase boundaries.
            bell_period = beat * (8.0 if kind != "combat" else 4.0)
            bell_index = np.floor(t / bell_period).astype(np.int64)
            bell_age = t - bell_index * bell_period
            bell_chords = np.asarray(progression, dtype=np.float64)
            bell_note = bell_chords[chord_index, (bell_index + 2) % 4] + 24.0
            bell_freq = midi_hz(bell_note)
            bell_env = np.exp(-bell_age * 1.45) * smoothstep(bell_age / 0.01)
            bell = np.sin(TAU * bell_freq * t) + 0.37 * np.sin(TAU * bell_freq * 2.76 * t)
            bell_gain = 0.032 if kind != "combat" else 0.020
            left += bell * bell_env * bell_gain
            right += bell * bell_env * bell_gain

            # Combat gets a low, soft pulse and brushed metallic noise; the other
            # playlists stay spacious and percussion-light.
            if kind == "combat":
                kick_index = np.floor(t / beat).astype(np.int64)
                kick_age = t - kick_index * beat
                kick_env = np.exp(-kick_age * 11.0)
                kick_phase = TAU * (47.0 * kick_age + 3.2 * (1.0 - np.exp(-kick_age * 15.0)))
                kick = np.sin(kick_phase) * kick_env
                noise = rng.standard_normal(count)
                noise = noise - np.roll(noise, 1)
                hat_period = beat * 0.5
                hat_index = np.floor(t / hat_period).astype(np.int64)
                hat_age = t - hat_index * hat_period
                hat_env = np.exp(-hat_age * 39.0)
                hat = noise * hat_env * 0.010
                pulse = kick * 0.14
                left += pulse + hat
                right += pulse + hat
            elif kind == "background":
                pulse_index = np.floor(t / (beat * 2.0)).astype(np.int64)
                pulse_age = t - pulse_index * beat * 2.0
                pulse = np.sin(TAU * 54.0 * pulse_age) * np.exp(-pulse_age * 8.5) * 0.025
                left += pulse
                right += pulse

            # Gentle fade at each end avoids a hard loop boundary on first play.
            fade_in = smoothstep(t / 2.4)
            fade_out = smoothstep((duration - t) / 3.0)
            fade = fade_in * fade_out
            left *= fade
            right *= fade

            # Keep the score dynamic without clipping and add a little stereo width.
            mixed = np.column_stack((left, right))
            mixed = np.tanh(mixed * 1.35) / np.tanh(1.35)
            encoded = np.clip(mixed * 0.82 * 32767.0, -32768, 32767).astype("<i2")
            wav.writeframes(encoded.tobytes())

    print(f"Rendered {kind}: {filename} ({duration:.0f} s)")
    return filename


def render_effect(name: str, path: Path) -> None:
    # name: (duration, start Hz, end Hz, noise mix, decay, extra harmonic)
    specs = {
        "button":    (0.13, 920, 650, 0.01, 18, 2.00),
        "cmdbtn":    (0.20, 560, 980, 0.02, 12, 2.00),
        "ordbtn":    (0.18, 1080, 760, 0.04, 15, 2.60),
        "close":     (0.24, 390, 170, 0.12, 13, 1.51),
        "endturn":   (0.95, 330, 165, 0.10, 3.5, 2.76),
        "cloakon":   (0.72, 210, 1380, 0.16, 4.5, 2.01),
        "cloakoff":  (0.72, 1380, 210, 0.16, 4.5, 2.01),
        "openwp":    (1.10, 90, 1450, 0.28, 3.2, 3.02),
        "closewp":   (1.00, 1450, 70, 0.30, 3.8, 2.48),
        "crtestrm":  (0.96, 75, 570, 0.40, 4.0, 2.12),
        "deststrm":  (0.96, 620, 65, 0.44, 4.0, 2.12),
        "crteplnt":  (1.10, 110, 790, 0.10, 3.0, 2.48),
        "destplnt":  (1.16, 780, 48, 0.27, 3.2, 1.51),
        "crtesun":   (1.15, 100, 1180, 0.13, 2.8, 3.01),
        "destsun":   (1.30, 1400, 38, 0.35, 2.9, 2.48),
        "boom1":     (0.52, 115, 35, 0.44, 8.5, 2.06),
        "boom2":     (0.75, 145, 27, 0.52, 5.0, 2.31),
        "boom3":     (0.98, 170, 22, 0.60, 3.8, 2.73),
    }
    duration, start_hz, end_hz, noise_mix, decay, harmonic = specs[name]
    rate = 22050
    count = int(duration * rate)
    t = np.arange(count, dtype=np.float64) / rate
    ratio = math.log(max(1.0, end_hz) / max(1.0, start_hz))
    frequency = start_hz * np.exp(ratio * np.clip(t / duration, 0.0, 1.0))
    phase = TAU * np.cumsum(frequency) / rate
    tone = np.sin(phase) + 0.24 * np.sin(phase * harmonic)
    rng = np.random.default_rng(0x5EED + sum(ord(c) for c in name))
    raw = rng.standard_normal(count)
    bright_noise = raw - np.concatenate(([raw[0]], raw[:-1]))
    env = np.exp(-t * decay) * smoothstep(t / 0.012)
    # Effects can be replaced by the next UI/combat cue; give their natural
    # endings a soft 50 ms release as well as the mixer's replacement fade.
    env *= smoothstep((duration - t) / 0.050)
    if name in ("button", "cmdbtn", "ordbtn"):
        # Crisp electronic UI signals, with eased edges so a pulse never clicks.
        if name == "cmdbtn":
            first = smoothstep(t / 0.006) * (1.0 - smoothstep((t - 0.067) / 0.008))
            second = 0.55 * smoothstep((t - 0.105) / 0.006) * (1.0 - smoothstep((t - 0.167) / 0.008))
            gate = np.maximum(first, second)
        elif name == "ordbtn":
            first = smoothstep(t / 0.006) * (1.0 - smoothstep((t - 0.047) / 0.008))
            second = 0.65 * smoothstep((t - 0.085) / 0.006) * (1.0 - smoothstep((t - 0.127) / 0.008))
            gate = np.maximum(first, second)
        else:
            gate = np.ones(count)
        env *= gate
    if name.startswith("boom") or name in ("destplnt", "destsun", "deststrm"):
        impact = np.exp(-t * (9.0 if name == "boom1" else 5.0))
        tone *= impact
    else:
        impact = 1.0
    signal = tone * env + bright_noise * env * noise_mix
    if name in ("openwp", "closewp", "crtestrm", "deststrm", "cloakon", "cloakoff"):
        shimmer = np.sin(TAU * (frequency * 2.73) * t) * np.exp(-t * 2.6)
        signal += shimmer * 0.10
    if name == "endturn":
        signal += 0.16 * np.sin(TAU * (start_hz * 1.498) * t) * np.exp(-t * 2.4)
    # A short terminal ramp prevents a hard edge when the one-shot ends.
    signal *= smoothstep((duration - t) / 0.018)
    signal = np.tanh(signal * 1.6) / np.tanh(1.6)
    # Effects often overlap the music bed. Leave ample headroom instead of
    # normalising each one-shot close to full scale.
    signal *= 0.42
    write_pcm16(path, signal, rate, 1)
    print(f"Rendered effect: {name}.wav ({duration:.2f} s)")


def encode_ogg(wav_path: Path, output_path: Path, ffmpeg: str) -> None:
    subprocess.run(
        [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav_path),
         "-c:a", "libvorbis", "-q:a", "4", "-ar", str(SAMPLE_RATE), "-ac", "2", str(output_path)],
        check=True,
    )
    if output_path.stat().st_size < 4096:
        raise RuntimeError(f"Encoded music file is unexpectedly small: {output_path}")
    print(f"Encoded {output_path.name}: {output_path.stat().st_size:,} bytes")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", default=r"C:\Program Files\Shotcut\ffmpeg.exe")
    args = parser.parse_args()
    if not Path(args.ffmpeg).is_file():
        raise SystemExit(f"FFmpeg not found: {args.ffmpeg}")

    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voidreign-audio-") as temporary:
        temporary_dir = Path(temporary)
        for kind in ("intro", "background", "combat"):
            filename, _, _, _ = TRACKS[kind]
            source_wav = temporary_dir / f"{kind}.wav"
            render_music(kind, source_wav)
            encode_ogg(source_wav, MUSIC_DIR / filename, args.ffmpeg)

    effects = (
        "button", "cmdbtn", "ordbtn", "close", "endturn",
        "cloakon", "cloakoff", "openwp", "closewp",
        "crtestrm", "deststrm", "crteplnt", "destplnt",
        "crtesun", "destsun", "boom1", "boom2", "boom3",
    )
    for name in effects:
        render_effect(name, SOUNDS_DIR / f"{name}.wav")

    def record(path: Path, kind: str, duration: float, sample_rate: int, channels: int, encoding: str) -> dict:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {
            "file": path.relative_to(ROOT).as_posix(),
            "type": kind,
            "duration_seconds": duration,
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "encoding": encoding,
            "bytes": path.stat().st_size,
            "sha256": digest,
        }

    tracks = []
    for kind, (filename, _bpm, duration, _seed) in TRACKS.items():
        tracks.append(record(MUSIC_DIR / filename, "music", duration, SAMPLE_RATE, 2, "Ogg Vorbis"))
    sound_records = []
    for name in effects:
        duration = {
            "button": 0.13, "cmdbtn": 0.20, "ordbtn": 0.18, "close": 0.24,
            "endturn": 0.95, "cloakon": 0.72, "cloakoff": 0.72, "openwp": 1.10,
            "closewp": 1.00, "crtestrm": 0.96, "deststrm": 0.96, "crteplnt": 1.10,
            "destplnt": 1.16, "crtesun": 1.15, "destsun": 1.30,
            "boom1": 0.52, "boom2": 0.75, "boom3": 0.98,
        }[name]
        sound_records.append(record(SOUNDS_DIR / f"{name}.wav", "sound-effect", duration, 22050, 1, "PCM signed 16-bit"))
    manifest = {
        "title": "VOIDREIGN original procedural audio",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/audio/generate_original_audio.py",
        "method": "Procedural oscillator, envelope and deterministic noise synthesis; no external recordings, samples or compositions.",
        "runtime_dependencies": [],
        "music": tracks,
        "sound_effects": sound_records,
    }
    manifest_path = ROOT / "game-data" / "AUDIO-MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(TRACKS)} original music tracks and {len(effects)} original sound effects.")
    print(f"Wrote SHA-256 and audio-format manifest: {manifest_path.relative_to(ROOT)}")
    print("No external samples, borrowed tracks or engine runtime dependencies were added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
