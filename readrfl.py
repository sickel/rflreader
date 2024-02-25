#!/usr/bin/python3

import sys
import struct


filename = sys.argv[1]
buffer_size = 4096*1024*11
le = False
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
    returndata = struct.unpack_from(pattern,data,start)
    newstart = start + struct.calcsize(pattern)
    return returndata,newstart,start

#fileheadstruct = ">"+"H"*72
spectreheadst = ">"+"H"*36
spectrestruct = ">"+"H"*1024
spectretailst = ">"+"H"*(1329-1024-36)
unitblock = ">"+"H"*84
rechead = ">"+"H"*82+"b"
spectresize = struct.calcsize(spectrestruct)
blocklength = 53997
specblocklength = 2658
head = 216
start = head - struct.calcsize(unitblock)
#(filehead,start,readfrom) = readchunk(fileheadstruct,0,data)
#print(f"0,{readfrom},{filehead}")

for i in range(50):
    if (i)%20 == 0 and i > 0:
        (recheaddata,start,readfrom) = readchunk(rechead,start,data)
        print(f"{i+1},{readfrom},{recheaddata}")
    if (i)%5 == 0 :
        (unitdata,start,readfrom) = readchunk(unitblock,start,data)
        print(f"{i+1},{readfrom},{unitdata}")
    if (i > 0):
        (spectrehead,start,readfrom) = readchunk(spectreheadst,start,data)
        print(f"{i+1},{readfrom},{spectrehead}")
    (spectre,start,readfrom) = readchunk(spectrestruct,start,data)
    print(f"{i+1},{readfrom},{spectre}")
    (spectretail,start,readfrom) = readchunk(spectretailst,start,data)
    print(f"{i+1},{readfrom},{spectretail}")
    
    #print(i+1,start,spectre[0:10],spectre[-60:])
sys.exit()
