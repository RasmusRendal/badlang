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

argumentRegisters = ["%rdi", "%rsi", "%rdx", "%rcx"]
POINTER_SIZE = 8


