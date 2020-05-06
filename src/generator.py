from arpeggio import visit_parse_tree, PTNodeVisitor

def AssemblySuffix(size):
    if size == 1:
        return "b"
    elif size == 2:
        return "w"
    elif size == 4:
        return "l"
    elif size == 8:
        return "q"
    else:
        raise ValueError("Unknown suffix size " + str(size))

POINTER_SIZE = 8

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
    def __init__(self, datatype, position):
        self.position = position
        if datatype == "string":
            self.datatype = "string"
            self.size = 8
        elif datatype == "int":
            self.datatype = "int"
            self.size = 2
        else:
            raise ValueError("Unknown datatype")

class SymbolManager():
    def __init__(self):
        self.symbols = {}
        self.currentPos = 0

    def AddSymbol(self, datatype, name, size):
        pos = self.currentPos
        self.symbols[name] = Symbol(datatype, self.currentPos)
        self.currentPos += size
        return pos

    # The -8 here to make it work is worrying
    def GetStackPos(self, name):
        pos = self.currentPos - self.symbols[name].position - self.symbols[name].size
        return str(pos) + "(%rsp)"

class generator(PTNodeVisitor):

    def __init__(self, debug):
        super().__init__()
        self.symbolManager = SymbolManager()
        self.literalManager = literalManager()

    # Returns address of string literal, and size
    def visit_string_literal(self, node, children):
        return (self.literalManager.AddLiteral(children[0]), POINTER_SIZE)

    # Returns int value and size
    def visit_integer(self, node, children):
        return ("$" + str(node), 2)

    def visit_var_decl(self, node, children):
        varType = children[0]
        varName = children[1]
        varValue = children[2][0]
        varSize = children[2][1]
        pos = self.symbolManager.AddSymbol(varType, varName, varSize)
        return "push" + AssemblySuffix(varSize) + " " + varValue + "\n"

    def builtin_print(self, arg):
        symbol = self.symbolManager.symbols[arg]
        out = "mov $1, %rax\n"
        out += "mov $1, %rdi\n"
        if symbol.datatype == "string":
            out += "mov " + self.symbolManager.GetStackPos(arg) + ", %rsi\n"
            out += "mov $" + str(13) + ", %rdx\n"
        elif symbol.datatype == "int":
            out += "lea" + AssemblySuffix(POINTER_SIZE) + " " + self.symbolManager.GetStackPos(arg) + ", %rsi\n"
            out += "mov $1, %rdx\n"
        out += "syscall\n"
        return out


    def visit_functionCall(self, node, children):
        arg = children[1]
        function = children[0]
        if function == "print":
            return self.builtin_print(arg)
        else:
            raise ValueError("Undefined function")

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
