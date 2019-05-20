from pyback.checkpoint import Checkpoint
from pyback.storage import FileSystemStorage
import sys
import time


in_path = sys.argv[1]
out_path = sys.argv[2]

start = time.time()
checkpoint = Checkpoint.build_checkpoint(in_path)
checkpoint_end = time.time()
storage = FileSystemStorage(out_path)
storage.store(in_path, checkpoint)
end = time.time()
print("Checkpoint build duration:" + str(checkpoint_end - start))
print("Total duration: " + str(end-start))

