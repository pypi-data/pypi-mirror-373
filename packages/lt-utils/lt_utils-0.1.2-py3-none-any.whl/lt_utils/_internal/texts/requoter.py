__all__ = ["requoter"]

import re
from typing import List

_SINGLE_QUOTES_MAP = {
    96: "'",
    8216: "'",
    8217: "'",
    8219: "'",
    10075: "'",
    10076: "'",
}

_DOUBLE_QUOTES_MAP = {
    8220: '"',
    8221: '"',
    8222: '"',
    10080: '"',
    12317: '"',
    12318: '"',
    12319: '"',
    65282: '"',
}


def _get_quotes(text: str) -> List[int]:
    """
    Count and return the total quotes and their indexes in the given text.

    Args:
        text (str): The input text.

    Returns:
        Tuple[int, List[int]]: A tuple containing the total quotes and their indexes.
    """
    return [i for i, char in enumerate(text) if char == '"']


def _clear_subquotes(text: str) -> str:
    """
    Remove sub-quotes and return the modified text.

    Args:
        text (str): The input text.

    Returns:
        str: The modified text without sub-quotes.
    """
    return re.sub("''", "'", text.translate(_SINGLE_QUOTES_MAP))


def _simplify_quotes(text: str, simplify_everything: bool = False) -> str:
    """
    Replace special quotation marks with simple double quotes in the given text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with special quotation marks replaced by simple double quotes.
    """
    res = re.sub('""', '"', text.translate(_DOUBLE_QUOTES_MAP))
    if simplify_everything:
        return _clear_subquotes(res)
    return res


def _update_text(positions: List[int], text: str, q1: str = "“", q2: str = "”") -> str:
    """
    Update the text by enclosing specified positions with given quotation marks.

    Args:
        positions (List[int]): A list of positions where quotation marks should be applied.
        text (str): The input text.
        q1 (str, optional): The opening quotation mark. Defaults to "“".
        q2 (str, optional): The closing quotation mark. Defaults to "”".

    Returns:
        str: The updated text with specified positions enclosed by the given quotation marks.
    """
    if not positions:
        return text
    split_version = [positions[i : i + 2] for i in range(0, len(positions), 2)]
    for i, pair in enumerate(split_version):
        if len(pair) == 2:
            text = (
                text[: pair[0]]
                + q1
                + text[pair[0] + 1 : pair[1]]
                + q2
                + text[pair[1] + 1 :]
            )
        else:
            text = text[: pair[0]] + q1 + text[pair[0] + 1 :]

    return text


def requoter(input_text: str, use_simple: bool = False) -> str:
    """
    Process the input text, fixing and changing the quotation style.

    Args:
        input_text (str): The text input that will be converted.
        use_simple (bool, optional): If `True`, It will return the text with the simply quotes instead of the special markings. Defaults to False.

    Returns:
        str: The processed text with fixed and changed quotation style.
    """
    input_text = _simplify_quotes(input_text, use_simple)
    if use_simple:
        return input_text
    elif '"' not in input_text:
        return input_text.replace("'", "’")
    return _update_text(_get_quotes(input_text), input_text).replace("'", "’")
