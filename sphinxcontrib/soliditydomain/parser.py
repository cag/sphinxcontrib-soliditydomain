from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from .SolidityLexer import SolidityLexer
from .SolidityParser import SolidityParser
from .SolidityListener import SolidityListener


class DefinitionsRecorder(SolidityListener):
    def enterContractDefinition(self, ctx):
        print(*ctx.parser._input.getHiddenTokensToLeft(ctx.start.tokenIndex))
        print(ctx.identifier().start)
        pass


def parse_sol(srcpath):
    src = FileStream(srcpath)
    lexer = SolidityLexer(src)
    stream = CommonTokenStream(lexer)
    parser = SolidityParser(stream)
    tree = parser.sourceUnit()
    recorder = DefinitionsRecorder()
    walker = ParseTreeWalker()
    walker.walk(recorder, tree)
