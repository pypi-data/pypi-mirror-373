# Pygments Lexer for the Erbsland Configuration Language

This repository provides a **Pygments lexer** for the *Erbsland Configuration Language (ELCL)*. It is based on the original lexer from the [Erbsland Configuration Language Parser for Python](https://github.com/erbsland-dev/erbsland-py-conf).

## Installation

The package is available on [PyPI](https://pypi.org/project/erbsland-conf-pygments/):

```bash
pip install erbsland-conf-pygments
```

## Usage

Once installed, the lexer can be used in your Pygments configuration. It is available under the following aliases:

- `elcl`
- `erbsland-conf`
- `erbsland-config`
- `erbsland-configuration`

In most cases, it will also be selected automatically for files with the extension **`.elcl`**.

## Requirements

- Python **3.12** or newer
- [`erbsland-conf`](https://github.com/erbsland-dev/erbsland-py-conf)
- [`pygments`](https://pypi.org/project/Pygments/)

## License

Copyright © 2025  
[Tobias Erbsland / Erbsland DEV](https://erbsland.dev/)

This project is licensed under the **Apache License, Version 2.0**. You may obtain a copy at: [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

The software is distributed on an *“AS IS”* basis, without warranties or conditions of any kind. See the [LICENSE](./LICENSE) file for full details.
