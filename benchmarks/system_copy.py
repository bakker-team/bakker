"""
Unchecked behavior when copying to a folder inside the folder that should be backed up.
"""

import sys
import time
import shutil


in_path = sys.argv[1]
out_path = sys.argv[2]

start = time.time()
shutil.copytree(in_path, out_path, symlinks=True)
end = time.time()
print("Total duration: " + str(end-start))

