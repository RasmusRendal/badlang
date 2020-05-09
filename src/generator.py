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
        self.anonNameIndex = 0

    def GenName(self):
        name = "_anon" + str(self.anonNameIndex)
        self.anonNameIndex += 1
        return name

    def AddSymbol(self, datatype, size, name=None):
        if name == None:
            name = self.GenName()
        if name in self.symbols:
            raise ValueError("Symbol already defined")
        pos = self.currentPos
        self.symbols[name] = Symbol(datatype, self.currentPos)
        self.currentPos += size
        return self.symbols[name]

    def GetStackPos(self, symbol):
        pos = self.currentPos - symbol.position - symbol.size
        return str(pos) + "(%rsp)"

    def PopStack(self):
        code = ""
        for s in self.symbols:
            code += "pop" + AssemblySuffix(self.symbols[s].size) + " %rcx\n"
        self.symbols = {}
        self.currentPos = 0
        self.anonNameIndex = 0
        return code



# From an expr, we want to return
# a symbol
class generator(PTNodeVisitor):

    def __init__(self, debug):
        super().__init__()
        self.symbolManager = SymbolManager()
        self.literalManager = literalManager()
        self.procedures = []
        self.code = ""

    # Returns address of string literal, and size
    def visit_string_literal(self, node, children):
        addr = self.literalManager.AddLiteral(children[0])
        self.code += "push" + AssemblySuffix(POINTER_SIZE) + " " + addr + "\n"
        return self.symbolManager.AddSymbol("string", POINTER_SIZE)

    # Returns int value and size
    def visit_integer(self, node, children):
        self.code += "push" + AssemblySuffix(2) + " $" + str(node) + "\n"
        return self.symbolManager.AddSymbol("int", 2)

    def visit_var(self, node, children):
        varName = str(node)
        symbol = self.symbolManager.symbols[varName]
        return symbol

    def visit_expr(self, node, children):
        val = children[0]
        for i in range(0, len(children)):
            if node[i] == "+":
                self.code += "movw " + self.symbolManager.GetStackPos(val) + ", %cx\n"
                self.code += "addw " + self.symbolManager.GetStackPos(children[i]) + ", %cx\n"
                self.code += "pushw %cx" + "\n"
                val = self.symbolManager.AddSymbol("int", 2)
        return val

    def visit_var_decl(self, node, children):
        name = str(children[1])
        symbol = children[2]
        key = None
        for s in self.symbolManager.symbols:
            if self.symbolManager.symbols[s] == symbol:
                key = s
                break
        del self.symbolManager.symbols[key]
        self.symbolManager.symbols[name] = symbol
        return symbol

    def builtin_print(self, arg):
        self.code += "mov $1, %rax\n"
        self.code += "mov $1, %rdi\n"
        if arg.datatype == "string":
            self.code += "mov " + self.symbolManager.GetStackPos(arg) + ", %rsi\n"
            self.code += "mov $" + str(13) + ", %rdx\n"
        elif arg.datatype == "int":
            self.code += "lea" + AssemblySuffix(POINTER_SIZE) + " " + self.symbolManager.GetStackPos(arg) + ", %rsi\n"
            self.code += "mov $1, %rdx\n"
        self.code += "syscall\n"


    def visit_procedureCall(self, node, children):
        arg = children[1]
        procedure = children[0]
        if procedure == "print":
            return self.builtin_print(arg)
        elif procedure in self.procedures:
            self.code += "call" + AssemblySuffix(POINTER_SIZE) + " _" + procedure + "\n"
        else:
            raise ValueError("Undefined procedure")

    # This is all a horrible hack, but if it works?
    def visit_statement(self, node, children):
        code = self.code
        self.code = ""
        return code

    def visit_statements(self, node, children):
        out = ""
        for c in children:
            out += c
        return out

    def visit_procedure(self, node, children):
        procName = children[0]
        code = children[1]
        self.procedures.append(procName)
        return "_" + procName + ":\n" + code + self.symbolManager.PopStack() + "ret" + AssemblySuffix(POINTER_SIZE) + "\n"

    def visit_procedures(self, node, children):
        out = ""
        for c in children:
            out += c
        return out

    def visit_program(self, node, children):
        procedures = None
        statements = None
        if (len(children) == 2):
            procedures = children[0]
            statements = children[1]
        else:
            statements = children[0]
        self.code = ".global _start\n"
        self.code += "\n"
        self.code += ".text\n"
        if procedures != None:
            self.code += procedures
        self.code += "_start:\n"
        self.code += statements
        self.code += "mov $60, %rax\n"
        self.code += "xor %rdi, %rdi\n"
        self.code += "syscall\n"
        self.code += self.literalManager.PrintLiteralPart()




def code_generation(tree):
    gen = generator(debug=False)
    visit_parse_tree(tree, gen)
    return gen.code
