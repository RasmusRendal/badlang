from arpeggio import visit_parse_tree, PTNodeVisitor

class generator(PTNodeVisitor):

    def __init__(self, debug):
        super().__init__()
        self.symbols = {}

    def visit_string(self, node, children):
        return children[0]

    def visit_const_decl(self, node, children):
        self.symbols[children[0]] = children[1]
        return ""

    def visit_print(self, node, children):
        arg = children[0]
        out = "mov $1, %rax\n"
        out += "mov $1, %rdi\n"
        out += "mov $" + arg + ", %rsi\n"
        out += "mov $" + str(len(self.symbols[arg])+1) + ", %rdx\n"
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
        for s in self.symbols:
            out += s + ":\n"
            out += ".ascii \"" + self.symbols[s] + "\\n\"\n"
        return out

def code_generation(tree):
    return visit_parse_tree(tree, generator(debug=False))
