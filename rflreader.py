#!/usr/bin/python3

import sys
import struct
import os

"""
Filestructur: Each sample is combined of 0 -4 detectors
each detector having 0 -5 crystals
one spectre is collected for each detector.

There is a file header, a header and footer for  each detector and each spectre
there is a footer for each sample
"""

class rflreader:
    samplelength= 53997

    def readchunk(self,pattern,start,data):
            last = start
            returndata = struct.unpack_from(pattern,data,start)
            newstart = start + struct.calcsize(pattern)
            return returndata,newstart,start

    def __init__(self,filename,printout=False):
        with open(filename,'rb') as file:
            data = file.read()
        self.data = data
        self.datasize = len(data)
        self.printout = printout
        # return self.data, self.datasize

    def searchfor(self,searchchar,data = None):
        # Used for searching for values in first block
        # Reading out all possible places for a given datatype within the first block
        if data is None:
            data = self.data
        longlong = "<"+(searchchar*20)
        longlonglength = struct.calcsize(longlong)
        for i in range(struct.calcsize(searchchar)):
            start = i
            while start < rflreader.samplelength:
                print(i,start,struct.unpack_from(longlong,data,start))
                start += longlonglength
        sys.exit()



    def rflparse(self,start =0, data = None, datasize = None):
        if data is None:
            data = self.data
        if datasize is None:
            datasize = len(data)
            
        structs = {
            'filehead': "<cccc"+"H"*61, # Signature, version? unknown, unknown, samplelength, unknown.
            'samplehead': "<BBBLHH", # Unkonwn, unkonwn, samplecounter, UTC, systemconstant
            'unithead': "<"+"bbLH", # Unknown, Unknown, UTC-time +1 sec, number of chs.
            'spectrehead': "<"+"H"*5+"B"*2+"H"*8+"I"+"H"*14+"I"+"H"*4, # 14B unknown,2BCrystalid, 2B sample#  pr detector (rollover after 255), I livetime (us/s) ,29: Total count
            'spectre': False, # To be determined from unithead
            'spectretail': "<"+"H"*(269), # 0 - 255: Downsampled spectre
            'unittail': "<bbbbLHH"+"H"*74,    
            'sampletail':  "<"+"H"*3+"bbddd"+"H"*61, # Unknown, smplflag?,unknown, unknown, smplflag? , ECEF X, ECEF Y, ECEF Z, unknowns
        }
        if self.printout:
            print('spectre#,blocktype,start')
        if start == 0:
            (filehead,start,readfrom) = self.readchunk(structs['filehead'],start,data)
            if self.printout:
                print(f"0,filehead,{readfrom},{filehead}")
            signature = b''.join(filehead[0:4])

            #  Checking that the file is as expected

            if signature != b'RSRL':
                print('Wrong file type signature: ',signature)
                sys.exit(2)

            if filehead[4] != 1:
                print(f'Wrong file version: {filehead[4]}')
                sys.exit(3)
                
            if filehead[7] != rflreader.samplelength:
                print(f"Expected samplelength {rflreader.samplelength}, found samplelength {filehead[7]}")
                sys.exit(3)

            i = 0
            if os.environ.get("RFL_READLIMIT"):
                # To be used to have a smaller output for testing
                datasize = int(datasize/10)

        prevsample = None
        ignoreerror = os.environ.get("RFL_IGNOREERROR")

        measurements = []
        sample = {'units':[]}
        while start <= datasize:
            # Five crystals in one detectors
            # Four detectors in one sample
            try:
                if (i)%20 == 0: 
                    st = 'samplehead'
                    (sampledata,start,readfrom) = self.readchunk(structs[st],start,data)
                    sampleid = sampledata[2]
                    if not ignoreerror and prevsample is not None:
                        if (prevsample + 1) % 256 != sampleid:
                            break
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{sampledata}")
                    sample = {'units':[], 'epoch': sampledata[3],'sampleid':sampleid}
                    prevsample = sampleid
                if (i)%5 == 0: 
                    st = 'unithead'
                    unit = {'spectres':[]}
                    (unitdata,start,readfrom) = self.readchunk(structs[st],start,data)
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{unitdata}")
                    unit['epochnext'] = unitdata[2]
                    if not structs ['spectre']:
                        structs['spectre'] = "<"+"H"*unitdata[3]
                st ='spectrehead'
                (spectrehead,start,readfrom) = self.readchunk(structs[st],start,data)
                if self.printout:
                    print(f"{i+1},{st},{readfrom},{spectrehead}")
                spectredata={'livetime':spectrehead[14]}
                st = 'spectre'
                (spectre,start,readfrom) = self.readchunk(structs[st],start,data)
                spectredata['spectre'] = spectre
                unit['spectres'].append(spectredata)
                if self.printout:
                    print(f"{i+1},{st},{readfrom},{spectre}")
                st = 'spectretail'
                (spectretail,start,readfrom) = self.readchunk(structs[st],start,data)
                if self.printout:
                    print(f"{i+1},{st},{readfrom},{spectretail}")
                if (i+1)%5 == 0:
                    st = 'unittail'
                    (unitend,start,readfrom) = self.readchunk(structs[st],start,data)
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{unitend}")
                    sample['units'].append(unit)
                samplefinished = False
                if (i+1)%20 == 0:
                    st = 'sampletail'
                    samplefinished = True
                    (sampletaildata,start,readfrom) = self.readchunk(structs[st],start,data)
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{sampletaildata}")
                    # 'sampletail': "<"+"H"*9+"bddd"+"H"*61, # Unknown x10, ECEF X, ECEF Y, ECEF Z, unknowns
                    sample['gpsxyz']=sampletaildata[5:8]
                    sample['sample#']=sampletaildata[3]
                    measurements.append(sample)
                i += 1
            except struct.error as e:
                if not samplefinished:
                    # Read incomplete data sets
                    print(f"Reading error in {st}")
                    print(e)
                    break
                break
        if os.environ.get("RFL_DUMPDATA"):
            print(measurements, file = sys.stderr)
        return readfrom,measurements


if __name__ == '__main__':

    
    filename = sys.argv[1]
    reader = rflreader(filename,True)
    if len(sys.argv) >2:
        searchchar = sys.argv[2]
        reader.searchfor(searchchar)
        sys.exit()
    readfrom,measurements = reader.rflparse()
    print(readfrom,len(measurements))
