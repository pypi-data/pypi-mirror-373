#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Base.Script import Script

Script.setUsageMessage(
    """
Register files in the catalog
Usage:
   cta-prod-register-file <ascii file with lfn list>
"""
)

Script.parseCommandLine(ignoreErrors=True)
# Must comes after parseCommandLine
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

fc = FileCatalog()


def registerFile(lfn, metadata_dict):



    #PFN = metadata_dict["PFN"]
    SE = metadata_dict["SE"]
    Size = metadata_dict["Size"]
    GUID = metadata_dict["GUID"]
    Checksum = metadata_dict["Checksum"]
    lfn_dict = {lfn: {'PFN': PFN, 'SE': SE, 'Size': Size, 'GUID': GUID, 'Checksum': Checksum}}
    print(lfn_dict)
    #res = fc.addFile(lfn)


def getFileMetadata(lfn):
    res = fc.getFileMetadata(lfn)
    metadata_dict = res["Value"]["Successful"][lfn]
    return metadata_dict

def getReplicas(lfn):
    res = fc.getReplicas(lfn)
    replica_dict = res["Value"]
    print(replica_dict)
    return replica_dict


def main():
    #args = Script.getPositionalArgs()
    #if len(args) > 0:
    #    infile = args[0]
    #else:
    #    Script.showHelp()

    #infileList = read_inputs_from_file(infile)
    #p = Pool(1)
    #p.map(registerFile, infileList)
    lfn = "/vo.cta.in2p3.fr/user/a/arrabito/testPIC-Disk.txt"
    metadata_dict = getFileMetadata(lfn)
    replica_dict = getReplicas(lfn)
    #lfn_dict = {lfn: {'PFN':, 'SE':, 'Size':, 'GUID':, 'Checksum': }}
    #registerFile(lfn, metadata_dict)

if __name__ == "__main__":
    main()
