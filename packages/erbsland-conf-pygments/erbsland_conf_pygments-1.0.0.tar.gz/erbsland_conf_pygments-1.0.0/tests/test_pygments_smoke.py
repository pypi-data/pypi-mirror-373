#  Copyright (c) 2025 Tobias Erbsland - https://erbsland.dev
#  SPDX-License-Identifier: Apache-2.0


import pathlib

import pytest
from pygments import highlight
from pygments.formatters import HtmlFormatter

from erbsland.conf_pygments.lexer import ElclLexer


def test_pygments_highlight_smoke():
    example_path = pathlib.Path(__file__).parent / "examplefiles" / "quick-intro.elcl"
    text = example_path.read_text(encoding="utf-8")

    # Smoke test: run Pygments highlight with our lexer. It should not raise and produce output.
    formatter = HtmlFormatter()
    try:
        result = highlight(text, ElclLexer(), formatter)
    except Exception as exc:
        pytest.fail(f"Pygments highlighting raised an exception: {exc}")
    assert isinstance(result, str)
    assert result.strip() != ""
