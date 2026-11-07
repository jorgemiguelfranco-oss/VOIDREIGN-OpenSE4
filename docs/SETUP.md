# Installing and setting up VOIDREIGN

VOIDREIGN is a **standalone 4X space strategy game**. Its own factions, ships,
technology, facilities, economy and galaxy rules are shipped in the `game-data/`
folder beside the executable.

You do **not** need Space Empires IV Deluxe, Steam, an external data folder, or a
separate mod installation. The OpenSE4 codebase is the engine foundation; VOIDREIGN
is the game.

## Windows installation

The Windows package is a 64-bit NSIS installer for Windows 7 SP1 and later, including
Windows 10 and 11.

1. Open the [VOIDREIGN GitHub Releases page](https://github.com/jorgemiguelfranco-oss/VOIDREIGN-OpenSE4/releases).
2. Download the latest `VOIDREIGN-<version>-windows-x86_64-setup.exe` asset when a
   release is published.
3. Run the installer. It installs the game and its native `game-data/` folder under
   Program Files, creates a Start Menu shortcut, and offers an optional desktop shortcut.
4. Leave **Start VOIDREIGN** selected on the final installer page to launch the game.

The installer includes `VOIDREIGN.exe`, the complete native game data, the runtime
utilities, the SDK documentation, the licence and third-party notices. No separate
game-data download or Steam account is required.

The installer can also be built from the repository's Windows release pipeline. The
development branch is not a finished release until the Windows build, installation,
launch, native gameplay tests and uninstall checks have all passed.

## First launch

Choose **Quick Start** for a fast game or **New Game** to configure the galaxy and
empires. The native factions are:

- **Aurelian Concord** — research and sensor-focused, with a cautious defensive doctrine.
- **Veyran Trade League** — logistics and industrial development, with a balanced fleet posture.
- **Khepri Ascendancy** — industrial and military development, with a more aggressive fleet doctrine.

Each empire begins with a Pathfinder Attack Ship in its **Home Patrol** fleet. The homeworld
starts with a Spaceport, Planetary Shipyard, Supply Depot and Warehouse. Select the fleet
in the home system to inspect it and issue movement orders. Use the construction queue to
build more ships and orbital bases.

The **Orbital Station** is a native Base hull. The built-in design minister provides base
designs such as **Base Space Yard**, which can be added to a planetary shipyard's queue.
No mod is needed for the native factions, ships, AI profiles or economy.

For a silent launch, use:

```powershell
.\VOIDREIGN.exe --no-audio
```

The current native game-data package does not include a soundtrack or a bank of
sound-effects files. This does not prevent the game from being played.

## Where VOIDREIGN keeps its own files

VOIDREIGN keeps your own files outside Program Files, so an update or uninstall does
not remove your saves.

| Platform | User data folder |
|---|---|
| Windows | `%APPDATA%\\VOIDREIGN\\` (usually `C:\\Users\\<you>\\AppData\\Roaming\\VOIDREIGN\\`) |
| Linux | `$XDG_DATA_HOME/VOIDREIGN/`, or `~/.local/share/VOIDREIGN/` |
| macOS | `~/Library/Application Support/VOIDREIGN/` |

The folder contains your saved games, settings, mods, game history and logs. On Windows,
the current and previous logs are `voidreign.log` and `voidreign.previous.log`.
The game's **Settings → Files** page shows the active user folder and can open it.

The Windows uninstaller removes the installed program, shortcuts and registry entries.
It deliberately leaves `%APPDATA%\\VOIDREIGN\\` untouched.

## A portable copy

A portable copy keeps its own saved games and settings in a `userdata/` folder beside
the executable instead of using your Windows user profile. This is intended for the
ZIP package unpacked to a folder you can write to, such as a folder under Documents or
on a USB drive. A Program Files installation is not writable by a normal user and
cannot be made portable.

To make an unpacked copy portable:

1. Unpack the full VOIDREIGN ZIP. Keep `VOIDREIGN.exe` and `game-data/` together.
2. Start the game and open **Settings → Files**.
3. Enable **Keep saves and settings in VOIDREIGN's folder** and choose **Copy and Switch**.

The game creates `portable.txt` beside the executable and stores its user files in
`userdata/`. You can also create an empty `portable.txt` beside `VOIDREIGN.exe`
yourself. Delete the marker or untick the setting to return to the normal user folder;
the `userdata/` contents are not deleted.

For automated tests or a separate profile, the environment variable
`OPENSE4_USER_DIR` overrides the normal user-folder location.

## Troubleshooting

| Symptom | What to check |
|---|---|
| The game says its native data is missing | Keep the full `game-data/` folder beside `VOIDREIGN.exe`. Re-run the installer or re-extract the complete ZIP; do not copy only the executable. |
| A black window or a graphics-driver error | Update the graphics driver. From a terminal in the install folder, try `VOIDREIGN.exe --renderer=opengl`. |
| The game closes or shows a data error | Check `voidreign.log` in the user data folder. The bundled checker can validate the data with `opense4-datacheck.exe .\\game-data\\Data`. |
| Saved games or settings appear to be missing | Open **Settings → Files** and check which user folder is active. Portable copies use `userdata/` beside the executable. |
| An optional mod or AI extension fails to load | Disable it in the Mods window and restart the data load. The native VOIDREIGN factions and built-in AI do not require an extension. |

For development builds and the engine's optional compatibility with original Space Empires IV
data, saves and classic mods, see [the advanced engine compatibility guide](ENGINE-COMPATIBILITY.md).
