# Job.py
import json
from collections import OrderedDict
from typing import Literal

from DIRAC.Interfaces.API.Job import Job


class MetadataDict(OrderedDict):
    MCCampaign: str
    array_layout: str
    catalogs: str
    configuration_id: str
    data_level: int
    group_size: int
    merged: int
    nsb: list
    split: str
    div_ang: str
    options: str
    output_extension: str
    outputType: Literal["Data", "Log", "Model"]
    particle: str
    phiP: int
    prog_name: str
    site: str
    sct: str
    thetaP: int
    type: str
    version: str

    predefined_keys: list[str] = [
        "MCCampaign",
        "array_layout",
        "catalogs",
        "configuration_id",
        "data_level",
        "group_size",
        "merged",
        "nsb",
        "split",
        "div_ang",
        "options",
        "output_extension",
        "outputType",
        "particle",
        "phiP",
        "prog_name",
        "sct",
        "site",
        "thetaP",
        "type",
        "version",
        "systematics",
    ]

    def __setitem__(self, key, value) -> None:
        if key not in self.predefined_keys and "_prog" not in key:
            raise KeyError(f"Key '{key}' is not allowed in MetadataDict")
        super().__setitem__(key, value)


class CTAJob(Job):
    """Base Job class for CTA DL1 -> DL2 jobs"""

    def __init__(self, we_type: str) -> None:
        Job.__init__(self)
        self.we_type: str = we_type
        self.setOutputSandbox(["*Log.txt"])
        self.setName("ctajob")
        self.setTag("production")
        self.input_limit = None
        self.output_metadata = MetadataDict()
        self.output_file_metadata = MetadataDict()
        self.catalogs: str = json.dumps(["DIRACFileCatalog"])
        self.prog_name = "ctapipe-process"
        self.program_category = "analysis"
        self.software_category = "stage1"
        self.package = "ctapipe"
        self.version = "v0.10.0"
        self.compiler = "gcc48_default"
        self.configuration_id = 1
        self.data_level = 1
        self.MCCampaign = "ProdTest"
        self.options = ""
        self.data_output_pattern = "./Data/*.h5"
        self.output_type = "Data"
        self.output_data_type = "Data"
        self.output_log_type = "Log"

    def set_output_metadata(self, metadata: MetadataDict = {}) -> None:
        """Set output metadata
        Parameters:
        metadata -- metadata dictionary from telescope simulation
        """
        self.output_metadata["array_layout"] = metadata["array_layout"]
        self.output_metadata["site"] = metadata["site"]
        try:
            self.output_metadata["particle"] = metadata["particle"]
        except (KeyError, TypeError):
            pass
        try:
            phi_p = metadata["phiP"]["="]
        except (KeyError, TypeError):
            phi_p = metadata["phiP"]
        self.output_metadata["phiP"] = phi_p
        try:
            theta_p = metadata["thetaP"]["="]
        except (KeyError, TypeError):
            theta_p = metadata["thetaP"]
        self.output_metadata["thetaP"] = theta_p
        if metadata.get("sct"):
            self.output_metadata["sct"] = metadata["sct"]
        else:
            self.output_metadata["sct"] = "False"
        self.output_metadata[self.program_category + "_prog"] = self.prog_name
        self.output_metadata[self.program_category + "_prog_version"] = self.version
        self.output_metadata["data_level"] = self.data_level
        self.output_metadata["outputType"] = self.output_type
        self.output_metadata["configuration_id"] = self.configuration_id
        self.output_metadata["MCCampaign"] = self.MCCampaign
        if metadata.get("systematic_uncertainty_to_test"):
            metadata_systematics = self.systematic_uncertainty_to_test.rstrip(
                "/"
            ).split("/")
            self.output_metadata["systematics"] = "_".join(metadata_systematics[1:])

    def init_debug_step(self) -> None:
        step = self.setExecutable(
            "/bin/ls -alhtr", logFile="LS_Init_Log.txt", modulesList=["cta_script"]
        )
        step["Value"]["name"] = "Step_LS_Init"
        step["Value"]["descr_short"] = "list files in working directory"

    def software_step(self) -> None:
        step = self.setExecutable(
            "cta-prod-setup-software",
            arguments=f"-p {self.package} -v {self.version} -a {self.software_category} -g {self.compiler}",
            logFile="SetupSoftware_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_SetupSoftware"
        step["Value"]["descr_short"] = "Setup software"

    def run_dedicated_software(self) -> None:
        """To be redefined in subclasses"""
        pass

    def set_metadata_and_register_data(self) -> str:
        meta_data_json: str = json.dumps(self.output_metadata)
        file_meta_data_json: str = json.dumps(self.output_file_metadata)
        output_data_type = self.output_data_type
        step = self.setExecutable(
            "cta-prod-managedata",
            arguments=f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
            f"'{self.data_output_pattern}' {self.package}_dl{self.data_level} {self.program_category}  \
             '{self.catalogs}' {output_data_type} update_ts",
            logFile="DataManagement_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_DataManagement"
        step["Value"]["descr_short"] = "Save data files to SE and register them in DFC"
        return meta_data_json

    def register_log(self, meta_data_json) -> None:
        """To be redifined in subclasses"""
        pass

    def set_executable_sequence(self, debug=False) -> None:
        if debug:
            self.init_debug_step()

        self.software_step()

        self.run_dedicated_software()

        meta_data_json: str = self.set_metadata_and_register_data()

        self.register_log(meta_data_json)
