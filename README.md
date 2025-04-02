# SnipIt - Text Replacement Tool

Text replacement utility created by Johannes Seif in 2025.

## Overview

SnipIt allows you to define text snippets that automatically expand into longer phrases, templates, or dynamic content. For example, type "ddate" and it will be replaced with the current date.

## Features

- Text snippet expansion
- Date and time substitution using special codes
- GUI for managing snippets
- Sound notifications (can be toggled)
- Input timeout (forgets partial input after 2 seconds)
- Clipboard-based replacement for better performance

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create the "Input.ini" file:
   Create the Input.ini using the "sample_input_ini.txt" template.
4. Ensure the correct directory structure:
   ```
   snipit.py
   Input.ini
   requirements.txt
   sub/
     __init__.py
     gui.py
     replace_flags.py
   ```

## Usage

1. Run the main script:
   ```
   python snipit.py
   ```

2. Type any configured snippet to see it automatically expand
3. Use the following hotkeys:
   - `Ctrl+Shift+S`: Open the settings GUI
   - `Ctrl+Shift+P`: Toggle sound notifications
   - `Ctrl+Shift+Q`: Exit the application
   - `Esc`: Reset/restart the script

## Configuration

All snippets are stored in `Input.ini` file. You can edit them directly or use the GUI.

### Special Codes for Dynamic Content

- `%dd`: Day with leading zero (01-31)
- `%d`: Day without leading zero (1-31)
- `%MM`: Month with leading zero (01-12)
- `%M`: Month without leading zero (1-12)
- `%yyyy`: Full year (e.g., 2025)
- `%yy`: Year with leading zero (00-99)
- `%y`: Last digit of year (0-9)
- `%HH`: Hour in 24h format with leading zero (00-23)
- `%H`: Hour in 24h format without leading zero (0-23)
- `%hh`: Hour in 12h format with leading zero (01-12)
- `%h`: Hour in 12h format without leading zero (1-12)
- `%mm`: Minutes with leading zero (00-59)
- `%m`: Minutes without leading zero (0-59)
- `%ss`: Seconds with leading zero (00-59)
- `%s`: Seconds without leading zero (0-59)

### Special Formatting

- `{n}`: Inserts a newline (without sending Enter key)

## Notes

- The keyboard module requires root/admin privileges on some systems (e.g. MacOS)
- The app has been tested on Windows 11
- Input timeout: if you type part of a snippet but stop for 2 seconds, the input buffer will be cleared
