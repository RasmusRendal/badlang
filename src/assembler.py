from tempfile import mktemp
from subprocess import call
import os

def assemble(machine_code, output):
    saveLoc = mktemp() + ".s"
    f = open(saveLoc, "w")
    f.write(machine_code)
    f.close()
    call(["gcc", "-nostdlib", saveLoc])
    os.remove(saveLoc)
    return "lol"
