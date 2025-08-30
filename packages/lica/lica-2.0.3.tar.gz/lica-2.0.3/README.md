# lica
 
 Assorte collection of source code with utilities (functions, classes, etc.) 
 used in other projects at LICA (UCM) or STARS4ALL

## Installation

### Stable version

```bash
pip install lica
```

### Development version using UV 
This must be handed a source code in your client package with one of the two commands below.

```bash
uv add git+https://github.com/guaix-ucm/lica --branch main
uv add git+https://github.com/guaix-ucm/lica --tag x.y.z
```

***Note:***
lica library uses different modules in its subpackages, so you must use one or more the following extras:
* lica[jinja]
* lica[tabular]
* lica[raw]
* lica[sqlalchemy]
* lica[aiosqlalchemy]
* lica[photometer]
* lica[lab]