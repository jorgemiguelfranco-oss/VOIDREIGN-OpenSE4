VOIDREIGN: making this copy portable
====================================

VOIDREIGN keeps your saved games, settings, mods, game history and logs in your user
folder:

  Windows   %APPDATA%\VOIDREIGN
  Linux     ~/.local/share/VOIDREIGN  ($XDG_DATA_HOME/VOIDREIGN when set)
  macOS     ~/Library/Application Support/VOIDREIGN

A portable copy keeps those files in the folder "userdata" beside the program instead,
so they travel with this copy of VOIDREIGN (for example on a USB drive or between
computers). This ZIP copy is not portable until you enable it in either of these ways:

  - Start VOIDREIGN.exe, open Settings (top right of the title screen, or Ctrl+Comma
    in a game), choose the Files page and enable "Keep saves and settings in
    VOIDREIGN's folder". Choose "Copy and Switch" to copy your existing saves and
    settings into userdata. The original files are not deleted.
  - Or create an empty text file named portable.txt in this folder, beside
    VOIDREIGN.exe. In Windows Explorer with file-name extensions hidden, name the
    new text document "portable".

Keep game-data\ beside VOIDREIGN.exe; portable mode changes only the location of
your personal files. Do not move or rename game-data\.

To use your normal user folder again, turn off the setting or delete portable.txt.
The files already in userdata stay where they are.

This folder must be writable. Unpack the ZIP into a folder of your own, not into
Program Files. A copy installed with the Windows setup program cannot be portable
because a standard user cannot write beside the installed executable.

The Files page shows the folder currently in use and can choose a separate saves
folder. The environment variable OPENSE4_USER_DIR overrides the normal user-folder
location when set. Uninstalling VOIDREIGN leaves the normal user folder (%APPDATA%\VOIDREIGN)
alone. See docs/SETUP.md for the standalone installation and troubleshooting guide.
