import DIRAC

from CTADIRAC.Interfaces.API.MCPipeJob import MCPipeJob


class MCSimTelProcessJob(MCPipeJob):
    """Generic MCPipe Job class"""

    def __init__(self) -> None:
        super().__init__(we_type="simtelprocessing")
        self.setType("DL0_Reprocessing")
        self.setName("SimTelProcessing")
        self.systematic_uncertainty_to_test = ""

    def set_moon(self, moon="dark") -> None:
        """Set to simulate with various moon conditions
        Redefined from parent class because in the case of sim_telarray processing,
        we do not expect to run multiple NSBs in the same job.

        Parameters:
        moon -- moon conditions for simulation
        """

        moon_options = {
            "dark": ("", 1),
            "half": ("--with-half-moon", 5),
            "full": ("--with-full-moon", 19),
        }

        if isinstance(moon, list) or moon not in moon_options:
            moon_str = str(moon).replace("'", "")
            DIRAC.gLogger.error(
                f"Unknown moon option: {moon_str}. "
                "Options for simulation step are: \n dark \n half \n full "
            )
            DIRAC.exit(-1)
        else:
            DIRAC.gLogger.info(f"Set simulations with {moon} conditions")
            self.moon, self.output_file_metadata["nsb"] = moon_options[moon]

    def set_systematic_uncertainty_to_test(
        self, systematic_uncertainty_to_test
    ) -> None:
        """Set the systematic uncertainty to test in the simulation

        Parameters:
        systematic_uncertainty_to_test -- the systematic uncertainty to test in the simulation
        """

        DIRAC.gLogger.info(
            f"Set systematic uncertainty to test to: {systematic_uncertainty_to_test}"
        )
        self.systematic_uncertainty_to_test = systematic_uncertainty_to_test

    def run_sim_telarray(self, debug=False) -> None:
        """
        Run sim_telarray processing of a CORSIKA file
        """
        prod_exe = "./dirac_sim_telarray_process"

        prod_args = self.systematic_uncertainty_to_test

        cs_step = self.setExecutable(
            prod_exe, arguments=prod_args, logFile="Simtel_Log.txt"
        )
        cs_step["Value"]["name"] = "Step_Simtel"
        cs_step["Value"]["descr_short"] = "Run sim_telarray processing of CORSIKA file"

    def set_metadata_and_register_data(self) -> None:
        super().set_metadata_and_register_data(propagate_run_number=False)

    def run_dedicated_software(self) -> None:
        self.run_sim_telarray()

    def set_executable_sequence(self, debug: bool = False) -> None:
        super().set_executable_sequence(debug=debug, define_n_showers=False)
