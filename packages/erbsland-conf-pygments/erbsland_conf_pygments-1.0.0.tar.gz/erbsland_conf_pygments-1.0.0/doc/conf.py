#  Copyright (c) 2025 Tobias Erbsland - https://erbsland.dev
#  SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

# -- Project information -----------------------------------------------------
project = "Pygments Lexer for the Erbsland Configuration Language"
copyright = "2025, Tobias Erbsland - Erbsland DEV"
author = "Tobias Erbsland - Erbsland DEV"
release = "1.0"

# -- General configuration ---------------------------------------------------
extensions = ["sphinx_rtd_theme", "sphinx_design", "sphinx_copybutton"]
templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = []
html_template_path = []
html_css_files = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css"]

# pygments_style = "_pygments.debug_style.DebugStyle"
pygments_style = "colorful"


# -- Add the syntax highlighter ---------------------------------------------
def setup(app):
    from erbsland.conf_pygments.lexer import ElclLexer

    app.add_lexer("erbsland-conf", ElclLexer)
