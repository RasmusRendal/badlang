from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

def name():               return _(r'[a-zA-Z]*')
def string_literal():     return '"', _(r'[a-z A-Z]*'), '"'
def integer():            return _(r'[0-9]+')
def var_decl():           return name, name, "=", [string_literal, integer]
def functionCall():           return name, "(", name, ")"
def statement():          return OneOrMore([var_decl, functionCall]), EOF

parser = ParserPython(statement)
