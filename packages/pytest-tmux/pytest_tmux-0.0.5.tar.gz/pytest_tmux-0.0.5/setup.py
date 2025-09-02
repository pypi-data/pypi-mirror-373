# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_tmux']

package_data = \
{'': ['*']}

install_requires = \
['libtmux==0.20']

entry_points = \
{'pytest11': ['pytest-tmux = pytest_tmux.plugin']}

setup_kwargs = {
    'name': 'pytest-tmux',
    'version': '0.0.5',
    'description': 'A pytest plugin that enables tmux driven tests',
    'long_description': '# pytest-tmux\n\n[![PyPI version](https://img.shields.io/pypi/v/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)\n\n[![Python versions](https://img.shields.io/pypi/pyversions/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)\n\nA pytest plugin that enables tmux driven tests\n\nThis plugin is intend to help users who want to test interrative cli.\n\nWhen using `tmux` fixture it basically :\n\n- creates a tmux server (socket created in pytest tmpdir)\n- creates a session automatically\n- attach to the window automatically\n- attach to the pane automatically\n\n## Warnings\n\n**Until a stable release, it is greatly encouraged to specify a strict version if\nyou use this tool in your CI since it is in its early development and could be\ngreatly changed between version.**\n\n## Docs\n\n[https://pytest-tmux.readthedocs.io/](https://pytest-tmux.readthedocs.io)\n\n## Features\n\n- Enable tmux driven tests\n- Enable screen assertion with retry\n- Enable row assertion with retry\n- Allow to debug tests interactively\n\n## Requirements\n\n- python >= 3.7\n- pytest\n- tmux\n\n## Installation\n\nYou can install "pytest-tmux" via [pip](https://pypi.org/project/pip/)\nfrom [PyPI](https://pypi.org/project):\n\n    $ pip install pytest-tmux\n\n## Configuration capabilities\n\nConfiguration could be set on different level (in order of precedence):\n\n- Server\n    - by overriding tmux_server_config (scope=\'session\') fixture\n    - env var\n    - cli args (see --tmux-* switch with pytest --help)\n- Session\n    - by overriding tmux_session_config fixture\n    - at the test level with tmux_session_cfg marker\n    - dynamically inside test with `tmux.config.session`\n    - env var\n    - cli args (see --tmux-* switch with pytest --help)\n- Assertion\n    - by overriding tmux_assertion_config fixture\n    - at the test level with tmux_assertion_cfg marker\n    - dynamically inside test with `tmux.config.session`\n    - when calling `tmux.screen() / tmux.row()` with `timeout` / `delay` argument\n    - env var\n    - cli args (see --tmux-* switch with pytest --help)\n\n\n## Usage\n\n### Basic example\n\n```python\nimport pytest\nfrom inspect import cleandoc\n\ndef test_assert(tmux):\n    # Set some options before session / windows is started\n    tmux.config.session.window_command=\'env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile\'\n    assert tmux.screen() == \'$\'\n    tmux.send_keys(r\'printf "  Hello World  .\\n\\n"\')\n    expected=r"""\n    $ printf "  Hello World  .\\n\\n"\n      Hello World  .\n\n    $\n    """\n    assert tmux.screen() == cleandoc(expected)\n```\n\n## License\n\nDistributed under the terms of the\n[MIT](http://opensource.org/licenses/MIT) license, "pytest-tmux" is free\nand open source software\n\n## Issues\n\nIf you encounter any problems, please [file an\nissue](https://github.com/rockandska/pytest-tmux/issues) along with a\ndetailed description.\n',
    'author': 'rockandska',
    'author_email': 'yoann_mac_donald@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/rockandska/pytest-tmux',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<=3.11.9999',
}


setup(**setup_kwargs)
