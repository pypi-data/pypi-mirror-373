from CTADIRAC.Interfaces.API.CTAJob import CTAJob


class CtapipeTrainEnergyJob(CTAJob):
    """Job extension class for ctapipe train energy regressor"""

    def __init__(self) -> None:
        super().__init__(we_type="ctapipetrainenergy")
        self.setName("ctapipe_train-energy")
        self.setType("Training")
        self.setNumberOfProcessors(minNumberOfProcessors=8)
        self.prog_name = "ctapipe-train-energy-regressor"
        self.data_level = 2
        self.data_output_pattern = "./Data/*.pkl"
        self.output_type = "Model"
        self.output_data_type = self.output_type

    def run_ctapipe_train_energy_regressor(self) -> None:
        step = self.setExecutable(
            "./dirac_ctapipe-train-energy-regressor_wrapper",
            arguments=f"{self.options}",
            logFile="ctapipe_train-energy_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_ctapipe_train-energy"
        step["Value"]["descr_short"] = "Run ctapipe train energy"

    def run_dedicated_software(self) -> None:
        self.run_ctapipe_train_energy_regressor()
