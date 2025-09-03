#  Copyright (c) 2025 Tobias Erbsland - https://erbsland.dev
#  SPDX-License-Identifier: Apache-2.0
import re
from typing import Any

from pygments.lexer import Lexer
from pygments import token

from erbsland.conf.syntax.lexer import SyntaxLexer

RE_BASE_NUMBER = re.compile(r"[-+]?0([xXbB])")
RE_ESCAPE_SEQUENCE = re.compile(r"(?i)\\(u[a-f0-9]{4}|u\{[a-f0-9]{1,8}\}|.)")
TOKEN_MAPPING: dict[str, Any] = {
    # Control / errors
    "Error": token.Error,
    # Whitespace
    "LineBreak": token.Whitespace,
    "Spacing": token.Whitespace,
    "Indentation": token.Whitespace,
    "Skipped": token.Whitespace,
    # Comments
    "Comment": token.Comment.Single,
    # Names & keys
    # Use Attribute to distinguish configuration keys from other names
    "Name": token.Name.Attribute,
    # Separators & structure
    # Assignment-like separators should read as operators
    "NameValueSeparator": token.Operator,
    # Commas and list separators are punctuation
    "ValueListSeparator": token.Punctuation,  # was Operator
    "MultiLineValueListSeparator": token.Punctuation,  # was Operator
    # Dotted access / path separator is punctuation
    "NamePathSeparator": token.Punctuation,  # was Operator
    # Numbers & booleans
    "Integer": token.Number.Integer,
    "Float": token.Number.Float,
    "Boolean": token.Literal.Boolean,
    # Text (single/multi-line)
    "Text": token.String.Double,
    "MultiLineTextOpen": token.String.Delimiter,
    "MultiLineTextClose": token.String.Delimiter,
    "MultiLineText": token.String.Double,
    # Inline & fenced code
    "Code": token.String.Backtick,
    "MultiLineCodeOpen": token.String.Delimiter,
    "MultiLineCodeLanguage": token.Name.Label,  # highlight info string distinctly
    "MultiLineCodeClose": token.String.Delimiter,
    "MultiLineCode": token.String.Backtick,
    # Regular expressions
    "RegEx": token.String.Regex,
    "MultiLineRegexOpen": token.String.Delimiter,
    "MultiLineRegexClose": token.String.Delimiter,
    "MultiLineRegex": token.String.Regex,
    # Bytes blocks
    "Bytes": token.String.Other,
    "MultiLineBytesOpen": token.String.Delimiter,
    "MultiLineBytesFormat": token.Name.Builtin,
    "MultiLineBytesClose": token.String.Delimiter,
    "MultiLineBytes": token.String.Other,
    # Date/time literals
    "Date": token.Literal.Date,
    "Time": token.Literal.Date,
    "DateTime": token.Literal.Date,
    "TimeDelta": token.Literal.Date,
    # Section delimiters (maps/lists)
    "SectionMapOpen": token.Punctuation,
    "SectionMapClose": token.Punctuation,
    "SectionListOpen": token.Punctuation,
    "SectionListClose": token.Punctuation,
}


def _tokenize_text(text: str):
    """Tokenize *text* and return a list of tuples (start_index, token_type)."""
    pos = 0
    while match := RE_ESCAPE_SEQUENCE.search(text, pos):
        if match.start() > pos:
            yield pos, token.String.Double, text[pos : match.start()]
        if match.group(1)[0].lower() in ("\\", '"', "$", "n", "r", "t", "u"):
            yield match.start(), token.String.Escape, match.group()
        else:
            yield match.start(), token.Error, match.group()
        pos = match.end()
    if pos < len(text):
        yield pos, token.String.Double, text[pos:]
    return None


class ElclLexer(Lexer):
    """Pygments Lexer for the Erbsland Configuration Language."""

    name = "Erbsland Configuration Language"
    aliases = ["elcl", "erbsland-conf", "erbsland-config", "erbsland-configuration"]
    filenames = ["*.elcl"]
    mimetypes = ["text/x-elcl"]

    def __init__(self, **options):
        super().__init__(**options)

    def get_tokens_unprocessed(self, text: str):
        syntax_lexer = SyntaxLexer(text)
        for lexer_token in syntax_lexer.tokens():
            pygments_token = token.Text
            match lexer_token.token_type:
                case "Integer":
                    if match := RE_BASE_NUMBER.match(lexer_token.raw_text):
                        if match.group(1).lower() == "x":
                            pygments_token = token.Number.Hex
                        elif match.group(1).lower() == "b":
                            pygments_token = token.Number.Bin
                    else:
                        pygments_token = token.Number.Integer
                case "Name":
                    pygments_token = token.Name.Attribute
                    if lexer_token.value.is_meta():
                        pygments_token = token.Name.Builtin
                    elif lexer_token.value.is_text():
                        pygments_token = token.Name.Label
                case "Text" | "MultiLineText":
                    yield from _tokenize_text(lexer_token.raw_text)
                    continue
                case _:
                    pygments_token = TOKEN_MAPPING.get(lexer_token.token_type, token.Text)
            yield lexer_token.begin.character_index, pygments_token, lexer_token.raw_text
        return None
