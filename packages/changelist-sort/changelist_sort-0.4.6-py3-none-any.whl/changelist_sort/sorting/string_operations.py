"""A Collection of String Operations used during sort and formatting.
"""


def capitalize_words(sentence: str) -> str:
    """
    Uppercase the first letter of every word in the sentence.
    """
    return ' '.join(word.capitalize() for word in sentence.split())


def replace_underscores(name: str) -> str:
    """
    Replace all underscore characters with spaces.
    """
    return name.replace('_', ' ')


def split_words_on_capitals(input_str: str) -> str:
    """
    Split a string into words on capital letters.
    """
    return ''.join(' ' + c if c.isupper() else c for c in input_str)
