from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

def name():       return _(r'[a-zA-Z]*')
def string():     return '"', _(r'[a-z A-Z]*'), '"'
def const_decl(): return name, "=", string
def print():      return "print(", name, ")"
def statement():  return OneOrMore([const_decl, print]), EOF

parser = ParserPython(statement)
