from CTADIRAC.Interfaces.API.CTAJob import CTAJob


class CtapipeTrainClassifierJob(CTAJob):
    """Job extension class for ctapipe train particle classifier"""

    def __init__(self) -> None:
        super().__init__(we_type="ctapipetrainclassifier")
        self.setName("ctapipe_train-classifier")
        self.setType("Training")
        self.setNumberOfProcessors(minNumberOfProcessors=8)
        self.prog_name = "ctapipe-train-particle-classifier"
        # defaults
        self.data_level = 2
        self.data_output_pattern = "./Data/*.pkl"
        self.output_type = "Model"
        self.output_data_type = self.output_type

    def run_ctapipe_train_particle_classifier(self) -> None:
        step = self.setExecutable(
            "./dirac_ctapipe-train-particle-classifier_wrapper",
            arguments=f"{self.options}",
            logFile="ctapipe_train-classifier_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_ctapipe_train-classifier"
        step["Value"]["descr_short"] = "Run ctapipe train classifier"

    def run_dedicated_software(self) -> None:
        self.run_ctapipe_train_particle_classifier()
