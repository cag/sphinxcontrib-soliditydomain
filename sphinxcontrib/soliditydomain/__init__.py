import os

from .domain import SolidityDomain
from .documenters import all_solidity_documenters, build_source_index


def setup(app):
    app.add_domain(SolidityDomain)
    for documenter in all_solidity_documenters:
        app.add_autodocumenter(documenter)

    app.add_config_value('autodoc_lookup_path',
                         os.path.join('..', 'contracts'), 'env')

    app.connect('builder-inited', builder_inited_handler)
    app.connect('env-before-read-docs', read_all_docs)


def builder_inited_handler(app):
    build_source_index(app)


def read_all_docs(app, env, doc_names):
    """Add all found docs to the to-be-read list, because we have no way of
    telling which ones reference Solidity that might have changed.

    Otherwise, builds go stale until you touch the stale RSTs or do a ``make
    clean``.

    This is straight-up lifted from `sphinx-js <https://github.com/erikrose/sphinx-js#sphinx-js>`_.

    """
    doc_names[:] = env.found_docs
