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


class SolidityObject(ObjectDescription):
    def add_target_and_index(self, name, sig, signode):
        if name not in self.state.document.ids:
            signode['names'].append(name)
            signode['ids'].append(name)
            signode['first'] = not self.names
            self.state.document.note_explicit_target(signode)
            domaindata = self.env.domaindata['sol']
            if name in domaindata:
                self.state_machine.reporter.warning(
                    'duplicate {type} description of {name}, '
                    'other instance in {otherloc}'.format(
                        type=self.objtype,
                        name=name,
                        otherloc=domaindata[name][0],
                    ), line=self.lineno)
                domaindata[name] = (self.env.docname, self.objtype)

        indextext = '{} ({})'.format(name, self.objtype)
        self.indexnode['entries'].append(('single', indextext, name, '', None))

    def before_content(self):
        if self.names:
            objects = self.env.ref_context.setdefault('sol:objects', [])
            objects.append(self.names.pop().rpartition('.')[2])

    def after_content(self):
        objects = self.env.ref_context.setdefault('sol:objects', [])
        try:
            objects.pop()
        except IndexError:
            pass


class SolidityTypeLike(SolidityObject):
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

        return '.'.join(self.env.ref_context.get('sol:objects', []) + [name])


param_var_re = re.compile(
    r'''\s* ( [\w\s\[\]\(\)=>]+? ) # type
        (?: \s* \b (
            public | private | internal |
            storage | memory |
            indexed
        ) )? # modifier
        \s*(\b\w+)? # name
        \s*''', re.VERBOSE)


def normalize_type(type_str):
    type_str = re.sub(r'\s*(\W)', r'\1', type_str)
    type_str = re.sub(r'(\W)\s*', r'\1', type_str)
    type_str = re.sub(r'(\w)\s+(\w)', r'\1 \2', type_str)
    type_str = type_str.replace('mapping(', 'mapping (')
    type_str = type_str.replace('=>', ' => ')
    return type_str


class SolidityStateVariable(SolidityObject):
    def handle_signature(self, sig, signode):
        match = param_var_re.fullmatch(sig)

        if match is None:
            raise ValueError

        # normalize type string
        type_str, visibility, name = match.groups()

        if name is None:
            raise ValueError

        type_str = normalize_type(type_str)

        signode += addnodes.desc_type(text=type_str + ' ')

        if visibility is not None:
            signode += nodes.emphasis(text=visibility + ' ')

        signode += addnodes.desc_name(text=name)

        return '.'.join(self.env.ref_context.get('sol:objects', []) + [name])


function_re = re.compile(
    r'''\s* (\w+)?  # name
        \s* \( ([^)]*) \)  # arglist
        \s* ((?:\w+ \s* (?:\([^)]*\))? \s* )*)  # modifiers
        \s*''', re.VERBOSE)


def _parse_args(arglist_str):
    params = addnodes.desc_parameterlist()

    if len(arglist_str.strip()) == 0:
        return params, []

    argmatches = [param_var_re.fullmatch(
        arg_str) for arg_str in arglist_str.split(',')]

    if not all(argmatches):
        raise ValueError

    abi_types = []
    for argmatch in argmatches:
        atype, memloc, name = argmatch.groups()
        atype = normalize_type(atype)
        abi_types.append(atype + ('' if memloc != 'storage' else ' storage' ))
        params += addnodes.desc_parameter(
            text=' '.join(filter(lambda x: x, (atype, memloc, name))))

    return params, abi_types


modifier_re = re.compile(r'(\w+)(?:\s*\(([^)]*)\))?')


class SolidityFunctionLike(SolidityObject):
    doc_field_types = [
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
                name = 'constructor'
                primary_line += addnodes.desc_name(text=self.objtype)
            elif self.objtype == 'function':
                name = '<fallback>'
                primary_line += addnodes.desc_name(text=_('<fallback>'))
                primary_line += nodes.emphasis(text=' ' + self.objtype)
                if len(arglist_str.strip()) != 0:
                    raise ValueError
            else:
                raise ValueError
        else:
            primary_line += nodes.emphasis(text=self.objtype + ' ')
            primary_line += addnodes.desc_name(text=name)

        args_parameter_list, args_types = _parse_args(arglist_str)
        primary_line += args_parameter_list
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
                    newline += _parse_args(modargs_str)[0]
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

        if self.objtype in ('function', 'event'):
            namesuffix = '(' + ','.join(args_types) + ')'
        else:
            namesuffix = ''

        return '.'.join(self.env.ref_context.get('sol:objects', []) + [name]) + namesuffix


class SolidityStruct(SolidityTypeLike):
    doc_field_types = [
        TypedField('member', label=_('Members'), names=(
            'member',), typenames=('type', )),
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
        'statevar':     ObjType(_('state variable'), 'svar'),
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
