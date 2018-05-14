import os

from sphinx.ext.autodoc import Documenter
from .parser import parse_sol


def build_source_index(app):
    lookup_path = app.env.config.autodoc_lookup_path
    for root, dirs, files in os.walk(lookup_path):
        for name in files:
            if name.lower().endswith('.sol'):
                with open(os.path.join(root, name)) as file:
                    src = file.read()
                    print(parse_sol(src))


class ContractDocumenter(Documenter):
    objtype = 'contract'

    def parse_name(self):
        return True

    def import_object(self):
        return False


all_solidity_documenters = (ContractDocumenter,)
