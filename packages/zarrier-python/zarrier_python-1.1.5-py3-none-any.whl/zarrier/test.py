from zarrier.math.geometry.plane.line import Line

from zarrier import run_in_multiprocess
import time,os

def ff(args):
    start= args[0]
    time.sleep(1)
    return start, time.time(),args[1]

if __name__ == '__main__':
    res = run_in_multiprocess(ff,[(123,i) for i in range(100)],multi=10)
    print(res)

