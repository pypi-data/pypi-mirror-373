# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fast']

package_data = \
{'': ['*']}

install_requires = \
['pybgl>=0.11.2']

setup_kwargs = {
    'name': 'find-abstract-syntax-tree',
    'version': '0.2.1',
    'description': 'Python3 module inferring Abstract Syntax Trees (AST) representing regular expressions (RE) given a set of positive examples.',
    'long_description': '# fAST (find Abstract Syntax Tree)\n\n[![PyPI](https://img.shields.io/pypi/v/find_abstract_syntax_tree.svg)](https://pypi.python.org/pypi/find-abstract-syntax-tree)\n[![Build](https://github.com/nokia/find-abstract-syntax-tree/workflows/build/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/build.yml)\n[![Documentation](https://github.com/nokia/find-abstract-syntax-tree/workflows/docs/badge.svg)](https://github.com/nokia/find-abstract-syntax-tree/actions/workflows/docs.yml)\n[![ReadTheDocs](https://readthedocs.org/projects/find-abstract-syntax-tree/badge/?version=latest)](https://find-abstract-syntax-tree.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/nokia/find-abstract-syntax-tree/branch/main/graph/badge.svg?token=I7FEGOOYFG)](https://codecov.io/gh/nokia/find-abstract-syntax-tree)\n\n## Overview\n\n[find-abstract-syntax-tree](https://github.com/nokia/find-abstract-syntax-tree) is a [Python 3](http://python.org/) implemention of the fAST algorithm. This algorithm aims at inferring a regular expression from a finite set of positive examples.\n\nThe fAST algorithm is described in:\n\n[[ICGI\'2023](https://icgi2023.inria.fr/)] fAST: regular expression inference from positive examples using Abstract Syntax Trees, [Maxime Raynal](https://raynalm.github.io/), [Marc-Olivier Buob](https://www.bell-labs.com/about/researcher-profiles/marc-olivier-buob/), [Georges Quénot](http://mrim.imag.fr/georges.quenot/).\n\nThis module is built on top of:\n* [numpy](https://pypi.org/project/numpy/);\n* [pybgl](https://pypi.org/project/pybgl/), a lightweight graph library.\n\n## Quick start\n\nInstall the package through PIP:\n```bash\npip3 install find-abstract-syntax-tree\n```\nIn your python interpreter, run:\n```python\nfrom fast import fast\n\nresults = fast(["abc", "abcabc", "abcabcabc"])\nfor (score, ast) in results:\n    print(score, ast.to_infix_regexp_str())\n```\n\n## Links\n\n* [Installation](https://github.com/nokia/find-abstract-syntax-tree/blob/master/docs/installation.md)\n* [Documentation](https://find-abstract-syntax-tree.readthedocs.io/en/latest/)\n* [Coverage](https://app.codecov.io/gh/nokia/find-abstract-syntax-tree)\n* [Wiki](https://github.com/nokia/find-abstract-syntax-tree/wiki)\n\n## License\n\nThis project is licensed under the [BSD-3-Clause license](https://github.com/nokia/find-abstract-syntax-tree/blob/master/LICENSE).\n',
    'author': 'Maxime Raynal',
    'author_email': 'maxime.raynal@nokia.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
