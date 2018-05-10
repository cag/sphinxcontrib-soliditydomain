import re
from docutils import nodes
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import _
from sphinx.roles import XRefRole
from sphinx.util.docfields import Field, GroupedField, TypedField

contract_re = re.compile(
    r'''\s* (\w+)  # name
        (?: \s+ is \s+
            (\w+ (?:\s*,\s* (?:\w+))*)  # parent contracts
        )? \s*''', re.VERBOSE)


class SolidityTypeLike(ObjectDescription):
    def handle_signature(self, sig, signode):
        match = contract_re.fullmatch(sig)
        if match is None:
            raise ValueError

        name, parents_str = match.groups()
        parents = [] if parents_str is None else [
            p.strip()
            for p in parents_str.split(',')]

        signode += nodes.emphasis(text=self.objtype + ' ')
        signode += addnodes.desc_name(text=name)

        if len(parents) > 0:
            signode += nodes.Text(' is ' + ', '.join(parents))

        return name


statevar_re = re.compile(
    r'''\s* ( [\w\s\[\]\(\)=>]+? ) # type
        (?: \b (public|private|internal) )? # visibility
        \s+(\w+) # name
        \s*''', re.VERBOSE)


class SolidityStateVariable(ObjectDescription):
    def handle_signature(self, sig, signode):
        match = statevar_re.fullmatch(sig)

        if match is None:
            raise ValueError

        # normalize type string
        type_str, visibility, name = match.groups()
        type_str = re.sub(r'\s*(\W)', r'\1', type_str)
        type_str = re.sub(r'(\W)\s*', r'\1', type_str)
        type_str = re.sub(r'(\w)\s+(\w)', r'\1 \2', type_str)
        type_str = type_str.replace('mapping(', 'mapping (')
        type_str = type_str.replace('=>', ' => ')

        signode += addnodes.desc_type(text=type_str + ' ')

        if visibility is not None:
            signode += nodes.emphasis(text=visibility + ' ')

        signode += addnodes.desc_name(text=name)

        return name


function_re = re.compile(
    r'''\s* (\w+)?  # name
        \s* \( ([^)]*) \)  # arglist
        \s* ((?:\w+ \s* (?:\([^)]*\))? \s* )*)  # modifiers
        \s*''', re.VERBOSE)


func_arg_re = re.compile(
    r'''\s* ([\w\[\]]+)  # type
        (\s+ (?:storage|memory|indexed))?  # memory location
        (?:\s+ (\w+))?  # name
        \s*''', re.VERBOSE)


def parse_args_into_parameter_list(arglist_str):
    params = addnodes.desc_parameterlist()

    if len(arglist_str.strip()) == 0:
        return params

    argmatches = [func_arg_re.fullmatch(
        arg_str) for arg_str in arglist_str.split(',')]

    if not all(argmatches):
        raise ValueError

    for argmatch in argmatches:
        params += addnodes.desc_parameter(
            text=' '.join(filter(lambda x: x, argmatch.groups())))

    return params


modifier_re = re.compile(r'(\w+)(?:\s*\(([^)]*)\))?')


class SolidityFunctionLike(ObjectDescription):
    doc_field_types = [
        # Field('visibility', label=_('Visibility'), has_arg=False,
        #       names=('vis', 'visibility')),
        # Field('statemutability', label=_('State mutability'), has_arg=False,
        #       names=('statemut', 'statemutability')),
        # GroupedField('modifier', label=_('Modifiers'),
        #              names=('mod', 'modifier')),
        TypedField('parameter', label=_('Parameters'),
                   names=('param', 'parameter', 'arg', 'argument'),
                   typenames=('type',)),
        TypedField('returnvalue', label=_('Returns'),
                   names=('return', 'returns'),
                   typenames=('rtype',)),
    ]

    def handle_signature(self, sig, signode):
        signode.is_multiline = True
        primary_line = addnodes.desc_signature_line(add_permalink=True)
        match = function_re.fullmatch(sig)
        if match is None:
            raise ValueError

        name, arglist_str, modifiers_str = match.groups()

        if name is None:
            if self.objtype == 'constructor':
                primary_line += addnodes.desc_name(text=self.objtype)
            elif self.objtype == 'function':
                primary_line += addnodes.desc_name(text=_('(fallback)'))
                primary_line += nodes.emphasis(text=' ' + self.objtype)
                if len(arglist_str.strip()) != 0:
                    raise ValueError
            else:
                raise ValueError
        else:
            primary_line += nodes.emphasis(text=self.objtype + ' ')
            primary_line += addnodes.desc_name(text=name)

        primary_line += parse_args_into_parameter_list(arglist_str)
        signode += primary_line

        if self.objtype == 'modifier' and len(modifiers_str.strip()) != 0:
            raise ValueError

        for match in modifier_re.finditer(modifiers_str):
            modname, modargs_str = match.groups()
            newline = addnodes.desc_signature_line()
            newline += nodes.Text(' ')  # HACK: special whitespace :/
            if modname in (
                'public', 'private',
                'external', 'internal',
                'pure', 'view', 'payable',
                'anonymous',
            ):
                newline += nodes.emphasis(text=modname)
                if modargs_str is not None:
                    raise ValueError
            elif modname == 'returns':
                newline += nodes.emphasis(text=modname + ' ')
                if modargs_str is not None:
                    newline += parse_args_into_parameter_list(modargs_str)
            else:
                newline += nodes.Text(modname)
                if modargs_str is not None:
                    marglist = addnodes.desc_parameterlist()
                    for marg in modargs_str.split(','):
                        marg = marg.strip()
                        if marg:
                            marglist += addnodes.desc_parameter(text=marg)
                    newline += marglist

            signode += newline

        return name


class SolidityStruct(SolidityTypeLike):
    doc_field_types = [
        TypedField('member', label=_('Members'), names=('member',), typenames=('type', )),
    ]


class SolidityEnum(SolidityTypeLike):
    doc_field_types = [
        GroupedField('member', label=_('Members'), names=('member',)),
    ]


class SolidityXRefRole(XRefRole):
    pass


class SolidityDomain(Domain):
    """Solidity language domain."""
    name = 'sol'
    label = 'Solidity'

    object_types = {
        'contract':     ObjType(_('contract'), 'contract'),
        'library':      ObjType(_('library'), 'lib'),
        'interface':    ObjType(_('interface'), 'interface'),
        'statevar':     ObjType(_('statevar'), 'svar'),
        'constructor':  ObjType(_('constructor'), 'cons'),
        'function':     ObjType(_('function'), 'func'),
        'modifier':     ObjType(_('modifier'), 'mod'),
        'event':        ObjType(_('event'), 'event'),
        'struct':       ObjType(_('struct'), 'struct'),
        'enum':         ObjType(_('enum'), 'enum'),
    }

    directives = {
        'contract':     SolidityTypeLike,
        'library':      SolidityTypeLike,
        'interface':    SolidityTypeLike,
        'statevar':     SolidityStateVariable,
        'constructor':  SolidityFunctionLike,
        'function':     SolidityFunctionLike,
        'modifier':     SolidityFunctionLike,
        'event':        SolidityFunctionLike,
        'struct':       SolidityStruct,
        'enum':         SolidityEnum,
    }

    roles = {
        'contract':     SolidityXRefRole(),
        'lib':          SolidityXRefRole(),
        'interface':    SolidityXRefRole(),
        'svar':         SolidityXRefRole(),
        'cons':         SolidityXRefRole(),
        'func':         SolidityXRefRole(),
        'mod':          SolidityXRefRole(),
        'event':        SolidityXRefRole(),
        'struct':       SolidityXRefRole(),
        'enum':         SolidityXRefRole(),
    }


def setup(app):
    app.add_domain(SolidityDomain)
