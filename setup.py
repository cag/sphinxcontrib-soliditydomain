from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sphinxcontrib-soliditydomain',
    version='0.3.0',
    description='Solidity domain for Sphinx',

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/cag/sphinxcontrib-soliditydomain',

    author='Alan Lu',
    author_email='alan@gnosis.pm',

    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='sphinx solidity domain contrib documentation generator plugin',

    packages=['sphinxcontrib.soliditydomain'],

    install_requires=[
        'antlr4-python3-runtime',
        'peewee',
    ],

    package_data={
        'sphinxcontrib.soliditydomain': ['Solidity.g4'],
    },
)
