# Building VOIDREIGN

VOIDREIGN is a native C++23 game based on the OpenSE4 engine. The repository is the source of truth; the game data is generated during the build and bundled next to the client.

## Requirements

- C++23 compiler: GCC 14+, Clang 18+, Visual Studio 2022 17.10+ / Visual Studio 2026, or Apple Clang 21.
- CMake 3.25+ and Ninja.
- SDL3 3.2+ (CMake uses a system copy or fetches the pinned dependency).
- `glslc` and Vulkan headers for shader compilation.
- Network access for the first configure, to fetch pinned dependencies.

## Linux

Install a compiler, CMake, Ninja, SDL3 development headers, Vulkan headers and `glslc`. Then run:

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
./build/debug/VOIDREIGN --quick-start=Aurel
```

To exercise the game without opening a visible window:

```sh
SDL_VIDEO_DRIVER=offscreen ./build/debug/VOIDREIGN --quick-start=Aurel --turns=3 --open=none --screenshot=/tmp/voidreign.png
```

The run should create a non-empty screenshot. This is also the game-start smoke test configured in the repository's Linux CI job.

## Windows

Install Visual Studio with **Desktop development with C++** and the Vulkan SDK. From an x64 Native Tools Command Prompt:

```bat
cmake --preset release
cmake --build --preset release
build\release\VOIDREIGN.exe
```

The distributable Windows installer is built by the repository's release packaging workflow. It includes the game data folder and the standalone VOIDREIGN executable.

## macOS

Install Xcode Command Line Tools, CMake, Ninja, SDL3, shaderc and Vulkan headers. Configure and build with the committed `debug` preset, then run `ctest --preset debug`. Use `--renderer=opengl` if the Vulkan/MoltenVK path is not configured.

## Generated game data

`tools/generate_voidreign_data.py` creates the standalone ruleset in the build's generated-data directory. CMake stages that output as `GameData` beside the client. The game is expected to start from that bundled data without looking for an external Space Empires IV installation.

The internal CMake target is still named `opense4` because this is the native OpenSE4 engine codebase; its produced player-facing executable is `VOIDREIGN` (or `VOIDREIGN.exe`).

The upstream engine's detailed development and clean-room notes are preserved in `OPENSE4-BUILDING.md`.
