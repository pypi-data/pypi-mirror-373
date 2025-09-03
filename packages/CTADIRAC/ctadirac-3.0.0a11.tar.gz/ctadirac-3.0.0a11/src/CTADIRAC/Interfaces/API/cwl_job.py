from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Interfaces.API.Job import Job

class CWLJob(Job):
    """Base Job class for CWL jobs"""

    def __init__(self) -> None:
        Job.__init__(self)
        self.setOutputSandbox(["*Log.txt"])
        self.setName("cwl_job")
        self.cwl_workflow: str = ""
        self.cwl_inputs: str = ""
        self.apptainer_repository: str = ""

    def set_cwl(self, cwl_workflow: str) -> None:
        """Set CWL workflow path or URL."""
        self.cwl_workflow = cwl_workflow

    def set_cwl_inputs(self, cwl_inputs: str) -> None:
        """Set CWL input parameters path."""
        self.cwl_inputs = cwl_inputs

    def set_apptainer_repository(self, apptainer_repository: str ) -> None:
        """Set the Apptainer repository path."""
        self.apptainer_repository = apptainer_repository

    def submit(self) -> dict:
        """Submit the CWL job to DIRAC."""
        dirac = Dirac()
        self.setInputSandbox([self.cwl_workflow, self.cwl_inputs])
        self.setExecutable("cwltool", arguments=f"{self.cwl_workflow} {self.cwl_inputs}", logFile="Job_Log.txt")
        res = dirac.submitJob(self)
        return res