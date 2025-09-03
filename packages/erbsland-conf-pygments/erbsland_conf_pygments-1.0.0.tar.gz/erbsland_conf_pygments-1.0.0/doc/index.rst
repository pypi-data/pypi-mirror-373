Pygments Lexer for the Erbsland Configuration Language
======================================================

This package provides a **Pygments Lexer** for the *Erbsland Configuration Language (ECL)*.  
It is built directly on top of the original lexer from the *Erbsland Configuration Language Parser for Python*.  
Because of this, it fully supports all features of the language and produces a rich set of tokens for precise syntax highlighting.

Installation
============

You can install the lexer from PyPI with:

.. code-block:: shell

    pip install erbsland-conf-pygments

Demo
====

Below you can see a complete language overview.  
This example also includes cases with errors. Please note that name conflicts and name-path issues are **not** flagged as errors by the lexer itself.

.. literalinclude:: /../tests/examplefiles/language-overview.elcl
    :language: erbsland-conf
    :force:

More Topics
===========

.. toctree::
    :maxdepth: 3

    chapters/examples
    chapters/installation
    chapters/requirements
    chapters/license

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
