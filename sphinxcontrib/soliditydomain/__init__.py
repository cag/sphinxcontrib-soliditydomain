import os

from .domain import SolidityDomain
from .documenters import all_solidity_documenters, build_source_index

def setup(app):
    app.add_domain(SolidityDomain)
    for documenter in all_solidity_documenters:
        app.add_autodocumenter(documenter)

    app.add_config_value('autodoc_lookup_path', os.path.join('..', 'contracts'), True)

    app.connect('builder-inited', builder_inited_handler)

def builder_inited_handler(app):
    build_source_index(app)
