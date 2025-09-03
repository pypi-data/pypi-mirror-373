__all__ = [
    "spacy_tokenizer",
    "tokenize_text",
    "similarity_simplified",
    "similarity",
    "has_digit",
    "entropy",
    "scramble_text",
    "compare_texts",
    "stem_text",
    "recursive_replacer",
    "clipboard",
    "html_to_markdown",
    "markdown_to_html",
    "split",
    "lemmatize_text",
    "generate_ngrams",
    "max_rfinder",
    "check_next_string",
    "trim_incomplete_sentence",
    "simplify_quotes",
    "clear_empty",
    "extract_named_entities",
    "delimiter_split",
    "find_repeated_words",
    "normalize_text",
    "remove_non_printable",
    "split_by_paragraph",
    "extract_hashtags",
    "extract_mentions",
    "count_sentences",
    "extract_keywords",
    "formatter",
    "count_words",
    "extract_keys",
    "find_in_text",
    "unescape",
    "escape",
    "replace_pos_tags",
    "requoter",
]

import gc
import re

from collections import Counter

from lt_utils.common import *
from lt_utils.type_utils import is_str, is_array
from lt_utils._internal.texts.requoter import requoter
from lt_utils._internal.texts.splitter import SplitText
from lt_utils._internal.texts.nlp_stuff import nlp_instance


def spacy_tokenizer(
    text: str,
    allowed_pos: set[str] = {"NOUN", "ADJ"},
    spacy_model: Literal["en_core_web_md", "en_core_web_lg"] = None,
) -> List[str]:
    """Tokenize and lemmatize text, filtering by POS tags."""
    nlp_instance.initialize_spacy(spacy_model)
    doc = nlp_instance.spc(text)
    return [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in allowed_pos
    ]


def tokenize_text(
    text: str,
    by: Literal["word", "sentence"] = "word",
    language: str = "english",
    preserve_line: bool = False,
) -> List[str]:
    """Tokenize text by words or sentences.

    Args:
        text (str): The input text to tokenize.
        by (Literal["word", "sentence"], optional): The level of tokenization ("word" or "sentence"). Defaults to "word".

    Returns:
        List[str]: A list of tokens based on the specified level.
    """
    assert by in ["word", "sentence"], "Invalid tokenization type"
    import nltk

    nlp_instance.initialize_nltk()
    if by == "word":
        return [
            recursive_replacer(
                x,
                {
                    "``": '"',
                    "`": '"',
                },
            )
            for x in nltk.word_tokenize(
                text,
                language=language,
                preserve_line=preserve_line,
            )
        ]
    return nltk.sent_tokenize(text, language=language)


def similarity_simplified(text1: str, text2: str) -> float:
    """Compute similarity between two texts using cosine similarity.

    Args:
        text1 (str): The first text for comparison.
        text2 (str): The second text for comparison.

    Returns:
        float: The cosine similarity score between the two texts.
    """
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]


def similarity(
    text1: str,
    text2: str,
    spacy_model: Literal["en_core_web_md", "en_core_web_lg"] = None,
) -> float:
    """Compute similarity between two texts using TF-IDF cosine or spaCy vectors.

    Args:
        text1 (str): First input text.
        text2 (str): Second input text.

    Returns:
        float: Similarity score.
    """
    nlp_instance.initialize_spacy(spacy_model)
    doc1, doc2 = nlp_instance.spc(text1), nlp_instance.spc(text2)
    return doc1.similarity(doc2)


def has_digit(text: str):
    return any([x.isdigit() for x in text.strip()])


def entropy(
    text: str,
    level: Literal["char", "word"] = "char",
    normalize: bool = False,
    language: str = "english",
) -> float:
    """Calculate entropy of a text using either character or word-level tokenization.

    Args:
        text (str): Input string.
        level (str): Tokenization level ("char" or "word").
        normalize (bool): If True, normalize entropy to [0, 1] range.
        language (str): Language for word tokenization.

    Returns:
        float: Entropy value.
    """
    import numpy as np

    if level == "word":
        tokens = tokenize_text(text.lower(), by="word", language=language)
    else:
        tokens = list(text.lower())

    if not tokens:
        return 0.0

    counter = Counter(tokens)
    total = len(tokens)
    probs = np.array([count / total for count in counter.values()])

    ent = -np.sum(probs * np.log2(probs))

    if normalize:
        import math

        max_entropy = math.log2(len(counter)) if len(counter) > 0 else 1
        ent /= max_entropy

    return float(ent)


def scramble_text(text: str) -> str:
    """Randomly shuffle the words in a text.

    Args:
        text (str): The input text to be scrambled.

    Returns:
        str: The text with its words randomly shuffled.
    """
    import random

    words = text.split()
    random.shuffle(words)
    return " ".join(words)


def compare_texts(text1: str, text2: str) -> List[str]:
    """Compare two texts and highlight the differences.

    Args:
        text1 (str): The first text to compare.
        text2 (str): The second text to compare.

    Returns:
        List[str]: A list of lines that differ between the two texts, prefixed with '- ' for deletions and '+ ' for additions.
    """
    import difflib

    differ = difflib.Differ()
    result = list(differ.compare(text1.splitlines(), text2.splitlines()))
    return [line for line in result if line.startswith("- ") or line.startswith("+ ")]


def stem_text(
    text: str,
    language: str = "english",
) -> str:
    """Reduce words in the text to their stem or root form.

    Args:
        text (str): The input text to be stemmed.

    Returns:
        str: The text with words reduced to their stems.
    """
    import nltk

    tokens = tokenize_text(
        text,
        by="word",
        language=language,
        preserve_line=False,
    )
    stemmer = nltk.PorterStemmer()

    return " ".join([stemmer.stem(token) for token in tokens])


def recursive_replacer(entry: str, dic: dict[str, str]) -> str:
    """
    Recursively replaces all keys of the dictionary with their corresponding values within a given string.

    Args:
        text (str): The original text.
        replacements (Dict[str, str]): A dictionary where keys are what to replace and values is what they will be replaced by

    Returns:
        str: The final modified text
    """
    for i, j in dic.items():
        entry = entry.replace(i, j)
    return entry


def clipboard(
    task: Literal["copy", "paste"], text: Optional[str] = None
) -> Optional[str]:
    """
    If  the task is set to:
    Copy: Set the clipboard to the given text.
    Paste: Returns the contents from the clipboard.
    """
    import pyperclip

    if task == "copy":
        pyperclip.copy(text or "")
    else:
        return pyperclip.paste()


def html_to_markdown(
    html: Union[str, bytes],
    escape_asterisks: bool = True,
    escape_underscores: bool = True,
    escape_misc: bool = True,
    heading_style: bool = "underlined",
    strong_em_symbol: bool = "*",
    sub_symbol: bool = "",
    sup_symbol: bool = "",
    wrap: bool = False,
    wrap_width: bool = 80,
) -> str:
    """
    Converts HTML content to Markdown format.

    Args:
        html (str): The HTML string that needs to be converted.
                    Example - "<h1>Hello, World!</h1>"

    Returns:
        str: The corresponding markdown version of the inputted HTML
             Example - "# Hello, World!"
    """
    import markdownify

    return markdownify.markdownify(
        html=html,
        escape_asterisks=escape_asterisks,
        escape_underscores=escape_underscores,
        escape_misc=escape_misc,
        heading_style=heading_style,
        strong_em_symbol=strong_em_symbol,
        sub_symbol=sub_symbol,
        sup_symbol=sup_symbol,
        wrap=wrap,
        wrap_width=wrap_width,
    )


def markdown_to_html(markdown: Union[str, bytes]) -> str:
    """
    Converts Markdown text to HTML.

    Args:
        markdown (Union[str, bytes]): The input Markdown text. Can be either a string or bytes object.

    Returns:
        str: The converted HTML.
    """
    import markdown2

    return markdown2.markdown(markdown)


def _blob_split(text: str, *, __recall: bool = False) -> List[str]:
    """
    Splits the input text into sentences using TextBlob.

    Args:
        text (str): The input text to split.

    Returns:
        list[str]: A list of the detected sentences in the provided text.
    """
    from textblob import TextBlob
    from textblob.exceptions import MissingCorpusError

    try:
        return [x for x in TextBlob(text).raw_sentences]
    except MissingCorpusError as e:
        if not __recall:
            import subprocess

            _ = subprocess.run(
                "python -m textblob.download_corpora",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            gc.collect()
            return _blob_split(text, __recall=True)
        raise e


def split(
    entry: str,
    max_length: int = 200,
    desired_length: int = 100,
    simplify_quote: bool = False,
    mode: Literal["base", "blob"] = "base",
):
    """Split the text into a list of sentences.
    Using "blob" mode it will return the split sentences independent of the size.

    On "base" mode, this function tries to make each of those splits at an approximated length
    to the desired_length, and below the max limit.

    Args:
        entry (str): The text to be splitten
        max_length (int, optional): Max size per sentence (available only at "base" mode). Defaults to 200.
        desired_length (int, optional): Size that the split will try to be done (available only at "base" mode). Defaults to 100.
        simplify_quote (bool, optional): If True, will replace "fancy" quotes to simpler ones. (available only at "base" mode). Defaults to False.
        mode (Literal["base", "blob"], optional): Splitting mode. Defaults to "base".

    Returns:
        _type_: _description_
    """
    mode = mode.lower()
    assert mode in [
        "base",
        "blob",
    ], f'Invalid mode "{mode}". It must be either "base", "blob"'
    if simplify_quote:
        entry = simplify_quotes(entry)
    if mode == "base":
        return SplitText()(
            entry,
            desired_length=desired_length,
            max_length=max_length,
        )

    return _blob_split(entry)


def lemmatize_text(text: str) -> str:
    """Reduce words in the text to their base or dictionary form.

    Args:
        text (str): The input text to be lemmatized.

    Returns:
        str: The text with words reduced to their base forms.
    """
    from textblob import TextBlob

    return " ".join([word.lemmatize() for word in TextBlob(text=text).words])


def generate_ngrams(
    inputs: str | Sequence[Any],
    n: int = 5,
    text_language: str = "english",
    split_text_by: Literal["word", "sentence"] = "word",
    split_ngram_text_by: Literal["char", "full"] = "char",
) -> List[Any]:
    """Generate n-grams (sequences of n items) from the text.

    Args:
        inputs (str | Sequence[Any]): The input text or a list of components from which to
                generate n-grams.
        n (int): The number of items in each n-gram.
        text_language (str, optional): Used only when the input is a string.
                It will be used to split the words/sentences properly.
        split_text_by (Literal["word", "sentence"], optional): Used only when the input is a string.
                If set to words the split will be word by word, otherwise will be the sentence.
        split_ngram_text_by (Literal["char", "full"], optional):  Used only when the input is a string.
                If set to 'char' it will split char by char, otherwise will do the n-grams for the entire
                words or sentences.
    Returns:
        List[Any]: A list of n-grams generated from the inputs.
    """
    import nltk

    if is_array(inputs, True):
        return [x for x in nltk.ngrams(inputs, n)]
    is_str(inputs, False, False, True)
    assert split_ngram_text_by in [
        "char",
        "full",
    ], f'Invalid option for "split_ngram_text_by": {split_ngram_text_by}, it must be either "char" or "full"'
    tokens = tokenize_text(
        inputs,
        by=split_text_by,
        language=text_language,
        preserve_line=False,
    )

    if split_ngram_text_by == "char":
        return [[x for x in nltk.ngrams(word, n)] for word in tokens]
    return [x for x in nltk.ngrams(tokens, n)]


def max_rfinder(entry: str, items_to_find: Union[List[str], Tuple[str, ...]]):
    """
    Finds the last occurrence of any item in a list or tuple within a string.

    Args:
        entry (str): The input string.
        items_to_find (Union[list[str], tuple[str]]): A list or tuple containing strings to find in 'txt'.

    Returns:
        int: The index of the last found item, -1 if no item is found.
    """
    highest_results = -1
    for item in items_to_find:
        current = entry.rfind(item)
        if current > highest_results:
            highest_results = current
    return highest_results


def check_next_string(
    entry: str,
    current_id: int,
    text_to_match: str | list[str] | None = None,
    is_out_of_index_valid: bool = False,
):
    """
    Checks if the next character in a string matches one or more possibilities.

    Args:
        entry (str): The input string.
        current_id (int): The index of the current character within the string.
        text_to_match (Union[str, list[str], None]): A single character to match or a list/tuple of characters.
                        If not provided and is_out_of_index_valid will be used as a result. Defaults to None.
        is_out_of_index_valid (bool): Whether returning True when the index is out of bounds should be valid. Defaults to False.

    Returns:
        bool: True, if any condition is met; False otherwise.
    """
    try:
        if is_array(text_to_match):
            return entry[current_id + 1] in text_to_match
        return entry[current_id + 1] == text_to_match
    except IndexError:
        return is_out_of_index_valid


def trim_incomplete_sentence(entry: str) -> str:
    """
    Tries to trim an incomplete sentence to the nearest complete one. If it fails returns the original sentence back.

    Args:
        entry (str): The original string containing sentences.
            If not complete, it will be trimmed to end with a valid punctuation mark.

    Returns:
        str: The finalized string.

    Example:

        >>> trimincompletesentence("Hello World! How are you doing?")
        "Hello World!"

        >>> trimincompletesentence("I like programming.")
        "I like programming." # Returns the sentence as it was.
        >>> trimincompletesentence("Hello there. This sentence is incomplete")
        "Hello there." # Returns the latest complete sequence.
        >>> trimincompletesentence("Hello there This sentence is incomplete")
        "Hello there This sentence is incomplete" # Returns the entire sentence if no cutting point was found.
    """
    possible_ends = (".", "?", "!", '."', '?"', '!"')
    entry = str(entry).rstrip()
    lastpunc = max_rfinder(entry, possible_ends)
    ln = len(entry)
    lastpunc = max(entry.rfind("."), entry.rfind("!"), entry.rfind("?"))
    if lastpunc < ln - 1:
        if entry[lastpunc + 1] == '"':
            lastpunc = lastpunc + 1
    if lastpunc >= 0:
        entry = entry[: lastpunc + 1]
    return entry


def simplify_quotes(entry: str) -> str:
    """
    Replaces special characters with standard single or double quotes.

    Args:
        entry (str): The input string containing special quote characters.

    Returns:
        str: The simplified string without the special quote characters.
    """
    is_str(entry, False, False, True)
    return requoter(entry, True)


def clear_empty(text: str, clear_empty_lines: bool = True) -> str:
    """
    Clear empty lines (optional) and empty spaces on a given text.
    """
    return "\n".join(
        [
            re.sub(r"\s+", " ", x.strip())
            for x in text.splitlines()
            if not clear_empty_lines or x.strip()
        ]
    )


def extract_named_entities(
    text: str,
    language: str = "english",
) -> List[str]:
    """Extract named entities from the text.

    Args:
        text (str): The input text from which to extract named entities.

    Returns:
        List[str]: A list of named entities found in the text.
    """
    import nltk

    nlp_instance.initialize_nltk()
    tokens = tokenize_text(
        text,
        by="word",
        language=language,
        preserve_line=False,
    )
    tagged = nltk.pos_tag(tokens)
    chunked = nltk.ne_chunk(tagged)
    return list(
        set([chunk.label() for chunk in chunked if isinstance(chunk, nltk.Tree)])
    )


def delimiter_split(text: str, delimiter: str) -> List[str]:
    """Splits text into parts based on a delimiter.

    Args:
        text (str): The input text to be chunked.
        delimiter (str): The delimiter to use for splitting the text.

    Returns:
        List[str]: A list of text chunks.
    """
    return text.split(delimiter)


def find_repeated_words(text: str, language: str = "english") -> Dict[str, int]:
    """Find and count repeated words in a text.

    Args:
        text (str): The input text to search for repeated words.

    Returns:
        Dict[str, int]: A dictionary where keys are repeated words and values are their counts.
    """

    words = [
        tokenize_text(
            text.lower(),
            by="word",
            language=language,
            preserve_line=False,
        )
    ]
    return dict(Counter(word for word in words if words.count(word) > 1))


def normalize_text(entry: str, lines_sep: str = "\n\n") -> str:
    """Convert text to lowercase and remove extra whitespace.
    Lines are preserved

    Args:
        text (str): The input text to normalize.
        lines_sep (str, optional): what will be used to divide the lines,
        "\\n\\n" will keep a paragraph style, while " " will make everything
        in a single line or "\n" a single line break per non-empty line.
    Returns:
        str: The normalized text.
    """
    entry = simplify_quotes(entry)
    return f"{lines_sep}".join(
        [re.sub(r"\s+", " ", x) for x in entry.splitlines() if x.strip()]
    )


def remove_non_printable(entry: str) -> str:
    """Remove non-printable characters from a text.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The text with non-printable characters removed.
    """
    from string import printable

    return "".join([x for x in entry if x in printable])


def split_by_paragraph(text: str) -> List[str]:
    """Split text into paragraphs.

    Args:
        text (str): The input text to split.

    Returns:
        List[str]: A list of paragraphs from the text.
    """
    text = re.sub(r"\n\n+", "\n\n", text)
    return [x.rstrip() for x in text.splitlines() if x.strip()]


def extract_hashtags(entry: str) -> list[str]:
    """Extract hashtags from a text.

    Args:
        text (str): The input text from which to extract hashtags.

    Returns:
        list[str]: A list of hashtags found in the text.
    """
    return re.findall(r"#\w+", entry)


def extract_mentions(entry: str) -> list[str]:
    """Extract mentions (e.g., @user) from a text.

    Args:
        text (str): The input text from which to extract mentions.

    Returns:
        list[str]: A list of mentions found in the text.
    """
    return re.findall(r"@\w+", entry)


def count_sentences(entry: str) -> int:
    """Count the number of sentences in a text.

    Args:
        text (str): The input text to analyze.

    Returns:
        int: The number of sentences in the text.
    """
    split_text = _blob_split(entry)
    return len(split_text)


def extract_keywords(
    entries: Union[str, List[str]],
    top_n: int = 5,
    return_scores: bool = False,
    allowed_pos: set[str] = {"NOUN", "ADJ"},
    ngram_range: Tuple[int, int] = (1, 2),
) -> Union[List[str], List[Tuple[str, float]]]:
    """
    Extract top-N keywords with highest TF-IDF scores after POS filtering and lemmatization.

    Args:
        entries (str | List[str]): One or more input documents.
        top_n (int): Number of keywords to return.
        return_scores (bool): Whether to return (keyword, score) pairs.
        allowed_pos (set[str]): POS tags to allow (e.g., {"NOUN", "ADJ"}).
        ngram_range (tuple): ngram range for vectorizer.

    Returns:
        List[str] or List[Tuple[str, float]]: Keywords or (keyword, score) pairs.
    """
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer

    if isinstance(entries, str):
        entries = [entries]

    # Preprocess texts using spaCy
    processed = [" ".join(spacy_tokenizer(doc, allowed_pos)) for doc in entries]

    try:
        vectorizer = TfidfVectorizer(ngram_range=ngram_range)
        tfidf_matrix = vectorizer.fit_transform(processed)
    except ValueError:
        return []

    # Compute average TF-IDF score across all docs
    tfidf_means = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_indices = tfidf_means.argsort()[::-1][:top_n]
    features = vectorizer.get_feature_names_out()

    if return_scores:
        return [(features[i], float(tfidf_means[i])) for i in top_indices]
    return [features[i] for i in top_indices]


def formatter(entry: str, width: int) -> str:
    """Format text to fit a certain width.

    Args:
        text (str): The input text to format.
        width (int): The maximum width of each line in the formatted text.

    Returns:
        str: The formatted text.
    """
    import textwrap

    return textwrap.fill(entry, width)


def count_words(entry: str, language: str = "english") -> int:
    """Count the number of words in a text.

    Args:
        text (str): The input text to analyze.

    Returns:
        int: The total word count in the text.
    """
    tokenized_text = tokenize_text(
        entry, by="word", language=language, preserve_line=False
    )
    return len(tokenized_text)


def extract_keys(entry: str) -> list | list[str]:
    # Use a regular expression to find all occurrences of {key} in the string
    keys = re.findall(r"\{(\w+)\}", entry)
    return keys


def find_in_text(
    entry: str,
    has_any: Union[str, Sequence[str]],
    force_lower_case: bool = False,
):
    """Basically the reverse of **in** function, it can be used to locate if **sources** contains anything from the **has_any** into it.

    Args:
        sources (str):
            Target string to be checked if has any of the provided keys.
        has_any (str | list[str]):
            The string or list of strings to be checked if they are or not in the text.
            If its a string each letter will be checked, if its a list of string, then each word in the list will be checked instead.
        force_lower_case (bool, optional):
            If true will set everything to lower-case (both source and has_any).
            This is useful for tasks that dont require a case-sensitive scan. Defaults to False.

    Returns:
        bool: If any key was found will be returned as true, otherwise False.
    """
    if not entry or not has_any:
        return False

    if isinstance(has_any, (list, tuple)) and has_any:
        has_any = [
            x.lower() if force_lower_case else x for x in has_any if isinstance(x, str)
        ]
        if not has_any:
            return False

    if force_lower_case:
        entry = entry.lower()
        if is_str(has_any):
            has_any = has_any.lower()  # type: ignore

    for elem in has_any:
        if elem in entry:
            return True
    return False


def unescape(
    entry: Union[str, bytes], errors: Literal["strict", "ignore"] = "strict"
) -> str:
    """
    Unescapes the given string.

    Args:
        entry (str, bytes): The input string.

    Raises:
        Assertion: If entry is not a valid string or bytes.

    Returns:
        (str, bytes): The unescaped entry same type as the input.

    Example:

        ```python

        results = unescape("This is the first line.\\\\n\\\\nThis is the last line!")
        # results = "This is the first line.\\n\\nThis is the last line!"

        ```
    """
    assert isinstance(
        entry, (str, bytes)
    ), "The input should be a valid string or bytes."
    if isinstance(entry, bytes):
        return entry.decode(encoding="unicode-escape", errors=errors).encode(
            errors=errors
        )
    return entry.encode(errors=errors).decode("unicode-escape", errors=errors)


def escape(
    entry: Union[str, bytes],
    errors: Literal["strict", "ignore"] = "strict",
    encoding: Union[
        str, Literal["utf-8", "ascii", "unicode-escape", "latin-1"]
    ] = "utf-8",
) -> Union[str, bytes]:
    """
    Escapes the given string.

    Args:
        entry (str, bytes): The input string.

    Raises:
        Assertion: If entry is not a valid string or bytes.

    Returns:
        (str, bytes): The escaped entry same type as the input.

    Example:

        ```python

        results = escape("This is the first line.\\n\\nThis is the last line!")
        # results = "This is the first line.\\\\n\\\\nThis is the last line!"

        ```
    """
    assert isinstance(
        entry, (str, bytes)
    ), "The input should be a valid string or bytes."
    if isinstance(entry, str):
        return entry.encode(encoding="unicode-escape", errors=errors).decode(
            errors=errors, encoding=encoding
        )
    return entry.decode(errors=errors, encoding=encoding).encode(
        encoding="unicode-escape", errors=errors
    )


def replace_pos_tags(
    entry: str,
    target_pos_tags: List[str],
    replacer: str,
    language: str = "english",
    preserve_line: bool = True,
) -> str:
    """
    Replace words in `text` that match specific POS tags with `replacer`.

    Args:
        text (str): The input text containing words.
        target_pos_tags (List[str]): List of POS tags to replace.
        replacer (str): The string to replace the words with.

    Returns:
        str: The modified text with the specified words replaced.
    """

    from nltk.tag import PerceptronTagger
    from string import whitespace, punctuation

    # Remove f-strings to avoid conflicts
    filtered_text = entry.replace("{}", "")

    all_fstrings = extract_keys(entry)
    if all_fstrings:
        filtered_text = recursive_replacer(
            filtered_text, {key: "" for key in all_fstrings}
        )

    # Tokenize and tag parts of speech
    tokens = tokenize_text(
        filtered_text,
        by="word",
        language=language,
        preserve_line=preserve_line,
    )
    tagged_tokens = PerceptronTagger().tag(tokens)
    tlstrings = list(whitespace) + list(punctuation)
    # Replace words based on POS tags
    replacers = {
        f"{start_txt}{word}{end_txt}": f"{start_txt}{replacer}{end_txt}"
        for word, pos in tagged_tokens
        if pos in target_pos_tags
        for start_txt in tlstrings
        for end_txt in tlstrings
    }

    return recursive_replacer(entry, replacers) if replacers else entry
