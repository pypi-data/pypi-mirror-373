from setuptools import setup
from os import environ

version = '1.0.0'
if 'VERSION' in environ.keys():
    version = environ['VERSION']

doc_url = 'https://neemgrp.univ-nantes.io/py3toolset/html'
api_doc_url = doc_url + '/api.html'
mods = ['bash_autocomp', 'cmd_interact', 'dep', 'file_backup',
        'fs', 'nmath', 'tuple_file', 'txt_color']
nmods = len(mods)
mod_links = [f'[{mod}]({api_doc_url}#module-{imod})' for imod, mod in enumerate(mods)]

setup(
    name='py3toolset',
    version=version,
    packages=['py3toolset'],
    url='',
    description='Python utility modules.',
    classifiers=['License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 3',
                 'Topic :: Software Development'],
    install_requires=['numpy>=2'],
    package_data={'py3toolset': ['LICENSE.md']},
    license="3-clause BSD 2.0",
    long_description_content_type='text/markdown',
    long_description= f"""Python collection of utility modules: {", ".join(mod_links)}...

This package software engineering has been funded by the [Laboratoire de Planétologie et Géosciences](https://lpg-umr6112.fr/), Nantes (France).
    """
)
