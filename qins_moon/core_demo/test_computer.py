
import time


import time

for i in range(5):
    start_t = time.time_ns()
    for j in range(100000000):
        pass
    print((time.time_ns()-start_t)/1000000000)

