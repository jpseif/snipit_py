#!/usr/bin/env python3
"""
GUI for SnipIt
"""

import os
import sys
import configparser
import tkinter as tk
from tkinter import messagebox, ttk
import traceback

def setup_gui(input_file, key_array):
    """Setup the GUI for managing snippets"""
    
    # Initialize variables
    key_list = []
    value_list = []
    key_value_list = []
    
    try:
        # Read the current snippets from the ini file - disable interpolation
        config = configparser.ConfigParser(interpolation=None)
        
        # Check if the file exists
        if not os.path.exists(input_file):
            config["Strings"] = {}
            config["Settings"] = {"SoundSetting": "0"}
            with open(input_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
        # Read the file with utf-8 encoding
        with open(input_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
        
        # Check if required sections exist
        if "Strings" not in config:
            config["Strings"] = {}
            with open(input_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
        # Generate the lists for the GUI
        for key in config["Strings"]:
            key_list.append(key)
            value_list.append(config["Strings"][key])
            # Limit the display length for very long replacements
            display_value = config["Strings"][key]
            if len(display_value) > 40:
                display_value = display_value[:37] + "..."
            display_value = display_value.replace("{n}", "↵")  # Show newlines with a symbol
            key_value_list.append(f"{key} => {display_value}")
        
        # Create the GUI
        root = tk.Tk()
        root.title("SnipIt: Snippets & Replacements")
        root.resizable(False, False)
        
        # Set font
        font_style = ("Verdana", 8)
        
        # Add elements to the GUI
        tk.Label(root, text="Snippets => Replacements", font=font_style).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Create listbox with scrollbar for snippets
        frame = tk.Frame(root)
        frame.grid(row=1, column=0, padx=20, sticky="w")
        
        listbox = tk.Listbox(frame, width=50, height=12, font=font_style)
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        listbox.pack(side="left", fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Add items to the listbox
        for item in key_value_list:
            listbox.insert(tk.END, item)
        
        # Create input fields and buttons
        input_frame = tk.Frame(root)
        input_frame.grid(row=0, column=1, rowspan=2, padx=10, sticky="n")
        
        tk.Label(input_frame, text="Enter snippet (max. 10):", font=font_style).pack(anchor="w", pady=(20, 5))
        snippet_entry = tk.Entry(input_frame, width=20, font=font_style)
        snippet_entry.pack(anchor="w")
        
        tk.Label(input_frame, text="Enter replacement:", font=font_style).pack(anchor="w", pady=(5, 5))
        replacement_entry = tk.Entry(input_frame, width=20, font=font_style)
        replacement_entry.pack(anchor="w")
        
        # Help text for special codes
        help_frame = tk.Frame(root)
        help_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")
        
        help_text = """Special codes:
- Date: %dd (day), %MM (month), %yyyy (year)
- Time: %HH (hour), %mm (mins), %ss (secs)
- {n} inserts a newline"""
        
        tk.Label(help_frame, text=help_text, font=("Verdana", 7), justify="left").pack(anchor="w")
        
        # Button actions
        def add_snippet():
            try:
                snippet = snippet_entry.get().strip()
                replacement = replacement_entry.get()
                
                if not snippet:
                    messagebox.showinfo("Info", "Enter a snippet first!")
                    return
                
                if not replacement:
                    messagebox.showinfo("Info", "Enter a replacement string first!")
                    return
                
                if len(snippet) > 10:
                    messagebox.showinfo("Info", "Snippet length should not exceed 10 characters!")
                    return
                
                # Write to the ini file
                config = configparser.ConfigParser(interpolation=None)
                with open(input_file, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                # Ensure the Strings section exists
                if "Strings" not in config:
                    config["Strings"] = {}
                
                config["Strings"][snippet] = replacement
                
                with open(input_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                # Restart the GUI to refresh the list
                root.destroy()
                setup_gui(input_file, key_array)
            except Exception as e:
                messagebox.showerror("Error", f"Error adding snippet: {e}")
        
        def delete_snippet():
            try:
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    if index < len(key_list):
                        key = key_list[index]
                        
                        # Delete from the ini file
                        config = configparser.ConfigParser(interpolation=None)
                        with open(input_file, 'r', encoding='utf-8') as f:
                            config.read_file(f)
                        
                        if "Strings" in config and key in config["Strings"]:
                            config.remove_option("Strings", key)
                            
                            with open(input_file, 'w', encoding='utf-8') as f:
                                config.write(f)
                        
                        # Restart the GUI to refresh the list
                        root.destroy()
                        setup_gui(input_file, key_array)
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting snippet: {e}")
        
        def continue_action():
            root.destroy()
        
        def stop_action():
            try:
                if os.path.exists(os.path.join(os.path.dirname(input_file), "List.txt")):
                    os.remove(os.path.join(os.path.dirname(input_file), "List.txt"))
            except:
                pass  # Ignore if file can't be deleted
                
            messagebox.showinfo("Info", "SnipIt is turning off now.")
            root.destroy()
            os._exit(0)  # Force exit to kill all threads
        
        # When an item is selected in the listbox, populate the entry fields
        def on_select(event):
            try:
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    if index < len(key_list):
                        snippet_entry.delete(0, tk.END)
                        snippet_entry.insert(0, key_list[index])
                        
                        replacement_entry.delete(0, tk.END)
                        replacement_entry.insert(0, value_list[index])
            except Exception as e:
                print(f"Error in on_select: {e}")
        
        listbox.bind('<<ListboxSelect>>', on_select)
        
        # Create buttons
        tk.Button(input_frame, text="Add/Update", width=20, command=add_snippet, font=font_style).pack(anchor="w", pady=(5, 5))
        tk.Button(input_frame, text="Delete", width=20, command=delete_snippet, font=font_style).pack(anchor="w", pady=(5, 5))
        tk.Button(input_frame, text="Continue", width=20, command=continue_action, font=font_style).pack(anchor="w", pady=(5, 5))
        tk.Button(input_frame, text="Stop", width=20, command=stop_action, font=font_style).pack(anchor="w", pady=(5, 5))
        
        # Copyright notice
        tk.Label(input_frame, text="(Python port of J. Seif's 2017 AHK script)", font=("Verdana", 7)).pack(anchor="w", pady=(15, 5))
        
        # Position the window in the center of the screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Remove the window decorator options
        try:
            root.attributes('-toolwindow', True)
        except:
            pass  # Not all platforms support this
        
        # Set the continue button as default
        root.bind('<Return>', lambda event: continue_action())
        
        # Start the GUI main loop
        root.mainloop()
    
    except Exception as e:
        print(f"Error in GUI setup: {e}")
        traceback.print_exc()
        
        # Create a simple error dialog
        try:
            error_root = tk.Tk()
            error_root.title("SnipIt Error")
            tk.Label(error_root, text=f"Error in GUI: {e}").pack(padx=20, pady=20)
            tk.Button(error_root, text="OK", command=error_root.destroy).pack(pady=10)
            error_root.mainloop()
        except:
            pass  # If even the error dialog fails, just continue