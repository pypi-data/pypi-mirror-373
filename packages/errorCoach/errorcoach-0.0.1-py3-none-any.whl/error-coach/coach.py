import sys
import re

ERRORS = {
    r"TypeError: unsupported operand type.*int.*str": (
        "You tried to add a number (int) and text (str).",
        "Convert one using int() or str()."
    ),
    r"TypeError: 'list' object is not callable": (
        "You used square brackets [] instead of parentheses () after 'list'.",
        "Use list() to create a list, or check if you meant to access an index."
    ),
    r"TypeError: 'int' object is not callable": (
        "You tried to call a number like a function.",
        "Check if you accidentally put parentheses after a number, or overwrote a function name."
    ),
    r"TypeError: 'str' object is not callable": (
        "You tried to call a string like a function.",
        "Check for typos, missing operators, or if you overwrote a function name with a string."
    ),
    r"TypeError: '.*' object is not callable": (
        "You tried to use something like a function, but it isn't one.",
        "Check for missing parentheses (), typos, or if you overwrote a function name."
    ),
    r"TypeError: can only concatenate str.*not.*int": (
        "You tried to join text with a number directly.",
        "Use str(number) to convert it first, or use f-strings: f'{text}{number}'."
    ),
    r"TypeError: '.*' object doesn't support item assignment": (
        "You tried to change an item in something that can't be changed (like a tuple).",
        "Use a list instead of a tuple, or create a new tuple with the changes."
    ),
    r"TypeError: '.*' object is not iterable": (
        "You tried to loop over something that can't be looped over.",
        "Make sure you're using a list, string, or other iterable object."
    ),
    r"IndexError: list index out of range": (
        "You tried to access a list index that doesn't exist.",
        "Remember: list indices start at 0, max index = len(list)-1."
    ),
    r"IndexError: string index out of range": (
        "You tried to access a character in a string that doesn't exist.",
        "Double-check the string length with len(), indices start at 0."
    ),
    r"NameError: name '.*' is not defined": (
        "You used a variable that hasn't been defined yet.",
        "Make sure you spelled it correctly, defined it first, or imported the module."
    ),
    r"KeyError: '.*'": (
        "You tried to access a dictionary key that doesn't exist.",
        "Use dict.get(key) to avoid errors, or check 'key in dict' first."
    ),
    r"AttributeError: '.*' object has no attribute '.*'": (
        "You tried to use a method/property that doesn't exist for this object type.",
        "Check spelling, the object type, or look up the correct method name."
    ),
    r"ValueError: invalid literal for int\(\) with base 10: '.*'": (
        "You tried to convert text into a number, but the text isn't numeric.",
        "Make sure the string only contains digits before using int(), or use try/except."
    ),
    r"ValueError: math domain error": (
        "You gave a math function an invalid input (like negative number to sqrt).",
        "Check that your number is in the correct range (e.g., sqrt needs ≥ 0)."
    ),
    r"ValueError: too many values to unpack": (
        "You tried to assign more values than variables available.",
        "Make sure the number of variables matches the values being unpacked."
    ),
    r"ValueError: not enough values to unpack": (
        "You tried to assign fewer values than variables available.",
        "Make sure you have enough values for all the variables."
    ),
    r"IndentationError: unexpected indent": (
        "Your code has spaces/tabs in the wrong place.",
        "Remove extra indentation, or check if you're missing an if/for/while statement above."
    ),
    r"IndentationError: expected an indented block": (
        "You wrote a statement like if/for/while/def without indented code under it.",
        "Add code indented by 4 spaces under the statement, or use 'pass' as a placeholder."
    ),
    r"IndentationError: inconsistent use of tabs and spaces": (
        "You mixed tabs and spaces for indentation.",
        "Choose either 4 spaces OR tabs consistently throughout your file (spaces preferred)."
    ),
    r"IndentationError: unindent does not match any outer indentation level": (
        "Your indentation doesn't line up with any previous level.",
        "Make sure each indentation level uses the same number of spaces (usually 4)."
    ),
    r"SyntaxError: EOL while scanning string literal": (
        "You forgot to close a string with quotes.",
        "Check for missing ' or \" at the end of your string."
    ),
    r"SyntaxError: invalid syntax": (
        "Python couldn't understand this line of code.",
        "Check for missing colons :, parentheses (), commas, or typos."
    ),
    r"SyntaxError: unexpected EOF while parsing": (
        "You're missing closing brackets, parentheses, or quotes somewhere.",
        "Check that all ( ) [ ] { } and quotes are properly closed."
    ),
    r"SyntaxError: invalid character.*": (
        "You have a character that Python doesn't recognize.",
        "Check for smart quotes, em-dashes, or other non-standard characters."
    ),
    r"ZeroDivisionError: division by zero": (
        "You tried to divide by zero.",
        "Check your denominator before dividing, or use an if statement to avoid zero."
    ),
    r"FileNotFoundError: .*": (
        "Python can't find the file you're trying to open.",
        "Double-check the filename and path, use absolute paths, or check if file exists."
    ),
    r"PermissionError: .*": (
        "You don't have permission to access this file.",
        "Check file permissions, close the file if it's open elsewhere, or run as administrator."
    ),
    r"IsADirectoryError: .*": (
        "You tried to open a folder as if it were a file.",
        "Make sure you're pointing to a file, not a directory."
    ),
    r"ModuleNotFoundError: No module named '.*'": (
        "You tried to import a module that isn't installed or doesn't exist.",
        "Check the spelling, install it with 'pip install module_name', or check if it's built-in."
    ),
    r"ImportError: cannot import name '.*'": (
        "You tried to import something that doesn't exist in that module.",
        "Check the spelling, or see what's actually available in the module."
    ),
    r"UnboundLocalError: .*referenced before assignment": (
        "You used a variable before defining it, or have scope issues.",
        "Define the variable first, or check if you need 'global' or 'nonlocal' keywords."
    ),
    r"RecursionError: maximum recursion depth exceeded": (
        "Your function calls itself too many times (infinite recursion).",
        "Add a base case to stop the recursion, or check your recursive logic."
    ),
    r"AssertionError": (
        "An assertion failed - something you expected to be true wasn't.",
        "Check the condition in your assert statement, or remove the assert if not needed."
    ),
}

def friendlyExcepthook(excType, excValue, traceback):
    msg = str(excValue)
    for pattern, (explanation, fix) in ERRORS.items():
        if re.match(pattern, f"{excType.__name__}: {msg}"):
            print("\n" + "-"*20 + " Error-Coach " + "-"*20)
            print(f"Error: {excType.__name__}: {msg}")
            print(f"What went wrong: {explanation}")
            print(f"How to Fix: {fix}")
            print("-"*54 + "\n")
            break
    else:
        sys.__excepthook__(excType, excValue, traceback)

def enable():
    sys.excepthook = friendlyExcepthook
    