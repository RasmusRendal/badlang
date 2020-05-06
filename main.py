#!/usr/bin/env python3

from src import *
import sys

if len(sys.argv) < 2:
    raise ValueError('bad')

f = open(sys.argv[1], 'r')
inString = f.read()
f.close()
out = parser.parse(inString)

machineCode = code_generation(out)
i = 1
for line in machineCode.split("\n"):
    iString = " "*(2-len(str(i))) + str(i)
    print(iString, line)
    i += 1
assemble(machineCode, "./a.out")

