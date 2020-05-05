#!/usr/bin/env python3

from src import *
import sys

if len(sys.argv) < 2:
    raise ValueError('bad')

f = open(sys.argv[1], 'r')
inString = f.read()
f.close()
#inString = "a = \"Hello World\" print(a)"
out = parser.parse(inString)

machineCode = code_generation(out)
assemble(machineCode, "./a.out")

