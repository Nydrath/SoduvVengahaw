import subprocess
import time

lifelength = 60*60*24
birth = time.time()

with open("life", "w") as f: pass

while True:
    time.sleep(1)
    if time.time()-birth >= lifelength:
        # All must end
        subprocess.call("./veil/death.sh")
        import sys
        sys.exit(1)
