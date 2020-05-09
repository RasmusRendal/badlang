from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _

def name():               return _(r'[a-zA-Z]*')
def string_literal():     return '"', _(r'[a-z A-Z, ?!]*'), '"'
def integer():            return _(r'[0-9]+')
def var():                return name
def expr():               return [integer, string_literal, var], ZeroOrMore("+", expr)
def var_decl():           return name, name, "=", expr
def procedureCall():      return name, "(", Optional(expr, ZeroOrMore(",", expr)), ")"
def statement():          return [var_decl, procedureCall]
def statements():         return OneOrMore(statement)
def proc_args():          return Optional(name, name, ZeroOrMore(",", name, name))
def procedure():          return "proc", name, "(", proc_args, ")", "{", statements, "}"
def procedures():         return OneOrMore(procedure)
def program():            return Optional(procedures), statements, EOF

parser = ParserPython(program)
