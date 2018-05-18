import os
import posixpath
import re
from itertools import takewhile
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.tree.Tree import TerminalNodeImpl
from peewee import Model, CharField, TextField, SqliteDatabase
from .SolidityLexer import SolidityLexer
from .SolidityParser import SolidityParser
from .SolidityListener import SolidityListener

db = SqliteDatabase(':memory:')


class SolidityObject(Model):
    objtype = CharField()
    file = CharField()
    signature = CharField()
    name = CharField(null=True)
    vartype = CharField(null=True)
    paramtypes = CharField(null=True)
    contract_name = CharField(null=True)
    docs = TextField(default='')

    class Meta:
        database = db


def remove_prefix(text, prefix):
    # https://stackoverflow.com/a/16891418
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def build_source_registry(app):
    db.connect()
    db.create_tables((SolidityObject,))

    lookup_path = app.env.config.autodoc_lookup_path

    for root, dirs, files in os.walk(lookup_path):
        for name in files:
            if os.path.splitext(name)[1].lower() == '.sol':
                parse_sol(os.path.join(root, name), relsrcpath=remove_prefix(
                    posixpath.join(
                        posixpath.relpath(root, lookup_path),
                        name),
                    './'))


def teardown_source_registry(app, exception):
    # for obj in (
    #     SolidityObject.select()
    #     .where(SolidityObject.objtype.in_(('contract', 'interface')))
    # ):
    #     print(
    #         obj.file,
    #         obj.objtype,
    #         obj.signature,
    #         obj.name,
    #         obj.vartype,
    #         obj.paramtypes,
    #         obj.contract_name,
    #     )
    #     print(obj.docs)
    #     print()
    db.close()


comment_line_re = re.compile(
    r'''
        ^ (?: /{3,} | /\*{2,} | is )
    ''', re.VERBOSE)


def get_docs_from_comments_for_obj(ctx):
    lines = []

    for comment in ctx.parser._input.getHiddenTokensToLeft(
        ctx.start.tokenIndex
    ) or ():
        if comment.text.startswith('///'):
            lines.append(comment.text[3:].strip())
        elif comment.text.startswith('/**'):
            for rawline in comment.text[3:-2].splitlines():
                lines.append(rawline.strip().lstrip('*').lstrip())

    return '\n'.join(lines)

def format_ctx_list(ctx_list):
    if ctx_list is None:
        return ''

    return '(' + ', '.join(
        ' '.join(
            child.getText()
            for child in pctx.getChildren())
        for pctx in ctx_list) + ')'



class DefinitionsRecorder(SolidityListener):
    def __init__(self, source_unit_name):
        self.current_contract_name = None
        self.source_unit_name = source_unit_name

    def enterContractDefinition(self, ctx):
        name = ctx.identifier().getText()

        if self.current_contract_name is not None:
            raise RuntimeError('trying to enter {} while already in {}'.format(
                name,
                self.current_contract_name))

        objtype = ctx.start.text

        signature = ' '.join((
            name,
            *(ctx.inheritanceSpecifier() and
                ('is', ', '.join(
                    node.getText()
                    for node in ctx.inheritanceSpecifier())))
        ))

        self.current_contract_name = name

        SolidityObject.create(
            objtype=objtype,
            file=self.source_unit_name,
            signature=signature,
            name=name,
            contract_name=None,
            docs=get_docs_from_comments_for_obj(ctx),
        )

    def exitContractDefinition(self, ctx):
        self.current_contract_name = None

    def enterStateVariableDeclaration(self, ctx):
        signature = ' '.join(
            child.getText() for child in takewhile(
                lambda child: child.getText() not in ('=', ';'),
                ctx.getChildren(),
            )
        )

        SolidityObject.create(
            objtype='statevar',
            file=self.source_unit_name,
            signature=signature,
            name=ctx.identifier().getText(),
            vartype=ctx.typeName().getText(),
            contract_name=self.current_contract_name,
            docs=get_docs_from_comments_for_obj(ctx),
        )

    def add_function_like_to_db(self, ctx):
        name = (ctx.identifier().getText()
                if hasattr(ctx, 'identifier')
                and ctx.identifier() is not None else None)

        paramtypes = None

        param_list = format_ctx_list(
            ctx.parameterList().parameter()

            if hasattr(ctx, 'parameterList')
            and ctx.parameterList() is not None else

            ctx.eventParameterList().eventParameter()

            if hasattr(ctx, 'eventParameterList') else

            None
        )

        signature = ' '.join((
            ('' if name is None else name) + param_list,
            *(
                ('{}{}'.format(
                    child.identifier().getText(),
                    format_ctx_list(child.expressionList().expression()),
                ) if isinstance(
                    child,
                    SolidityParser.ModifierInvocationContext,
                ) and child.expressionList() is not None else
                    child.getText()
                    for child in ctx.modifierList().getChildren())
                if hasattr(ctx, 'modifierList') else
                ()
            ),
            *(
                (ctx.AnonymousKeyword().getText(),)
                if hasattr(ctx, 'AnonymousKeyword')
                and ctx.AnonymousKeyword() is not None else
                ()
            ),
            *(
                ('{} {}'.format(
                    ctx.returnParameters().start.text, format_ctx_list(
                        ctx.returnParameters().parameterList().parameter())),)
                if hasattr(ctx, 'returnParameters')
                and ctx.returnParameters() is not None
                else
                ()
            ),
        ))

        SolidityObject.create(
            objtype=ctx.start.text,
            file=self.source_unit_name,
            signature=signature,
            name=name,
            paramtypes=paramtypes,
            contract_name=self.current_contract_name,
            docs=get_docs_from_comments_for_obj(ctx),
        )

    enterConstructorDefinition = add_function_like_to_db
    enterFunctionDefinition = add_function_like_to_db
    enterModifierDefinition = add_function_like_to_db
    enterEventDefinition = add_function_like_to_db

    def enterStructDefinition(self, ctx):
        docs = get_docs_from_comments_for_obj(ctx)

        signature = ' '.join((
            ctx.start.text,
            ctx.identifier().getText(),
        ))

        members = tuple(
            ' '.join(
                child.getText()
                for child in vdctx.getChildren()
            )
            for vdctx in ctx.variableDeclaration()
        )

    def enterEnumDefinition(self, ctx):
        docs = get_docs_from_comments_for_obj(ctx)

        signature = ' '.join((
            ctx.start.text,
            ctx.identifier().getText(),
        ))

        members = tuple(
            enum_val.getText()
            for enum_val in ctx.enumValue()
        )


def parse_sol(srcpath, relsrcpath):
    src = FileStream(srcpath, encoding='utf8')
    lexer = SolidityLexer(src)
    stream = CommonTokenStream(lexer)
    parser = SolidityParser(stream)
    tree = parser.sourceUnit()
    recorder = DefinitionsRecorder(relsrcpath)
    walker = ParseTreeWalker()
    walker.walk(recorder, tree)
