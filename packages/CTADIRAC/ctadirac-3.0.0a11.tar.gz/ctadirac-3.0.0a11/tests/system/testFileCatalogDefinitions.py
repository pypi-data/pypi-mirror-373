""" Collection of classes for DMS testing purposes
"""

__RCSID__ = "$Id$"

import os

from DIRAC.Core.Base.Script import Script


import DIRAC
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.Resources.Catalog.RucioFileCatalogClient import RucioFileCatalogClient
from DIRAC.DataManagementSystem.Client.DataManager import DataManager

Script.parseCommandLine()


class ClientFileCatalog:
    def __init__(self, catalog):
        self.catalogs = [catalog]
        self.dest_se_1 = "PIC-Disk"
        self.dest_se_2 = "CSCS-Disk"
        self.test_dir = "/ctao/tests/file_catalog"
        self.lfn = os.path.join(self.test_dir, "testFile.txt")
        self.file_name = os.path.basename(self.lfn)
        self.file_tuple = (
            self.lfn,
            "destUrl",
            0,
            self.dest_se_1,
            "D41D8CD9-8F00-B204-E980-0998ECF8427E",
            "001",
        )
        self.file_dict = dict()
        self.file_dict[self.lfn] = {
            "Checksum": "f1df822d",
            "GUID": "7FF3F2EB-1B21-4874-493E-25C27FF3F53F",
            "Size": 3303708045,
            "SE": self.dest_se_1,
            "PFN": os.path.join(
                "root://tmpes28pstr@srm.pic.es//pnfs/pic.es/data/cta/Grid/Data",
                self.lfn,
            ),
        }

        if "RucioFileCatalog" in self.catalogs:
            self.fc = RucioFileCatalogClient()
        elif "DIRACFileCatalog" in self.catalogs:
            self.fc = FileCatalogClient()
        self.dm = DataManager(self.catalogs)

    def write_test_file(self):
        with open(self.file_name, "w") as file:
            file.write("This is a test file")
        return DIRAC.S_OK()

    def create_directory(self):
        gLogger.notice(f"Create directory {self.test_dir}")
        res = self.fc.createDirectory(self.test_dir)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to create directory: {res['Message']}")
        return res

    def list_directory(self):
        gLogger.notice(f"List directory {self.test_dir}")
        res = self.fc.listDirectory(self.test_dir)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to list directory: {res['Message']}")
        return res

    def register_file(self):
        "Only registers file in the catalog without uploading to any SE"
        gLogger.notice(f"Register file {self.lfn}")
        res = self.fc.addFile(self.file_dict)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to register file: {res['Message']}")
        return res

    def put_and_register(self):
        "Use the DataManager for the put and register"
        gLogger.notice(f"Upload file {self.lfn} to {self.dest_se_1}")
        res = self.dm.putAndRegister(self.lfn, self.file_name, self.dest_se_1)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to upload file: {res['Message']}")
        return res

    def remove_file(self):
        gLogger.notice(f"Remove file {self.lfn}")
        res = self.fc.removeFile(self.lfn)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to remove file: {res['Message']}")
        return res
