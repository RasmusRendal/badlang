from arpeggio import visit_parse_tree, PTNodeVisitor
from .symbols import *
from .asmdefs import *


class generator(PTNodeVisitor):

    def __init__(self, debug):
        super().__init__()
        self.symbolManager = SymbolManager()
        self.literalManager = literalManager()
        self.procedures = []
        self.code = ""

    def visit_string_literal(self, node, children):
        addr = self.literalManager.AddLiteral(children[0])
        self.code += "push" + AssemblySuffix(POINTER_SIZE) + " " + addr + "\n"
        return self.symbolManager.AddSymbol("string", POINTER_SIZE)

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

    def builtin_print(self, args):
        toPrint = args[0]
        printLen = args[1]
        self.code += "mov $1, %rax\n"
        self.code += "mov $1, %rdi\n"
        if toPrint.datatype == "string":
            self.code += "mov " + self.symbolManager.GetStackPos(toPrint) + ", %rsi\n"
        elif toPrint.datatype == "int":
            self.code += "lea" + AssemblySuffix(POINTER_SIZE) + " " + self.symbolManager.GetStackPos(toPrint) + ", %rsi\n"
        self.code += "movw " + self.symbolManager.GetStackPos(printLen) + ", %dx\n"
        self.code += "syscall\n"


    def visit_procedureCall(self, node, children):
        procedure = children[0]
        args = children[1:]
        if procedure == "printn":
            return self.builtin_print(args)
        elif procedure in self.procedures:
            for i in range(len(args)):
                arg = args[i]
                self.code += "mov" + AssemblySuffix(arg.size) + " " + self.symbolManager.GetStackPos(arg) + ", " + argumentRegisters[i] + "\n"
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

    def visit_proc_args(self, node, children):
        register = 0
        for i in range(0, len(children), 2):
            datatype = children[0]
            arg = children[1]
            if datatype == "int":
                self.code += "push" + AssemblySuffix(2) + " " + argumentRegisters[register] + "\n"
                self.symbolManager.AddSymbol("int", 2, arg)
            elif datatype == "string":
                self.code += "push" + AssemblySuffix(8) + " " + argumentRegisters[register] + "\n"
                self.symbolManager.AddSymbol("string", 8, arg)
            else:
                raise ValueError("Unknown datatype")
            register += 1

    def visit_procedure(self, node, children):
        procName = children[0]
        code = children[1]
        self.procedures.append(procName)
        return "_" + procName + ":\n" + code + self.symbolManager.PopStack() + "ret" + AssemblySuffix(POINTER_SIZE) + "\n\n"

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
