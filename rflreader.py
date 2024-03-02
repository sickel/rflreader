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

    def searchfor(self,searchchar,n=1,data = None):
        # Used for searching for values in first block
        # Reading out all possible places for a given datatype within the first block
        if data is None:
            data = self.data
        longlong = "<"+(searchchar*20)
        longlonglength = struct.calcsize(longlong)
        for nsample in range(n):
            for i in range(struct.calcsize(searchchar)):
                start = i + rflreader.samplelength * nsample
                while start < rflreader.samplelength * (nsample +1):
                    print(i,start,struct.unpack_from(longlong,data,start))
                    start += longlonglength
            print(f"=== sample end {nsample+1} ===")
        sys.exit()



    def rflparse(self,start =0, data = None, datasize = None):
        if data is None:
            data = self.data
        if datasize is None:
            datasize = len(data)
            
        structs = {
            'filehead': "<4s"+"H"*61, # Signature, version? versjon? , unknown, samplelength, max recs, n recs, active/finished, filenr, padding (?)
            'samplehead': "<BBBLHH", # Unkonwn, unkonwn, samplecounter, UTC, systemconstant
            'unithead': "<"+"BBLH", # Unknown, Unknown, UTC-time +1 sec, number of chs.
            'spectrehead': "<"+"H"*5+"B"*2+"H"*4+"f"+"H"*2+"I"+"H"*14+"I"+"H"*4, # 14B unknown,2BCrystalid, 2B sample#  pr detector (rollover after 255), I livetime (us/s) ,29: Total count
            'spectre': False, # To be determined from unithead
            'spectretail': "<"+"H"*(269), # 0 - 255: Downsampled spectre
            'unittail': "<bbbbLHH"+"H"*57+"bffb"+"H"*12, # Pressure, temperature
            'sampletail':  "<"+"H"*3+"bbddd"+"H"*19+"d"+"H"*38, # Unknown, GPSsmplflag?,unknown, unknown, GPS|smplflag? , ECEF X, ECEF Y, ECEF Z, unknowns, altitude, unkonwns
       
        }
        
        fieldidxs = {'signature': 0,     # filehead
                     'version': 2,       # filehead
                     'samplelength': 4,  # filehead
                     'samplesinfile': 7, # filehead
                     'active': 8,        # filehead
                     'filenr': 9,        # filehead
                     'sample#':2,        # samplehead
                     'UTC': 3,           # samplehead
                     'noofchs': 3,       # unithead
                     'pressure': 65,     # unittail
                     'temperature': 66,  # unittail
                     'livetime': 14,     # spectrehead
                     'totcounts': 29,    # spectrehead
                     'cosmiccounts': 32, # spectrehead
                     'crystalid': 8,     # spectrehead
                     'unitspectre#': 9,  # spectrehead
                     'gpxx': 5,          # sampletail
                     'gpxy': 6,          # sampletail
                     'gpxz': 7,          # sampletail
                     'altitude': 27,     # sampletail
                     }
        
        
        structs = {
            'filehead': "<4s"+"H"*61, # Signature, version? versjon? , unknown, samplelength, max recs, n recs, active/finished, filenr, padding (?)
            'samplehead': "<BBBLHHB", # Unkonwn, unkonwn, samplecounter, UTC, systemconstant
            'unithead': "<"+"BLHHH", # Unknown, Unknown, UTC-time +1 sec, number of chs.
            'spectrehead': "<"+"H"*3+"B"*2+"H"*4+"f"+"H"*2+"I"+"H"*14+"I"+"H"*4, # 14B unknown,2BCrystalid, 2B sample#  pr detector (rollover after 255), I livetime (us/s) ,29: Total count
            'spectre': False, # To be determined from unithead
            'spectretail': "<"+"H"*(271), # 0 - 255: Downsampled spectre
            'unittail': "<bbbbLHH"+"H"*57+"bffb"+"H"*10+"B", # Pressure, temperature
            'sampletail':  "<B"+"H"*2+"bbddd"+"H"*19+"d"+"H"*38, # Unknown, GPSsmplflag?,unknown, unknown, GPS|smplflag? , ECEF X, ECEF Y, ECEF Z, unknowns, altitude, unkonwns
       
        }
        
              
        
        fieldidxs = {'signature': 0,     # filehead
                     'version': 2,       # filehead
                     'samplelength': 4,  # filehead
                     'samplesinfile': 7, # filehead
                     'active': 8,        # filehead
                     'filenr': 9,        # filehead
                     'sample#':2,        # samplehead
                     'UTC': 3,           # samplehead
                     'noofchs': 2,       # unithead
                     'UTCnext': 2,       # unithead
                     'pressure': 65,     # unittail
                     'temperature': 66,  # unittail
                     'livetime': 14,     # spectrehead
                     'totcounts': 29,    # spectrehead
                     'cosmiccounts': 32, # spectrehead
                     'crystalid': 8,     # spectrehead
                     'unitspectre#': 9,  # spectrehead
                     'gpxx': 5,          # sampletail
                     'gpxy': 6,          # sampletail
                     'gpxz': 7,          # sampletail
                     'altitude': 27,     # sampletail
                     }
        
        
        if self.printout:
            print('spectre#,blocktype,start')
        if start == 0:
            (filehead,start,readfrom) = self.readchunk(structs['filehead'],start,data)
            if self.printout:
                print(f"0,filehead,{readfrom},{filehead}")
            signature = filehead[fieldidxs['signature']]
            #  Checking that the file is as expected

            if signature != b'RSRL':
                print('Wrong file type signature: ',signature)
                sys.exit(2)

            if filehead[fieldidxs['version']] != 1001:
                print(f'Wrong file version: {filehead[fieldidxs["version"]]}')
                sys.exit(3)
                
            if filehead[fieldidxs['samplelength']] != rflreader.samplelength:
                print(f"Expected samplelength {rflreader.samplelength}, found samplelength {filehead[fieldidxs['samplelength']]}")
                sys.exit(3)

            i = 0
            if os.environ.get("RFL_READLIMIT"):
                # To be used to have a smaller output for testing
                datasize = int(datasize/10)

        prevsample = None
        ignoreerror = os.environ.get("RFL_IGNOREERROR")

        measurements = []
        sample = {'units':[]}
        nsample = 1
        while start <= datasize:
            # Five crystals in one detectors
            # Four detectors in one sample
            try:
                if (i)%20 == 0: 
                    st = 'samplehead'
                    (sampledata,start,readfrom) = self.readchunk(structs[st],start,data)
                    sampleid = sampledata[fieldidxs['sample#']]
                    if not ignoreerror and prevsample is not None:
                        if nsample > filehead[fieldidxs['samplesinfile']]:
                            break
                        #if (prevsample + 1) % 256 != sampleid:
                        #    break
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{sampledata}")
                    sample = {'units':[], 'epoch': sampledata[fieldidxs['UTC']],'sampleid':sampleid}
                    prevsample = sampleid
                    nsample += 1
                if (i)%5 == 0: 
                    st = 'unithead'
                    unit = {'spectres': [], 
                            'pressure': None,
                            'temperature': None}
                    (unitdata,start,readfrom) = self.readchunk(structs[st],start,data)
                    if self.printout:
                        print(f"{i+1},{st},{readfrom},{unitdata}")
                    unit['epochnext'] = unitdata[2]
                    if not structs ['spectre']:
                        structs['spectre'] = "<"+"H"*unitdata[fieldidxs['noofchs']]
                st ='spectrehead'
                (spectrehead,start,readfrom) = self.readchunk(structs[st],start,data)
                if self.printout:
                    print(f"{i+1},{st},{readfrom},{spectrehead}")
                spectredata={'livetime':spectrehead[fieldidxs['livetime']]}
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
                    for field in ('temperature','pressure'):
                        idx = fieldidxs[field]
                        if unitend[idx] !=0:
                            unit[field] = unitend[idx]
                            
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
                    sample['sample#']=sampletaildata[fieldidxs['sample#']]
                    sample['altitude'] = sampletaildata[fieldidxs['altitude']]
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
        n=1
        if len(sys.argv) > 3:
            n = int(sys.argv[3])
        reader.searchfor(searchchar,n)
        sys.exit()
    readfrom,measurements = reader.rflparse()
    print(readfrom,len(measurements))
