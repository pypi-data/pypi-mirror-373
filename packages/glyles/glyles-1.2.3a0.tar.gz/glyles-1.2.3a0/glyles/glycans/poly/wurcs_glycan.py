import logging
from antlr4 import CommonTokenStream, InputStream

from glyles.glycans.poly.glycan import Glycan
from glyles.glycans.poly.merger import Merger
from glyles.glycans.utils import ParseError
from glyles.wurcs.WURCSLexer import WURCSLexer
from glyles.wurcs.WURCSParser import WURCSParser
from glyles.glycans.poly.wurcs_walker import WURCSTreeWalker


class WURCSGlycan(Glycan):
    def parse(self):
        try:
            stream = InputStream(data=self.iupac)
            lexer = WURCSLexer(stream)
            token = CommonTokenStream(lexer)
            parser = WURCSParser(token)
            
            try:
                self.grammar_tree = parser.start()
            except ParseError as pe:
                self.parse_tree = None
                self.glycan_smiles = ""
                raise pe from None
            
            # self.parse_tree, self.tree_full = WURCSTreeWalker(self.factory, self.tree_only).parse(self.grammar_tree)

            # if the glycan should be parsed immediately, do so
            # if not self.tree_only and self.tree_full and self.full:
            #     self.glycan_smiles = Merger(self.factory).merge(self.parse_tree, self.root_orientation, start=self.start)
            #     catch any exception at glycan level to not destroy the whole pipeline because of one mis-formed glycan
        except ParseError as e:
            msg = e.__str__().replace("\n", " ")
            logging.error(f"A parsing error occurred with \"{self.iupac}\": Error message: {msg}")
            self.glycan_smiles = ""
        except Exception as e:
            msg = e.__str__().replace("\n", " ")
            logging.error(f"An unexpected exception occurred with \"{self.iupac}\". This glycan cannot be parsed. "
                          f"Error message: {msg}")
            self.glycan_smiles = ""
            raise e
