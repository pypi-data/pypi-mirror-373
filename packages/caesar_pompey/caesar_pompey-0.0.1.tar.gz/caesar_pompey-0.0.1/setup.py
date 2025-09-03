# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['caesar_pompey']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['caesar = caesar_pompey.caesar:main',
                     'pompey = caesar_pompey.pompey:main']}

setup_kwargs = {
    'name': 'caesar-pompey',
    'version': '0.0.1',
    'description': 'Cipher and decipher message using caesar code.',
    'long_description': '# caesar_pompey\n\nCipher and deciper message using the Caesar algorithm.\n\n## Installation\n\n```bash\npoetry lock\npoetry install\n```\n',
    'author': 'Maxime Haselbauer',
    'author_email': 'maxime.haselbauer@googlemail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
