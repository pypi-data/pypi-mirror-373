import re
from pathlib import Path
from typing import Dict

from docx2python import docx2python

from openpecha.config import get_logger
from openpecha.exceptions import EmptyFileError

logger = get_logger(__name__)


def normalize_whitespaces(text: str):
    """
    If there are spaces or tab between newlines, it will be removed.
    """
    return re.sub(r"\n[\s\t]+\n", "\n\n", text)


def normalize_newlines(text: str):
    """
    If there are more than 2 newlines continuously, it will replace it with 2 newlines.
    """
    return re.sub(r"\n{3,}", "\n\n", text)


def normalize_text(text: str):
    text = normalize_whitespaces(text)
    text = normalize_newlines(text)
    text = text.strip()
    return text


def read_docx(docx_file: str | Path, ignore_footnotes: bool = True) -> str:
    """
    Read docx file as text.
    """
    text = docx2python(docx_file).text
    if not text:
        logger.warning(
            f"The docx file {str(docx_file)} is empty or contains only whitespace."
        )
        raise EmptyFileError(
            f"[Error] The document '{str(docx_file)}' is empty or contains only whitespace."
        )

    text = normalize_text(text)
    if ignore_footnotes:
        text = remove_footnote(text)

    logger.info(f"Text extracted from docx file: {text}")
    return text


def remove_footnote(text: str) -> str:
    """
    Input: text extracted from docx file
    Output: text without footnote
    """

    # Remove footnote numbers
    text = re.sub(r"----footnote\d+----", "", text)

    # Remove footnote content
    parts = text.split("\n\n")
    res = []
    for part in parts:
        # Use regex to check if part starts with 'footnote' followed by digits
        if not re.match(r"^footnote\d+\)", part.strip()):
            res.append(part)
    text = "\n\n".join(res)
    return text


def extract_numbered_list(docx_file: str | Path) -> Dict[str, str]:
    """
    Extract number list from the docx file.

    Example Output:>
        {
            '1': 'དབུ་མ་དགོངས་པ་རབ་གསལ་ལེའུ་དྲུག་པ་བདེན་གཉིས་སོ་སོའི་ངོ་བོ་བཤད་པ།། ',
            '2': 'གསུམ་པ་ལ་གཉིས། ཀུན་རྫོབ་ཀྱི་བདེན་པ་བཤད་པ་དང་། ',
            '3': 'དེས་གང་ལ་སྒྲིབ་ན་ཡང་དག་ཀུན་རྫོབ་འདོད་ཅེས་པས་ཡང་དག་པའི་དོན་ལ་སྒྲིབ་པས་ཀུན་རྫོབ་བམ་སྒྲིབ་བྱེད་དུ་འདོད་ཅེས་པ་སྟེ། །',
            ...
        }
    """
    text = read_docx(docx_file)

    number_list_regex = r"^(\d+)\)\t(.*)"

    res: Dict[str, str] = {}
    for para_text in text.split("\n\n"):
        match = re.match(number_list_regex, para_text)
        if match:
            number = match.group(1)
            text = match.group(2)
            res[number] = text

    logger.info(f"Numbered List extracted from the docx file: {res}")

    return res
