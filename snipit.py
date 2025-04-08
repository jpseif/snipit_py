#!/usr/bin/env python3
"""
SnipIt - Text replacement tool
"""

import os
import sys
import time
import configparser
import keyboard
import datetime
import re
import threading
import json
import pyperclip
from pathlib import Path
import traceback

# Import helper modules
from sub.replace_flags import replace_flags
from sub.gui import setup_gui

# Initialize variables
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "Input.ini")
list_file = os.path.join(script_dir, "List.txt")

# Initialize arrays
key_array = []
log = ""
sound_setting = 0
last_key_time = time.time()
input_timeout = 2.0  # 2 seconds timeout for keyboard input
debugging = True  # Set to True to enable debug messages
version = "v1.0.3c"
ctrl_pressed = False
alt_pressed = False
shift_pressed = False

# Initialize lock for thread safety
log_lock = threading.Lock()

def read_ini_file():
    """Read the Input.ini file and load snippets into key_array"""
    global key_array, sound_setting
    
    try:
        # Read the sound setting - disable interpolation to handle % characters
        config = configparser.ConfigParser(interpolation=None)
        
        # Check if the file exists
        if not os.path.exists(input_file):
            create_default_ini()
        
        # Read the file with utf-8 encoding to properly handle special characters
        with open(input_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
        
        # Check if required sections exist
        if "Strings" not in config:
            config["Strings"] = {}
        if "Settings" not in config:
            config["Settings"] = {"SoundSetting": "0"}
            with open(input_file, 'w', encoding='utf-8') as f:
                config.write(f)
        
        sound_setting = int(config.get("Settings", "SoundSetting", fallback="0"))
        
        # Delete the list txt file if it exists
        if os.path.exists(list_file):
            try:
                os.remove(list_file)
            except:
                pass  # Ignore if file can't be deleted
        
        # Get snippets from the config
        snippets = []
        for key in config["Strings"]:
            snippets.append(key)
        
        # Sort snippets by length in descending order so longer snippets are checked first
        snippets.sort(key=len, reverse=True)
        
        # Store in global key_array
        key_array = snippets
        
        # Write snippets to list file for reference (optional)
        with open(list_file, 'w', encoding='utf-8') as f:
            for key in snippets:
                f.write(key + "\n")
        
        # Hide list file (not perfect equivalent, just make it hidden on Windows)
        try:
            if os.name == 'nt':
                os.system(f'attrib +h "{list_file}"')
        except:
            pass  # Just continue if we can't hide the file
            
        if debugging:
            print("Loaded snippets:", key_array)
            
    except Exception as e:
        print(f"Error reading Input.ini: {e}")
        traceback.print_exc()
        # Create a default ini file in case of error
        create_default_ini()
        key_array = ["ttime", "ddate"]  # Fallback to basic snippets

def create_default_ini():
    """Create a default Input.ini file"""
    config = configparser.ConfigParser(interpolation=None)
    config["Strings"] = {
        "ttime": "%HH%mm%ss_",
        "ddate": "%yy%MM%dd_",
        "date2": "%dd.%MM.%yyyy",
        "ddd": "%yyyy-%MM-%dd_",
        "bbb": "Best regards.{n}John Doe",
        "kkind": "Kind regards.{n}John Doe"
    }
    config["Settings"] = {"SoundSetting": "0"}
    
    with open(input_file, 'w', encoding='utf-8') as f:
        config.write(f)

    if debugging:
        print("Default Input.ini created.")

def play_sound():
    """Play a system beep sound if sound_setting is enabled"""
    if sound_setting == 1:
        try:
            import winsound
            winsound.MessageBeep()
        except:
            # Fallback for non-Windows systems
            print('\a')  # Terminal bell

def check_timeout():
    """Check if enough time has passed to reset the input log"""
    global log, last_key_time, log_lock
    
    while True:
        try:
            current_time = time.time()
            with log_lock:
                if log and (current_time - last_key_time) > input_timeout:
                    if log and debugging:
                        print(f"Input buffer cleared (timeout) - [{datetime.datetime.now().strftime('%H:%M:%S')}]")
                    log = ""
            # Check every 100ms
            time.sleep(0.1)
        except Exception as e:
            if debugging:
                print(f"Error in timeout thread: {e}")
            # Continue checking even if an error occurs
            time.sleep(0.1)

        if debugging:
            print("timeout")

def get_replacement(snippet):
    """Get the replacement text for a snippet from the config file"""
    try:
        config = configparser.ConfigParser(interpolation=None)
        with open(input_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
        
        if "Strings" in config and snippet in config["Strings"]:
            return config["Strings"][snippet]
        if debugging:
            print("get replacement")
        return None
    except Exception as e:
        print(f"Error getting replacement for '{snippet}': {e}")
        return None

def check_for_snippets():
    """Check if the current input buffer contains any snippet"""
    global log, log_lock

    with log_lock:
        current_log = log

    # Clean the log by removing any control characters or invisible space
    clean_log = current_log.strip()

    # Print current buffer for debugging
    if debugging:
        print(f"Current buffer: '{clean_log}'")

    # Check each snippet
    for snippet in key_array:
        # Check if the snippet is in the buffer
        # Try both exact matching and checking if it's at the end of the buffer
        if snippet == clean_log or clean_log.endswith(snippet):
            return snippet

    return None

# def check_for_snippets():
#     """Check if the current input buffer ends with any snippet preceded by word boundary"""
#     global log, log_lock
#
#     with log_lock:
#         current_log = log
#
#     # Print current buffer for debugging
#     if debugging:
#         print(f"Current buffer: '{current_log}'")
#
#     # Define word delimiters - characters that would appear before a snippet
#     # when it's intentionally typed as a standalone entity
#     delimiters = [' ', '\t', '\n', '', ';', '.', ',', '!', '?', '-', '_', '(', ')', '[', ']', '{', '}']
#
#     # Check each snippet
#     for snippet in key_array:
#         # Only replace if the snippet is at the end of the buffer
#         if current_log.endswith(snippet):
#             # Determine what character comes before the snippet
#             prefix_position = len(current_log) - len(snippet) - 1
#
#             # If snippet is at the beginning of the buffer or preceded by a delimiter
#             if prefix_position < 0 or (prefix_position >= 0 and current_log[prefix_position] in delimiters):
#                 if debugging:
#                     print(f"Found valid snippet: '{snippet}' at end of buffer")
#                 return snippet
#             else:
#                 # This is a partial match (snippet within a word), don't expand
#                 if debugging:
#                     print(f"Ignored snippet '{snippet}' within a word")
#
#     return None

# def update_modifier_state(key, is_pressed):
#     """Update the state of modifier keys"""
#     global ctrl_pressed, alt_pressed, shift_pressed
#
#     if key == 'ctrl':
#         ctrl_pressed = is_pressed
#     elif key == 'alt':
#         alt_pressed = is_pressed
#     elif key == 'shift':
#         shift_pressed = is_pressed

def process_key(key):
    """Process each keystroke and check for snippet matches"""
    global log, last_key_time, log_lock  #, ctrl_pressed, alt_pressed
    
    try:
        # Update the last key time
        last_key_time = time.time()

        # Skip processing if Ctrl or Alt is pressed
        # if ctrl_pressed or alt_pressed:
        #     return
        
        # Filter out special keys that should not be part of snippets
        if len(key) > 1 and key not in ['space', 'backspace', 'tab']:
            return
        
        # Convert special keys to their character representation
        if key == 'space':
            key = ' '
        elif key == 'tab':
            key = '\t'
        elif key == 'backspace' and log:
            with log_lock:
                log = log[:-1]  # Remove last character
                if debugging:
                    print(f"Backspace pressed, new log: '{log}'")
            return
        
        # Add the key to the log
        with log_lock:
            log += key
            if debugging:
                print(f"Key pressed: '{key}', current log: '{log}'")
        
        # Check for any snippet matches
        snippet = check_for_snippets()
        if snippet:
            # Get the replacement value
            replacement = get_replacement(snippet)
            
            if replacement:
                # Print confirmation to terminal
                if debugging:
                    print(f"Replacing '{snippet}' - [{datetime.datetime.now().strftime('%H:%M:%S')}]")
                
                try:
                    # Replace flags in the replacement text
                    replacement = replace_flags(replacement)
                    
                    # Save the current clipboard content
                    try:
                        original_clipboard = pyperclip.paste()
                    except:
                        original_clipboard = ""
                    
                    # Handle multi-line replacement by converting {n} to actual newlines
                    if isinstance(replacement, list):
                        replacement = "\n".join(replacement)
                    else:
                        replacement = replacement.replace("{n}", "\n")
                    
                    # Copy the replacement to clipboard
                    pyperclip.copy(replacement)
                    
                    # Calculate how much to delete - we delete the whole snippet
                    delete_count = len(snippet)
                    for _ in range(delete_count):
                        keyboard.press_and_release('backspace')
                    
                    # Small delay to ensure backspaces are processed
                    time.sleep(0.05)
                    
                    # Paste the replacement
                    keyboard.press_and_release('ctrl+v')
                    
                    # Restore original clipboard after a short delay
                    def restore_clipboard():
                        try:
                            pyperclip.copy(original_clipboard)
                        except:
                            pass
                    threading.Timer(0.5, restore_clipboard).start()
                    
                    # Play confirmation sound
                    play_sound()
                except Exception as e:
                    print(f"Error during replacement: {e}")
                    if debugging:
                        traceback.print_exc()
                
                # Reset the log
                with log_lock:
                    log = ""

        if debugging:
            print("snippet processed")

    except Exception as e:
        print(f"Error processing key: {e}")
        if debugging:
            traceback.print_exc()

def main():
    """Main function to start the snippet runner"""
    global log
    
    try:
        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print banner
        print("="*60)
        print(f"          SnipIt - Text Replacement Tool - {version}")
        print("="*60)
        print("Status: Starting...")
        
        # Read the ini file
        read_ini_file()
        
        # Print loaded snippets
        print(f"Loaded {len(key_array)} snippets from Input.ini")
        print("Hotkeys:")
        print("  Ctrl+Shift+S: Open settings GUI")
        print("  Ctrl+Shift+P: Toggle sound notifications")
        print("  Ctrl+Shift+Q: Exit the application")
        print("  Esc: Reset/restart the script")
        print("-"*60)
        print("SnipIt is now running and monitoring keystrokes")
        print("-"*60)
        
        # Register hotkeys
        keyboard.add_hotkey('ctrl+shift+q', exit_app)
        keyboard.add_hotkey('ctrl+shift+s', setup)
        keyboard.add_hotkey('ctrl+shift+p', toggle_sound)
        keyboard.add_hotkey('esc', restart_script)
        
        # Start key capture
        log = ""
        
        # Start the timeout checker in a separate thread
        timeout_thread = threading.Thread(target=check_timeout, daemon=True)
        timeout_thread.start()

        # Define callbacks for key press and release events for modifier keys
        # def on_modifier_press(event):
        #     if event.name in ['ctrl', 'alt', 'shift']:
        #         update_modifier_state(event.name, True)
        #
        # def on_modifier_release(event):
        #     if event.name in ['ctrl', 'alt', 'shift']:
        #         update_modifier_state(event.name, False)
        #
        # keyboard.on_press(on_modifier_press)
        # keyboard.on_release(on_modifier_release)

        # Define a callback function for key press events
        # def on_key_press(event):
        #     try:
        #         # Skip if modifiers are pressed
        #         # if ctrl_pressed or alt_pressed:
        #         #     return
        #
        #         # Get the key value, handling special characters correctly
        #         if hasattr(event, 'name') and event.name:
        #             key = event.name
        #         elif hasattr(event, 'char') and event.char:
        #             key = event.char
        #         else:
        #             key = ""
        #
        #         if key:  # Only process if we got a valid key
        #             process_key(key)
        #     except Exception as e:
        #         print(f"Error in key press callback: {e}")
        #         if debugging:
        #             traceback.print_exc()
        #
        # # Start keyboard listener with the callback
        # keyboard.on_press(on_key_press)
        
        # Keep the program running
        keyboard.wait()
    
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

def exit_app():
    """Exit the application"""
    try:
        if os.path.exists(list_file):
            try:
                os.remove(list_file)
            except:
                pass  # Ignore if file can't be deleted
        print("="*60)
        print("SnipIt is turning off now.")
        print("="*60)
    except:
        pass
    os._exit(0)  # Force exit to kill all threads

def setup():
    """Start the setup GUI"""
    print("Opening settings GUI...")
    
    try:
        # Stop keyboard listener temporarily
        keyboard.unhook_all()
        
        # Start the GUI
        setup_gui(input_file, key_array)
        
        # Restart the script
        restart_script()
        
        # Resume keyboard listener with the correct callback
        def on_key_press(event):
            try:
                # Get the key value, handling special characters correctly
                if hasattr(event, 'name') and event.name:
                    key = event.name
                elif hasattr(event, 'char') and event.char:
                    key = event.char
                else:
                    key = ""
                
                if key:  # Only process if we got a valid key
                    process_key(key)
            except Exception as e:
                print(f"Error in key press callback: {e}")
                if debugging:
                    traceback.print_exc()
                    
        keyboard.on_press(on_key_press)
    except Exception as e:
        print(f"Error in setup: {e}")
        if debugging:
            traceback.print_exc()
        restart_script()

def toggle_sound():
    """Toggle sound setting"""
    global sound_setting
    
    try:
        config = configparser.ConfigParser(interpolation=None)
        with open(input_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
        
        if "Settings" not in config:
            config["Settings"] = {}
            
        if sound_setting == 1:
            config["Settings"]["SoundSetting"] = "0"
            print("Sounds switched off.")
            sound_setting = 0
        else:
            config["Settings"]["SoundSetting"] = "1"
            print("Sounds switched on.")
            sound_setting = 1
        
        with open(input_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        restart_script()
    except Exception as e:
        print(f"Error toggling sound: {e}")
        if debugging:
            traceback.print_exc()

def restart_script():
    """Restart the script"""
    global log, log_lock
    
    try:
        print("Restarting script...")
        read_ini_file()
        print(f"Reloaded {len(key_array)} snippets from Input.ini")
        # Reset the log
        with log_lock:
            log = ""
    except Exception as e:
        print(f"Error restarting script: {e}")
        if debugging:
            traceback.print_exc()
    
if __name__ == "__main__":
    main()