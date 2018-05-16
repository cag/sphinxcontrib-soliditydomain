import os
import posixpath

from sphinx.ext.autodoc import Documenter
from .parser import parse_sol


# https://stackoverflow.com/a/16891418
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def build_source_index(app):
    lookup_path = app.env.config.autodoc_lookup_path

    for root, dirs, files in os.walk(lookup_path):
        for name in files:
            if os.path.splitext(name)[1].lower() == '.sol':
                print(
                    '---',
                    remove_prefix(
                        posixpath.join(
                            posixpath.relpath(root, lookup_path),
                            name),
                        './'),
                    '---',
                )
                parse_sol(os.path.join(root, name))


class ContractDocumenter(Documenter):
    objtype = 'contract'

    def parse_name(self):
        return True

    def import_object(self):
        return False


all_solidity_documenters = (ContractDocumenter,)
