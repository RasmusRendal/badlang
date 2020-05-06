from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

def name():               return _(r'[a-zA-Z]*')
def string_literal():     return '"', _(r'[a-z A-Z]*'), '"'
def var_decl():           return name, name, "=", string_literal
def print():              return "print(", name, ")"
def statement():          return OneOrMore([var_decl, print]), EOF

parser = ParserPython(statement)
