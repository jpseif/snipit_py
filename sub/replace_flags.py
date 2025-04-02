#!/usr/bin/env python3
"""
Replace flags in text with dynamic content
Ported from AutoHotKey to Python with improvements
"""

import datetime
import re

def replace_flags(input_str):
    """
    Replace special flags in input string with dynamic content
    
    Flags:
    `%dd or %dd --> replaced by day: 01 - 31
    `%d or %d --> replaced by day: 1 - 31
    `%MM or %MM --> replaced by month: 01 - 12
    `%M or %M --> replaced by month: 1 - 12
    `%y or %y --> replaced by year: e.g. 8 (no leading zero)
    `%yy or %yy --> replaced by year: e.g. 08 (with leading zero)
    `%yyyy or %yyyy --> replaced by year: e.g. 2017
    `%hh or %hh --> replaced by hour: 01 - 12
    `%h or %h --> replaced by hour: 1 - 12
    `%HH or %HH --> replaced by hour: 01 - 23
    `%H or %H --> replaced by hour: 1 - 23
    `%mm or %mm --> replaced by minutes: 00 - 59
    `%m or %m --> replaced by minutes: 0 - 59
    `%ss or %ss --> replaced by seconds: 00 - 59
    `%s or %s --> replaced by seconds: 0 - 59
    {n} --> will be converted to newlines later in the main script
    """
    try:
        now = datetime.datetime.now()
        
        # Make a copy of the input string to avoid modifying the original
        result = str(input_str)
        
        # Process date/time replacements in a specific order to avoid conflicts
        # For example, replace %yyyy before %yy to prevent double replacement
        
        # Year replacements (longest first)
        result = result.replace("`%yyyy", now.strftime("%Y"))
        result = result.replace("%yyyy", now.strftime("%Y"))
        result = result.replace("`%yy", now.strftime("%y"))
        result = result.replace("%yy", now.strftime("%y"))
        result = result.replace("`%y", str(now.year)[-1:])
        result = result.replace("%y", str(now.year)[-1:])
        
        # Month replacements
        result = result.replace("`%MM", now.strftime("%m"))
        result = result.replace("%MM", now.strftime("%m"))
        result = result.replace("`%M", str(now.month))
        result = result.replace("%M", str(now.month))
        
        # Day replacements
        result = result.replace("`%dd", now.strftime("%d"))
        result = result.replace("%dd", now.strftime("%d"))
        result = result.replace("`%d", str(now.day))
        result = result.replace("%d", str(now.day))
        
        # Hour replacements (24-hour format)
        result = result.replace("`%HH", now.strftime("%H"))
        result = result.replace("%HH", now.strftime("%H"))
        result = result.replace("`%H", str(now.hour))
        result = result.replace("%H", str(now.hour))
        
        # Hour replacements (12-hour format)
        result = result.replace("`%hh", now.strftime("%I"))
        result = result.replace("%hh", now.strftime("%I"))
        result = result.replace("`%h", str(int(now.strftime("%I"))))
        result = result.replace("%h", str(int(now.strftime("%I"))))
        
        # Minute replacements
        result = result.replace("`%mm", now.strftime("%M"))
        result = result.replace("%mm", now.strftime("%M"))
        result = result.replace("`%m", str(int(now.strftime("%M"))))
        result = result.replace("%m", str(int(now.strftime("%M"))))
        
        # Second replacements
        result = result.replace("`%ss", now.strftime("%S"))
        result = result.replace("%ss", now.strftime("%S"))
        result = result.replace("`%s", str(int(now.strftime("%S"))))
        result = result.replace("%s", str(int(now.strftime("%S"))))
        
        # Remove any backtick characters (escape characters in the original script)
        result = result.replace("`", "")
        
        return result
    
    except Exception as e:
        print(f"Error in replace_flags: {e}")
        # Return the input string unchanged in case of error
        return input_str