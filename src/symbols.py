from .asmdefs import *

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
            symbol = self.symbols[s]
            if symbol.size == 8:
                code += "pop" + AssemblySuffix(symbol.size) + " %rcx\n"
            elif symbol.size == 4:
                code += "pop" + AssemblySuffix(symbol.size) + " %ecx\n"
            elif symbol.size == 2:
                code += "pop" + AssemblySuffix(symbol.size) + " %cx\n"
            elif symbol.size == 1:
                code += "pop" + AssemblySuffix(symbol.size) + " %cl\n"
        self.symbols = {}
        self.currentPos = 0
        self.anonNameIndex = 0
        return code



