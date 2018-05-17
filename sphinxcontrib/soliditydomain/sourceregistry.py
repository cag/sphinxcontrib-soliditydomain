import os
import posixpath
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
    name = CharField()
    vartype = CharField()
    paramtypes = CharField()
    contract_name = CharField()
    docs = TextField()

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


def format_ctx_list(ctx_list):
    if ctx_list is None:
        return ''

    return '(' + ', '.join(
        ' '.join(
            child.getText()
            for child in pctx.getChildren())
        for pctx in ctx_list) + ')'


def construct_signature_for_function_like(ctx):
    param_list = format_ctx_list(
        ctx.parameterList().parameter()

        if hasattr(ctx, 'parameterList')
        and ctx.parameterList() is not None else


        ctx.eventParameterList().eventParameter()

        if hasattr(ctx, 'eventParameterList') else

        None
    )
    return ' '.join((
        '{} {}{}'.format(
            ctx.start.text,
            ctx.identifier().getText(),
            param_list,
        )
        if hasattr(ctx, 'identifier')
        and ctx.identifier() is not None
        else
        '{}{}'.format(
            ctx.start.text,
            param_list,
        ),
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


class DefinitionsRecorder(SolidityListener):
    def __init__(self, source_unit_name):
        self.current_contract_ctx = None
        self.source_unit_name = source_unit_name

    def enterContractDefinition(self, ctx):
        if self.current_contract_ctx is not None:
            raise RuntimeError('trying to enter {} while already in {}'.format(
                ctx.identifier().getText(),
                self.current_contract_ctx.identifier().getText()))

        # print(*(ctx.parser._input.getHiddenTokensToLeft(ctx.start.tokenIndex) or ()))
        signature = ' '.join((
            ctx.start.text,
            ctx.identifier().getText(),
            *(ctx.inheritanceSpecifier() and
                ('is', ', '.join(
                    node.getText()
                    for node in ctx.inheritanceSpecifier())))
        ))

        self.current_contract_ctx = ctx

        # print(signature)

    def exitContractDefinition(self, ctx):
        self.current_contract_ctx = None

    def enterStateVariableDeclaration(self, ctx):
        signature = ' '.join(
            child.getText() for child in takewhile(
                lambda child: child.getText() not in ('=', ';'),
                ctx.getChildren(),
            )
        )

        # print('   ', signature)

    def enterConstructorDefinition(self, ctx):
        signature = construct_signature_for_function_like(ctx)
        # print('   ', signature)

    def enterFunctionDefinition(self, ctx):
        signature = construct_signature_for_function_like(ctx)
        # print('   ', signature)

    def enterModifierDefinition(self, ctx):
        signature = construct_signature_for_function_like(ctx)
        # print('   ', signature)

    def enterEventDefinition(self, ctx):
        signature = construct_signature_for_function_like(ctx)
        # print('   ', signature)

    def enterStructDefinition(self, ctx):
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

        # print('   ', signature)
        # for member in members:
        #     print('       ', member)

    def enterEnumDefinition(self, ctx):
        signature = ' '.join((
            ctx.start.text,
            ctx.identifier().getText(),
        ))

        members = tuple(
            enum_val.getText()
            for enum_val in ctx.enumValue()
        )

        # print('   ', signature)
        # for member in members:
        #     print('       ', member)


def parse_sol(srcpath, relsrcpath):
    src = FileStream(srcpath, encoding='utf8')
    lexer = SolidityLexer(src)
    stream = CommonTokenStream(lexer)
    parser = SolidityParser(stream)
    tree = parser.sourceUnit()
    recorder = DefinitionsRecorder(relsrcpath)
    walker = ParseTreeWalker()
    walker.walk(recorder, tree)
