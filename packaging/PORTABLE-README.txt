VOIDREIGN: making this copy portable
====================================

VOIDREIGN keeps your saved games, settings, logs, mods and game history in your user folder:

  Windows   %APPDATA%\VOIDREIGN
  Linux     ~/.local/share/VOIDREIGN ($XDG_DATA_HOME/VOIDREIGN when that is set)
  macOS     ~/Library/Application Support/VOIDREIGN

A portable copy keeps them in the folder "userdata" beside its program instead, so that
they go wherever the program folder goes: a USB stick or several copies side by side.
This copy is not portable until you enable it in either of two ways:

  - Start VOIDREIGN, open Settings (top right on the title screen, or Ctrl+Comma in a
    game), choose Files and tick "Keep saves and settings in VOIDREIGN's folder".
    VOIDREIGN offers to copy saved games and settings; it never deletes or overwrites
    the originals.
  - Or create an empty text file named portable.txt beside VOIDREIGN.exe (Windows) or
    VOIDREIGN (Linux).

To use your normal user folder again, untick the setting or delete portable.txt.
Files already in userdata stay where they are.

The program folder must be writable. Extract a portable archive into a folder you
control, not Program Files. An installation made with the Windows installer cannot
be portable.

The environment variable VOIDREIGN_USER_DIR overrides the default location. The old
OPENSE4_USER_DIR variable is still accepted as a compatibility fallback.
See docs/SETUP.md for installation, data, saves and troubleshooting.
