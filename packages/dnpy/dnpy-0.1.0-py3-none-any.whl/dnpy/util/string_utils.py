"""
String utilities for handling obfuscated .NET assemblies.
"""

import unicodedata

__all__ = [
    "is_printable_unicode",
    "clean_string_for_display",
]


def is_printable_unicode(char: str) -> bool:
    """
    Check if a Unicode character is printable and safe to display.

    This function determines if a character should be displayed as-is
    or escaped based on its Unicode properties.
    """
    if not char:
        return True

    code_point = ord(char)

    # Basic ASCII printable range
    if 32 <= code_point <= 126:
        return True

    # Check Unicode category for printable characters
    category = unicodedata.category(char)

    # Printable categories - expanded to include more Unicode characters:
    # Lu, Ll, Lt, Lm, Lo - Letters
    # Nd, Nl, No - Numbers
    # Pc, Pd, Pe, Pf, Pi, Po, Ps - Punctuation
    # Sc, Sk, Sm, So - Symbols
    # Zl, Zp, Zs - Separators
    # Mc, Me, Mn - Combining marks and modifiers
    printable_categories = {
        "Lu",
        "Ll",
        "Lt",
        "Lm",
        "Lo",  # Letters
        "Nd",
        "Nl",
        "No",  # Numbers
        "Pc",
        "Pd",
        "Pe",
        "Pf",
        "Pi",
        "Po",
        "Ps",  # Punctuation
        "Sc",
        "Sk",
        "Sm",
        "So",  # Symbols
        "Zl",
        "Zp",
        "Zs",  # Separators
        "Mc",
        "Me",
        "Mn",  # Combining marks and modifiers
    }

    return category in printable_categories


def clean_string_for_display(text: str) -> str:
    """
    Clean a string for display, preserving readable Unicode while escaping problematic characters.

    This is a more conservative approach that tries to preserve as much readable
    content as possible while ensuring safe display.
    """
    if not text:
        return text

    result = []
    for char in text:
        if is_printable_unicode(char):
            result.append(char)
        else:
            # Escape non-printable characters
            code_point = ord(char)
            if code_point <= 0xFF:
                result.append(f"\\x{code_point:02x}")
            elif code_point <= 0xFFFF:
                result.append(f"\\u{code_point:04x}")
            else:
                result.append(f"\\U{code_point:08x}")

    return "".join(result)
