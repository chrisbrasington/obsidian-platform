# Game Platform Metadata Setter

This Python script iterates through markdown game files in your Obsidian vault and helps you set the `platform` metadata field if it is missing.

## Features

- Scans all markdown files in the configured directory.
- Skips files with `dataSource: SteamAPI` (assumed PC games).
- Maintains a dynamic list of platforms with numeric shortcuts.
- Allows input of new platforms or selection from existing ones.
- Automatically adds any detected platform not in the list.
- Supports quitting anytime by typing `q` or `quit`.
- Updates markdown frontmatter in-place.

## Setup

1. Make sure you have Python 3 installed.
2. Install required dependencies:
    ```bash
    pip install pyyaml
    ```

3. Configure your vault path in `config.json`.
4. Run the script:

   ```bash
   python platform_setter.py
   ```

## Usage

* The script will print each file being processed.
* If a file needs a platform, it will show the list of known platforms with numbers.
* You can type:

  * A platform number to select an existing platform.
  * A new platform name to add it.
  * `q` or `quit` to exit the program.

## Example

```
Known platforms:
1. GC
2. PS2
Enter platform number, new platform name, or 'q' to quit: 1
Platform 'GC' set for Resident Evil 4.md
```
