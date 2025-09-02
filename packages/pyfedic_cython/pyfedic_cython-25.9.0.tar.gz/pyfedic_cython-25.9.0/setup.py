# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfedic_cython']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyfedic_cython',
    'version': '25.9.0',
    'description': 'Digital Image (2D/3D) Correlation Software - CYTHON module',
    'long_description': '# pyFEDIC : Digital Image (2D/3D) Correlation Software\n\npyFEDIC is a DIC software using global approach with finite element shape functions to describe the displacement field. It allows to perform 2D DIC and 3D DIC also called DVC (V stand for volume).\n\nThis software is a pure python library and offer a simple command line to run analysis with a few parameters as input.\n\nIt can be directly installed using pip:\n\n```console\n$ pip install pyfedic\n```\n\nFor more information, visit https://sourcesup.renater.fr/www/pyfedic/html/index.html\n\n\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8298429.svg)](https://doi.org/10.5281/zenodo.8298429)\n\n',
    'author': 'Joël Lachambre',
    'author_email': 'joel.lachambre@cnrs.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://sourcesup.renater.fr/www/pyfedic/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11,<3.13',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
