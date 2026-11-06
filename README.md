# EverDrive X7 Autoboot OS

A quiet autoboot for the **Sega Game Gear EverDrive X7**. It loads a Game Gear ROM directly from the SD card without opening the file browser or displaying the AB2 diagnostic messages.

## Download and install

Download [**EverDrive-X7-Autoboot-OS.zip**](https://github.com/drhegdedarshan-spec/everdrive-x7-autoboot-os/raw/refs/heads/main/downloads/EverDrive-X7-Autoboot-OS.zip). The ZIP contains the correct filename and folder structure:

```text
EverDrive-X7-Autoboot-OS.zip
├── README.md
└── SMSSYS/
    └── SMSOS.BIN
```

1. Back up your current `SMSSYS/SMSOS.BIN` and save files.
2. Extract the ZIP onto your **FAT32** SD card. Merge the `SMSSYS` folder and replace `SMSOS.BIN`; preserve the other files already in `SMSSYS`.
3. Put one **uncompressed `.gg` ROM** directly in the root of the SD card. Keep the game's original filename.
4. Eject the SD card properly, insert it into the X7, and power on.

Your SD card should look like this:

```text
SD card root/
├── Sonic the Hedgehog.gg    # Your game; no ROM is included
└── SMSSYS/
    ├── SMSOS.BIN            # Keep this exact filename
    └── ...                  # Existing system and save files
```

**Do not rename the OS file to the project name.** The cartridge expects `SMSSYS/SMSOS.BIN`. There is no extra project folder between the SD card root and `SMSSYS`.

If you use GitHub's **Download ZIP** source archive instead of the release ZIP, copy the `SMSSYS` folder from inside the extracted repository folder to the SD card root.

## Changing games

Remove the previous `.gg` file from the SD card root and copy in the new game. You **do not** need to rename games to `BOOT.GG`.

If more than one `.gg` file is present, the first match in **SD directory order** is loaded. This may differ from alphabetical order. Keeping one game in the root makes selection predictable.

## Behavior

- Searches the SD card root for a regular `.gg` file, with case-insensitive extension matching (`.gg`, `.GG`, etc.).
- Supports short FAT names and long filenames; skips directories and dot files.
- Does not search subfolders.
- Shows no AB2 messages, normal OS progress text, or game-selection menu.
- Disables the in-game menu while retaining the original mapper, loading, and save machinery.
- Preserves the selected game's filename for save-file naming; padded short names are converted to the usual dotted form.
- Retains stock error and initialization-warning screens when a problem occurs.

The cartridge's own early **OS loading** screen may appear briefly before this OS takes control. This SD-card OS modification does not change the cartridge's built-in bootloader.

## Compatibility and validation

This is the **quiet v3 build**, based on the v2 diagnostic build reported working by the user. V3 has passed Z80 CPU tests but has not yet been confirmed on an X7 in this thread.

Tests cover filename matching, startup control flow, failure paths, actual stock FAT directory traversal and descriptor decoding, long filenames crossing cluster boundaries, and games appearing beyond directory entry 128. Sector reads and cartridge-specific selection/loading boundaries are mocked, so these checks do not validate full hardware behavior.

The original OS limit of **1,024 indexed root entries** remains. This modification targets the **Game Gear EverDrive X7** and is based on the exact SMSOS v1.04 binary supplied for this project.

## Recovery

Restore the original `SMSSYS/SMSOS.BIN'

## Rebuild the patch

Python 3 is required; no third-party packages are needed.

```sh
python3 tools/build_patch.py path/to/original/SMSOS.BIN SMSSYS/SMSOS.BIN
```

The script refuses inputs that do not match the expected stock binary.

| File | SHA-256 |
| --- | --- |
| Original SMSOS v1.04 | `c261956de0ff81132b780abe706d7080c4a9e847a44c796f110a54247bfe53cd` |
| Patched `SMSSYS/SMSOS.BIN` | `6132fea35e324187b0f449172ec0339373d4cdd5aae94f107054135b71d7417f` |

## Attribution

This is an unofficial modification of **Krikzz's SMSOS v1.04**, made from the supplied OS archive. The original OS and EverDrive hardware are Krikzz's work. This project is not an official Krikzz release. No game ROMs are included.
