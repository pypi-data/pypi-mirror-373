""" Collection of classes for DMS testing purposes
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

DIRAC.initialize()  # Initialize configuration


class ClientDMS:
    def __init__(self):
        self.dest_se1 = "CSCS-Disk"
        self.dest_se2 = "PIC-Disk"
        self.test_dir = "/ctao/tests/dms"
        self.test_file = "DMS_TestFile.txt"
        self.test_lfn = "/ctao/tests/dms/DMS_TestFile.txt"

    def write_test_file(self):
        with open(self.test_file, "w") as file:
            file.write("This is a test file")


class DMSmetadata:
    def __init__(
        self,
        dataset_name="Prod5b_LaPalma_AdvancedBaseline_NSB1x_electron_North_20deg_R1",
        dataset_dir="/vo.cta.in2p3.fr/datasets",
        dir_meta_dict=None,
        dir_meta_field_dict=None,
        file_meta_field_dict=None,
        file_meta_dict=None,
    ):
        self.dataset_name = dataset_name
        self.dataset_dir = dataset_dir
        self.file_list = []

        self.fc = FileCatalog()
        self.fcc = FileCatalogClient()
        var_char = "VARCHAR(128)"
        if not dir_meta_field_dict:
            self.dir_meta_field_dict = {
                "MCCampaign": var_char,
                "array_layout": var_char,
                "site": var_char,
                "particle": var_char,
                "thetaP": "float",
                "phiP": "float",
                "sct": var_char,
                "tel_sim_prog_version": var_char,
                "tel_sim_prog": var_char,
                "analysis_prog": var_char,
                "analysis_prog_version": var_char,
                "data_level": "int",
                "outputType": var_char,
                "configuration_id": "int",
                "merged": "int",
            }
        else:
            self.dir_meta_field_dict = dir_meta_field_dict

        if not file_meta_field_dict:
            self.file_meta_field_dict = {
                "nsb": "int",
                "div_ang": var_char,
                "split": var_char,
            }
        else:
            self.file_meta_field_dict = file_meta_field_dict

        if not dir_meta_dict:
            self.dir_meta_dict = {
                "MCCampaign": "Prod5bTest",
                "array_layout": "Advanced-Baseline",
                "site": "LaPalma",
                "particle": "electron",
                "thetaP": 20,
                "phiP": 180.0,
                "tel_sim_prog_version": "2020-06-29b",
                "tel_sim_prog": "sim_telarray",
                "data_level": -1,
                "outputType": "Data",
                "configuration_id": 15,
            }
        else:
            self.dir_meta_dict = dir_meta_dict

        if not file_meta_dict:
            self.file_meta_dict = {
                "nsb": 1,
            }
        else:
            self.file_meta_dict = file_meta_dict

    def create_directory(self):
        # Create directory where datasets will be registered
        gLogger.notice("Create directory where datasets will be registered")
        res = self.fc.createDirectory(self.dataset_dir)
        if not res["OK"]:
            gLogger.error(f"ERROR: Failed to create directory {self.dataset_dir}")
        return res

    def remove_dir_md_from_dfc(self):
        # Remove directory metadata fields from the DFC if present
        gLogger.notice("Remove directory metadata fields from the DFC if present")
        for meta_field in self.dir_meta_field_dict:
            res = self.fc.deleteMetadataField(meta_field)
            if not res["OK"]:
                gLogger.error(f"ERROR: Failed to delete metadata field {meta_field}")
            return res

    def remove_file_md_from_dfc(self):
        # Remove file metadata fields from the DFC if present
        gLogger.notice("Remove file metadata fields from the DFC if present")
        for meta_field in self.dir_meta_field_dict:
            res = self.fc.deleteMetadataField(meta_field)
            if not res["OK"]:
                gLogger.error(f"ERROR: Failed to delete metadata field {meta_field}")
            return res

    def add_dir_md_in_dfc(self):
        # Add directory metadata fields in DFC
        gLogger.notice("Adding directory metadata fields in DFC")
        for key, value in self.dir_meta_field_dict.items():
            res = self.fc.addMetadataField(key, value)
            if not res["OK"]:
                gLogger.error(f"ERROR: Failed to add metadata field {key}")
            return res

    def add_file_md_in_dfc(self):
        # Add file metadata fields in DFC
        gLogger.notice("Adding file metadata fields in DFC")
        for key, value in self.file_meta_field_dict.items():
            res = self.fc.addMetadataField(key, value, metaType="-f")
            if not res["OK"]:
                gLogger.error(f"ERROR: Failed to add metadata field {key}")
            return res

    def main(self):
        suite = {
            "create_directory": self.create_directory,
            "add_dir_md_in_dfc": self.add_dir_md_in_dfc,
            "add_file_md_in_dfc": self.add_file_md_in_dfc,
        }

        return suite
