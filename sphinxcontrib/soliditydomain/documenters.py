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


class SolidityObjectDocumenter(Documenter):
    domain = 'sol'

    def get_sourcename(self):
        return 'foo.sol'

    def add_directive_header(self):
        domain = getattr(self, 'domain', 'sol')
        directive = getattr(self, 'directivetype', self.objtype)
        sourcename = self.get_sourcename()

        self.add_line('.. {domain}:{directive}:: {signature}'.format(
            domain=domain, directive=directive, signature='SOMETHING'
        ), sourcename)

        if self.options.noindex:
            self.add_line(u'   :noindex:', sourcename)

    def add_content(self, more_content):
        """Add content from source docs and user."""
        pass

    def document_members(self, all_members=False):
        # type: (bool) -> None
        """Generate reST for member documentation.

        If *all_members* is True, do all members, else those given by
        *self.options.members*.
        """
        pass

    def generate(self, more_content=None, all_members=False):
        # type: (Any, str, bool, bool) -> None
        """Generate reST for the object given by *self.name*, and possibly for
        its members.

        If *more_content* is given, include that content.
        If *all_members* is True, document all members.
        """

        print(self.name)
        print('...')
        print('...')

        # TODO: find info about what is requested
        # TODO: collect comments

        sourcename = self.get_sourcename()

        # make sure that the result starts with an empty line.  This is
        # necessary for some situations where another directive preprocesses
        # reST and no starting newline is present
        self.add_line('', sourcename)

        # generate the directive header and options, if applicable
        self.add_directive_header()
        self.add_line('', sourcename)

        # make sure content is indented
        # TODO: consider adding a source unit directive
        self.indent += self.content_indent

        # add all content (from docstrings, attribute docs etc.)
        self.add_content(more_content)

        # document members, if possible
        self.document_members(all_members)


class ContractDocumenter(SolidityObjectDocumenter):
    objtype = 'contract'


def method_stub(self):
    raise NotImplementedError


for method_name in (
    'parse_name', 'import_object', 'get_real_modname', 'check_module',
    'format_args', 'format_name', 'format_signature', 'get_doc', 'process_doc',
    'get_object_members', 'filter_members',
):
    setattr(ContractDocumenter, method_name, method_stub)

all_solidity_documenters = (ContractDocumenter,)
