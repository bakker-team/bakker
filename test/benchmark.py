import xxhash
import sys
import time


def get_digest(hash_function, filename):
    BLOCKSIZE = 65536

    m = hash_function()
    with open(filename, 'rb') as f:
        file_buffer = f.read(BLOCKSIZE)
        while len(file_buffer) > 0:
            m.update(file_buffer)
            file_buffer = f.read(BLOCKSIZE)
        
    print(m.hexdigest())

def benchmark(hash_function, filename, times): 
    start = time.time()
    for i in range(times):
        get_digest(hash_function, filename)
    end = time.time()
    print("Average in {} runs: {}.".format(times, (end-start)/times))

benchmark(xxhash.xxh64, sys.argv[0], 100)


