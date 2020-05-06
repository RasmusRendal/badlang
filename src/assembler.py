from tempfile import mktemp
from subprocess import call
import os

def assemble(machine_code, output):
    saveLoc = mktemp() + ".s"
    f = open(saveLoc, "w")
    f.write(machine_code)
    f.close()
    retVal = call(["gcc", "-nostdlib", saveLoc])
    os.remove(saveLoc)
    if retVal != 0:
        raise ValueError("Invalid assembly")
