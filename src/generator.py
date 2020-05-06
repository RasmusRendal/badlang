from arpeggio import visit_parse_tree, PTNodeVisitor

class literalManager():
    def __init__(self):
        self.literals = {}

    def AddLiteral(self, literal):
        literalName = "strlit" + str(len(self.literals))
        self.literals[literalName] = literal
        return "$" + literalName

    def PrintLiteralPart(self):
        out = ""
        for s in self.literals:
            out += s + ":\n"
            out += ".ascii \"" + self.literals[s] + "\\n\\0\"\n"
        return out

class Symbol():
    def __init__(self, position):
        self.position = position

class SymbolManager():
    def __init__(self):
        self.symbols = {}
        self.currentPos = 0

    def AddSymbol(self, name, size):
        pos = self.currentPos
        self.symbols[name] = Symbol(self.currentPos)
        self.currentPos += size
        return pos

    # The -8 here to make it work is worrying
    def GetStackPos(self, name):
        pos = self.currentPos - self.symbols[name].position - 8
        return str(pos) + "(%rsp)"

class generator(PTNodeVisitor):

    def __init__(self, debug):
        super().__init__()
        self.symbolManager = SymbolManager()
        self.literalManager = literalManager()

    def visit_string_literal(self, node, children):
        return (self.literalManager.AddLiteral(children[0]), 8)

    def visit_var_decl(self, node, children):
        stringRet = children[2]
        pos = self.symbolManager.AddSymbol(children[1], children[2][1])
        print(pos, children[2])
        return "pushq " + children[2][0] + "\n"

    def visit_print(self, node, children):
        arg = children[0]
        symbol = self.symbolManager.symbols[arg]
        out = "mov $1, %rax\n"
        out += "mov $1, %rdi\n"
        out += "mov " + self.symbolManager.GetStackPos(arg) + ", %rsi\n"
        out += "mov $" + str(13) + ", %rdx\n"
        out += "syscall\n"
        return out

    def visit_statement(self, node, children):
        out = ".global _start\n"
        out += "\n"
        out += ".text\n"
        out += "_start:\n"
        for c in children:
            out += c
        out += "mov $60, %rax\n"
        out += "xor %rdi, %rdi\n"
        out += "syscall\n"
        out += self.literalManager.PrintLiteralPart()
        return out

def code_generation(tree):
    return visit_parse_tree(tree, generator(debug=False))
