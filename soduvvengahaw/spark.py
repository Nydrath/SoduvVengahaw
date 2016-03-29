import os
import subprocess

try:
    with open("life", "r") as f:
        pass
except:
    import sys
    sys.exit(1)

incarnation = '388254327096700872703874549470387008385096220832703270543290342256945038825432709670087270387454947038700838509622083270327054329034225694503882'
# Hardcoded because muh bug
mac = 73813843880474L
pid = os.getpid()

newstr = ""
i = 1
for c in str(incarnation):
    n = str(mac)[i%len(str(mac))]
    p = str(pid)[i%len(str(pid))]
    newstr += str(int(c)*int(n)*int(p)+i)[-1]
    i+=1

with open("corpus", "r") as f:
    corpus = int(f.read()[:-1])
os.utime("manifestation.py", None) # Same as "touch" command. Metaphysical reasons.

with open("soduvvengahaw/spark.py", "r") as f:
    core = f.readlines()

core[10] = "incarnation = '"+newstr+"'\n"

with open("soduvvengahaw/egg.py", "w") as f:
    f.write("".join(core))

subprocess.call("./soduvvengahaw/samsara.sh")