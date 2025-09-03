"""
  Simple Wrapper on the Job class to handle EvnDisp Analysis
  for the Prod5b 2020 analysis from container
  https://forge.in2p3.fr/issues/42322
"""

__RCSID__ = "$Id$"

from CTADIRAC.Interfaces.API.CTAJob import CTAJob, MetadataDict


class EvnDispJob(CTAJob):
    def __init__(self) -> None:
        super().__init__(we_type="evndispsingjob")
        self.setName("Evndisplay_CalibReco")
        self.setType("EvnDispProcessing")
        self.package = "evndisplay"
        self.version = "eventdisplay-cta-dl1-prod5.v06"
        self.container = True
        self.program_category = "analysis"
        self.prog_name = "evndisp"
        self.configuration_id = 8
        self.output_data_level = 1
        self.base_path = "/vo.cta.in2p3.fr/MC/PROD5b/"
        self.ts_task_id = 0
        self.group_size = 1
        self.data_output_pattern = "./Data/*.simtel.DL1.tar.gz"

    def set_output_metadata(self, metadata: MetadataDict = {}) -> None:
        super().set_output_metadata(metadata)
        self.output_metadata["merged"] = 0

    def run_event_disp_software(self):
        ev_step = self.setExecutable(
            "./dirac_evndisp_wrapper",
            arguments=f"{self.options}",
            logFile="EvnDisp_Log.txt",
            modulesList=["cta_script"],
        )
        ev_step["Value"]["name"] = "Step_EvnDisplay"
        ev_step["Value"]["descr_short"] = "Run EvnDisplay"

    def run_dedicated_software(self) -> None:
        self.run_event_disp_software()
