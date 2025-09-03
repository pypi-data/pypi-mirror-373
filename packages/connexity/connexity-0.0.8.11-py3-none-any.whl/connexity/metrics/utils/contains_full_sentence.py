import re


def contains_full_sentence(text: str) -> bool:
    """
    Checks if there is at least one 'full sentence' in the string.
    A 'full sentence' must:
    1) Start with a capital letter,
    2) End with one of '.', '!', '?', '...',
    3) Followed by either the end of the text or by a space and a capital letter.
    """
    pattern = re.compile(
        r'[A-Z]'               # Start with uppercase letter
        r'[^.?!]*?'            # Then any characters, non-greedy
        r'(?:\.\.\.|[.?!])'    # End with '...', '.', '?', or '!'
        r'(?:\s+[A-Z]|$)'      # Followed by space + capital letter or end of string
    )
    return bool(pattern.search(text))