#  Copyright (c) 2025 Tobias Erbsland - https://erbsland.dev
#  SPDX-License-Identifier: Apache-2.0


from pygments.style import Style
from pygments.token import (
    Token,
    Keyword,
    Name,
    Literal,
    String,
    Number,
    Operator,
    Punctuation,
    Comment,
    Error,
    Generic,
    Whitespace,
)


class DebugStyle(Style):
    default_style = ""
    styles = {
        # Base & errors
        Token: "bg:#ffffff #000000",
        Error: "bold #ffffff bg:#ff0044",
        # Whitespace (visible if HTML formatter shows it)
        Whitespace: "bg:#f5f5f5 #aaaaaa",
        # Comments
        Comment: "italic #444444 bg:#eeeeee",
        Comment.Single: "italic #444444 bg:#eeeeee",
        Comment.Multiline: "italic #444444 bg:#eaeaea",
        Comment.Hashbang: "bold italic #333333 bg:#e0e0e0",
        Comment.Preproc: "italic #333333 bg:#ddddee",
        # Names (identifiers)
        Name: "#000000 bg:#d1ffd6",
        Name.Attribute: "bold #000000 bg:#b7f5c0",  # config keys
        Name.Builtin: "#000000 bg:#b2ffb9",
        Name.Function: "bold #000000 bg:#a0f5b1",
        Name.Class: "bold #000000 bg:#79e5a0",
        Name.Decorator: "#000000 bg:#59d58b",
        Name.Label: "bold #000000 bg:#d0f0ff",  # info-string / code fence lang
        Name.Namespace: "#000000 bg:#c7f7e9",
        # Operators & punctuation
        Operator: "#000000 bg:#ccffff",
        Operator.Word: "bold #000000 bg:#bff8ff",
        Punctuation: "#000000 bg:#e0ffff",
        # Keywords (kept for completeness)
        Keyword: "bold #000000 bg:#ffd1dc",
        Keyword.Namespace: "bold #000000 bg:#ffc1d2",
        # Literals
        Literal: "#000000 bg:#d1d9ff",
        Literal.Boolean: "bold #000000 bg:#cddcff",
        Literal.Date: "#000000 bg:#cbd9ff",
        # Numbers
        Number: "#ff0000 bg:#c4b5fd",
        Number.Integer: "#000000 bg:#bda7fc",
        Number.Hex: "#000000 bg:#e0a7fc",
        Number.Bin: "#000000 bg:#ffa7fc",
        Number.Float: "#000000 bg:#b399fb",
        # Strings & delimiters
        String: "#000000 bg:#fff3b0",
        String.Double: "#000000 bg:#ffe98f",
        String.Single: "#000000 bg:#ffe07a",
        String.Delimiter: "bold #000000 bg:#ffd86a",  # opening/closing fences/quotes
        String.Backtick: "#000000 bg:#ffd35c",  # inline/fenced code content
        String.Regex: "#000000 bg:#ffd8f0",
        String.Other: "#000000 bg:#ffefc7",
        String.Doc: "italic #000000 bg:#fff7c8",
        String.Escape: "bold #000000 bg:#ffe0a0",
        # Generic doc parts
        Generic.Heading: "bold #000000 bg:#ffd6a5",
        Generic.Subheading: "bold #000000 bg:#fdffb6",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
    }
