from itertools import takewhile
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.tree.Tree import TerminalNodeImpl
from .SolidityLexer import SolidityLexer
from .SolidityParser import SolidityParser
from .SolidityListener import SolidityListener


def format_ctx_list(ctx_list):
    if ctx_list is None:
        return ''

    return '(' + ', '.join(
        ' '.join(
            child.getText()
            for child in pctx.getChildren())
        for pctx in ctx_list) + ')'


class DefinitionsRecorder(SolidityListener):
    def __init__(self):
        self.current_contract_ctx = None

    def enterContractDefinition(self, ctx):
        if self.current_contract_ctx is not None:
            raise RuntimeError('trying to enter {} while already in {}'.format(
                ctx.identifier().getText(),
                self.current_contract_ctx.identifier().getText()))

        # print(*(ctx.parser._input.getHiddenTokensToLeft(ctx.start.tokenIndex) or ()))
        fullname = ' '.join((
            ctx.start.text,
            ctx.identifier().getText(),
            *(ctx.inheritanceSpecifier() and
                ('is', ', '.join(
                    node.getText()
                    for node in ctx.inheritanceSpecifier())))
        ))

        self.current_contract_ctx = ctx

        print(fullname)

    def exitContractDefinition(self, ctx):
        self.current_contract_ctx = None

    def enterStateVariableDeclaration(self, ctx):
        fullname = ' '.join(
            child.getText() for child in takewhile(
                lambda child: child.getText() not in ('=', ';'),
                ctx.getChildren(),
            )
        )

        # print('   ', fullname)

    def enterConstructorDefinition(self, ctx):
        self.enterFunctionDefinition(ctx)

        # print('   ', fullname)

    def enterFunctionDefinition(self, ctx):
        fullname = ' '.join((
            '{} {}{}'.format(
                ctx.start.text,
                ctx.identifier().getText(),
                format_ctx_list(ctx.parameterList().parameter()
                                if hasattr(ctx, 'parameterList')
                                and ctx.parameterList() is not None else None),
            )
            if hasattr(ctx, 'identifier')
            and ctx.identifier() is not None
            else
            '{}{}'.format(
                ctx.start.text,
                format_ctx_list(ctx.parameterList().parameter()
                                if hasattr(ctx, 'parameterList')
                                and ctx.parameterList() is not None else None),
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
                ('{} {}'.format(
                    ctx.returnParameters().start.text, format_ctx_list(
                        ctx.returnParameters().parameterList().parameter())),)
                if hasattr(ctx, 'returnParameters')
                and ctx.returnParameters() is not None
                else
                ()
            ),
        ))

        print('   ', fullname)

    def enterModifierDefinition(self, ctx):
        self.enterFunctionDefinition(ctx)

    def enterEventDefinition(self, ctx):
        self.enterFunctionDefinition(ctx)


def parse_sol(srcpath):
    src = FileStream(srcpath, encoding='utf8')
    lexer = SolidityLexer(src)
    stream = CommonTokenStream(lexer)
    parser = SolidityParser(stream)
    tree = parser.sourceUnit()
    recorder = DefinitionsRecorder()
    walker = ParseTreeWalker()
    walker.walk(recorder, tree)
