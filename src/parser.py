from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

def name():               return _(r'[a-zA-Z]*')
def string_literal():     return '"', _(r'[a-z A-Z]*'), '"'
def integer():            return _(r'[0-9]+')
def var():                return name
def expr():               return [integer, string_literal, var], ZeroOrMore("+", expr)
def var_decl():           return name, name, "=", expr
def functionCall():       return name, "(", expr, ")"
def statement():          return OneOrMore([var_decl, functionCall]), EOF

parser = ParserPython(statement)
