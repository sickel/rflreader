#!/usr/bin/python3

import sys
import struct


filename = sys.argv[1]
buffer_size = 4096*1024*11
le = True # confirmed with block size in 
fieldtype = "h"
fieldsize = 2   

if le:
    bo = '<'
else:
    bo = '>'


with open(filename,'rb') as file:
    data = file.read()
    
print("read")

"""
read
Searching for [0, 0, 0, 0, 1, 2, 0, 4, 3, 2, 7, 6, 8, 6, 9, 6, 10, 7, 11, 13]
Found @108, 108 from last
Searching for [0, 0, 0, 0, 2, 3, 3, 3, 2, 3, 5, 1, 3, 2, 3, 2, 0, 5, 5]
Found @1437, 1329 from last
Searching for [0, 0, 0, 0, 0, 0, 0, 6, 5, 3, 3, 6, 4, 1, 11, 11, 6, 8, 6, 8]
Found @54105, 52668 from last
Searching for [0, 0, 0, 0, 2, 4, 3, 1, 5, 11, 3, 5, 7, 5, 5, 5, 7, 10, 9, 13, 12]
Found @108102, 53997 from last
Searching for [0, 0, 0, 0, 2, 2, 4, 4, 1, 2, 4, 4, 3, 4, 9, 4, 8, 5, 15, 12, 9]
Found @162099, 53997 from last
Searching for [0, 0, 0, 0, 3, 4, 2, 1, 5, 1, 3, 7, 4, 7, 4, 6, 8, 10, 10, 22, 23]
"""

def readchunk(pattern,start,data):
    last = start
    returndata = struct.unpack_from(pattern,data,start)
    start += struct.calcsize(pattern)
    return returndata,start,last


spectrestruct = bo+"H"*1024
spectremetastruct = bo+"H"*308  
unitblock = bo+"H"*86   
rechead = bo+"H"*82+"b"
spectresize = struct.calcsize(spectrestruct)
blocklength0 = 53997
blocklength = struct.unpack_from(bo+"H",data,10)[0]
if blocklength != blocklength0:
    print("Reading problem")
    sys.exit()
specblocklength = 2658
head = 216
start = head - struct.calcsize(unitblock)
for i in range(200):
    if (i)%20 == 0  and i > 0:
        (recheaddata,start,last) = readchunk(rechead,start,data)
        print(f"{i+1},{last},{recheaddata}")
    if (i)%5 == 0 :
        (unitdata,start,last) = readchunk(unitblock,start,data)
        print(f"{i+1},{last},{unitdata}")
    (spectre,start,last) = readchunk(spectrestruct,start,data)
    print(f"{i+1},{last},{spectre}")
    (spectremeta,start,last) = readchunk(spectremetastruct,start,data)
    print(f"{i+1},{last},{spectremeta}")
    
sys.exit()
