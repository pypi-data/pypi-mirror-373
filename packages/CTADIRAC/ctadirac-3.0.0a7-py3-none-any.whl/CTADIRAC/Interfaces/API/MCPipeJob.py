import itertools
import json
from typing import Any

import DIRAC
import numpy as np

from CTADIRAC.Core.Utilities.tool_box import DATA_LEVEL_METADATA_ID
from CTADIRAC.Interfaces.API.CTAJob import CTAJob


class MCPipeJob(CTAJob):
    """Generic MCPipe Job class"""

    def __init__(self, we_type: str = "mcsimulation") -> None:
        super().__init__(we_type=we_type)
        self.setName("MC_Generation")
        self.setType("MCSimulation")
        self.package = "corsika_simtelarray"
        self.compiler = "gcc83_matchcpu"
        self.program_category = "tel_sim"
        self.prog_name = "sim_telarray"
        self.start_run_number = "0"
        self.run_number = "@{JOB_ID}"
        self.data_level: int = DATA_LEVEL_METADATA_ID["R1"]
        self.base_path = "/vo.cta.in2p3.fr/MC/PROD6/"
        self.sct = ""
        self.magic = ""
        self.only_corsika = ""
        self.moon = ""
        self.layout = ""
        self.array_layout = "Prod6-Hyperarray"
        self.div_ang = ""
        self.zenith_angle = 20.0
        self.sequential = ""
        self.random_mono_probability = ""
        self.instrument_random_seeds = ""
        self.software_category = "simulations"
        self.degraded_values = [1]
        self.particle = None

    def set_degraded_mirror_reflectivity(self, degraded_mirror_reflectivity=False):
        """Set the values of degraded mirror reflectivity to simulate

        Parameters:
        degraded_mirror_reflectivity -- a boolean to set if to simulate a degraded mirror reflectivity
        (0.3 to 1.0 in steps of 0.05)
        """
        if degraded_mirror_reflectivity:
            DIRAC.gLogger.info("Set simulations with degraded mirror reflectivities")
            self.degraded_values = np.arange(0.3, 1.05, 0.05)
            self.degraded_mirror = "--degraded-mirror-ref"
        else:
            DIRAC.gLogger.info("Set simulations without degraded mirror reflectivities")
            self.degraded_values = [1]  # No degraded mirror reflectivity
            self.degraded_mirror = ""

    def set_div_ang(self, div_ang=None) -> None:
        div_default = [
            "0.0022",
            "0.0043",
            "0.008",
            "0.01135",
            "0.01453",
        ]  # Default divergent angles
        if div_ang is not None:
            if str(div_ang).replace(", ", ",").split(sep=",") != div_default:
                div_ang_str: str = ", ".join(str(x) for x in div_default)
                DIRAC.gLogger.error(
                    f"Unknown div_ang option: {div_ang}. Option for simulation step is: {div_ang_str}"
                )
                DIRAC.exit(-1)
            else:
                self.div_ang = div_default
                self.output_file_metadata["div_ang"] = div_default

    def set_magic(self, with_magic=False) -> None:
        """Set to simulate with MAGIC

        Parameters:
        with_magic -- a boolean for simulating with MAGIC
        """
        if with_magic is True:
            DIRAC.gLogger.info("Set simulations with MAGIC telescopes")
            self.magic = "--with-magic"

    def set_layout(self, layout) -> None:
        """Set the layout to simulate.
        The names has to follow the definitions in the sim_telarray run script
        Note, the "--" before the layout name is not needed

        Parameters:
        layout -- a string with the name of the layout
        """

        DIRAC.gLogger.info(f"Set layout to simulate to: {layout}")
        self.layout = f"--{str(layout).replace('--', '')}"

    def set_only_corsika(self, only_corsika=False) -> None:
        """Set to simulate only CORSIKA, without piping to sim_telarray

        Parameters:
        only_corsika -- a boolean for simulating only corsika
        """
        if only_corsika is True:
            DIRAC.gLogger.info(
                "Set simulations of CORSIKA only, without piping to sim_telarray"
            )
            self.only_corsika = "--without-multipipe"
            self.program_category = "airshower_sim"
            self.prog_name = "corsika"

    def set_sequential_mode(self, sequential_mode=False) -> None:
        """Set to run in sequential mode,
        i.e., use only one core instead of a core per sim_telarray instance

        Parameters:
        sequential_mode -- a boolean if to run in sequential mode
        """
        if sequential_mode is True:
            DIRAC.gLogger.info("Set to run in sequential mode")
            self.sequential = "--sequential"

    def set_random_mono_probability(self, random_mono_probability=None) -> None:
        """Set the probability to accept mono telescope triggers

        Parameters:
        random_mono_probability -- a float for the probability to accept mono telescope triggers
        """
        if random_mono_probability is not None:
            if 0 <= float(random_mono_probability) <= 1:
                DIRAC.gLogger.info(
                    f"Set random mono probability to: {random_mono_probability}"
                )
                self.random_mono_probability = (
                    f"--random-mono-probability {random_mono_probability}"
                )
            else:
                DIRAC.gLogger.error("Random mono probability must be between 0 and 1")
                DIRAC.exit(-1)

    def set_instrument_random_seeds(self, instrument_random_seeds=False) -> None:
        """Set to use predefined instrument random seeds from files rather than
        an auto-generated random seed.

        Parameters:
        instrument_random_seeds -- a boolean if to use predefined instrument random seeds
        """
        if instrument_random_seeds is True:
            DIRAC.gLogger.info("Set to use predefined instrument random seeds")
            self.instrument_random_seeds = "--instrument-random-seeds"

    def set_moon(self, moon=["dark", "half", "full"]) -> None:
        """Set to simulate with various moon conditions

        Parameters:
        moon -- a list of moon conditions for simulation
        """
        if not isinstance(moon, list):
            moon = [moon]

        if moon == ["dark"]:
            DIRAC.gLogger.info("Set simulations with dark conditions")
            self.moon = ""
            self.output_file_metadata["nsb"] = [1]
        elif moon == ["dark", "half"]:
            DIRAC.gLogger.info("Set simulations with half-moon conditions")
            self.moon = "--with-half-moon"
            self.output_file_metadata["nsb"] = [1, 5]
        elif moon == ["dark", "half", "full"]:
            DIRAC.gLogger.info("Set simulations with full-moon conditions")
            self.moon = "--with-full-moon"
            self.output_file_metadata["nsb"] = [1, 5, 19]
        else:
            moon_str = str(moon).replace("'", "")
            DIRAC.gLogger.error(
                f"Unknown moon option: {moon_str}. Options for simulation step are: \n [dark] \n [dark, half] \n \
                 [dark, half, full] "
            )
            DIRAC.exit(-1)

    def set_pointing_dir(self, pointing) -> None:
        """Set the pointing direction, North or South

        Parameters:
        pointing -- a string for the pointing direction
        """
        if pointing in ["North", "South", "East", "West"]:
            DIRAC.gLogger.info(f"Set Pointing dir to: {pointing}")
            self.pointing_dir = pointing
        else:
            DIRAC.gLogger.error(f"Unknown pointing direction: {pointing}")
            DIRAC.exit(-1)

    def set_particle(self, particle) -> None:
        """Set the corsika primary particle

        Parameters:
        particle -- a string for the particle type/name
        """
        if particle in [
            "gamma",
            "gamma-diffuse",
            "electron",
            "proton",
            "helium",
            "muon",
        ]:
            DIRAC.gLogger.info(f"Set Corsika particle to: {particle}")
            self.particle = particle
        else:
            DIRAC.gLogger.error(f"Corsika does not know particle type: {particle}")
            DIRAC.exit(-1)

    def set_sct(self, with_sct=None) -> None:
        """Set to include SCTs in simulations

        Parameters:
        with_sct -- a string to include SCTs
        """
        if with_sct is not None:
            if with_sct.lower() == "all":
                DIRAC.gLogger.info("Set to include SCTs for all MST positions")
                self.sct = "--with-all-scts"
            elif with_sct.lower() == "non-alpha":
                DIRAC.gLogger.info("Set to include SCTs for non-Alpha MST positions")
                self.sct = "--with-sct"
            else:
                DIRAC.gLogger.error(f"Unknown SCT option: {with_sct}")
                DIRAC.exit(-1)
            self.version = self.version + "-sc"

    def set_site(self, site) -> None:
        """Set the site to simulate

        Parameters:
        site -- a string for the site name (LaPalma)
        """
        if site in ["Paranal", "LaPalma"]:
            DIRAC.gLogger.info(f"Set Corsika site to: {site}")
            self.site = site
        else:
            DIRAC.gLogger.error(f"Site is unknown: {site}")
            DIRAC.exit(-1)

    def set_telescope(self, telescope):
        """Set the telescope to simulate

        Parameters:
        telescope -- a string for the telescope name
        """
        if telescope in ["LST", "MST-FlashCam", "MST-NectarCam", "SST", "SCT"]:
            DIRAC.gLogger.info(f"Set telescope to: {telescope}")
            self.telescope = telescope
        else:
            DIRAC.gLogger.error(f"Telescope {telescope} is unknown, aborting")
            DIRAC.exit(-1)

    def build_file_metadata(
        self, combination, propagate_run_number=True
    ) -> tuple[dict[str, str], Any, str, str]:
        file_meta_data: dict[str, str] = {}
        if propagate_run_number:
            file_meta_data["runNumber"] = self.run_number

        for key, value in combination.items():
            file_meta_data[key] = value

        if combination["nsb"] == 1:
            moon_str = "dark"
        if combination["nsb"] == 5:
            moon_str = "moon"
        if combination["nsb"] == 19:
            moon_str = "fullmoon"

        if combination.get("div_ang"):
            div = f"div{combination['div_ang']}"
            div_str = div + "_"
        else:
            div = ""
            div_str = ""

        return file_meta_data, moon_str, div, div_str

    def run_corsika_sim_telarray(self, debug=False) -> None:
        """
        Run CORSIKA/sim_telarray simulation step
        """
        prod_exe = "./dirac_prod_run"
        default_args = (
            f"--start_run {self.start_run_number} --run-number {self.run_number} --rn-format %06d "
            f"{self.layout} {self.only_corsika} {self.moon} {self.sct} {self.sequential} "
            f"{self.random_mono_probability} {self.instrument_random_seeds} "
        )
        if self.div_ang:
            prod_args: str = f"{default_args} --divergent "
        else:
            prod_args = f"{default_args} {self.magic}"

        prod_args = f"{prod_args} {self.site} {self.particle} {self.pointing_dir} {self.zenith_angle}"

        step = self.setExecutable(
            prod_exe,
            arguments=prod_args,
            logFile="CorsikaSimtel_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_CorsikaSimtel"
        step["Value"]["descr_short"] = "Run Corsika piped into simtel"

    def init_debug_step(self) -> None:
        super().init_debug_step()
        step = self.setExecutable("/bin/env", logFile="Env_Log.txt")
        step["Value"]["name"] = "Step_Env"
        step["Value"]["descr_short"] = "Dump environment"

    def verify_number_of_simtel_events(self, data_output_pattern, log_str) -> None:
        step = self.setExecutable(
            "dirac_simtel_check",
            arguments=f"'{data_output_pattern}'",
            logFile=f"Verify_n_showers_{log_str}Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_VerifyNShowers"
        step["Value"]["descr_short"] = "Verify number of showers"

    def upload_and_register_data_file(
        self,
        meta_data_json,
        file_meta_data_json,
        data_output_pattern,
        log_str,
    ) -> None:
        output_data_type = self.output_data_type
        step = self.setExecutable(
            "cta-prod-managedata",
            arguments=f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
            f"'{data_output_pattern}' {self.package} {self.program_category} '{self.catalogs}' {output_data_type}",
            logFile=f"DataManagement_{log_str}Log.txt",
        )

        step["Value"]["name"] = "Step_DataManagement"
        step["Value"]["descr_short"] = "Save data files to SE and register them in DFC"

    def upload_and_register_log(
        self,
        meta_data_json,
        file_meta_data_json,
        log_file_pattern,
        log_str,
    ) -> None:
        output_data_type = self.output_log_type
        step = self.setExecutable(
            "cta-prod-managedata",
            arguments=f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
            f"'{log_file_pattern}' {self.package} {self.program_category} '{self.catalogs}' {output_data_type}",
            logFile=f"LogManagement_{log_str}Log.txt",
        )
        step["Value"]["name"] = "Step_LogManagement"
        step["Value"]["descr_short"] = "Save log to SE and register them in DFC"

    def set_metadata_and_register_data(self, propagate_run_number=True) -> None:
        meta_data_json: str = json.dumps(self.output_metadata)
        keys = self.output_file_metadata.keys()

        # check if self.output_file_metadata.values() is a scalar
        # (could happen for sim_telarray processing)
        elements = self.output_file_metadata.values()
        if not any(isinstance(element, list) for element in elements):
            elements = [elements]
        for element in itertools.product(*elements):
            combination = dict(zip(keys, element))

            file_meta_data, moon_str, div, div_str = self.build_file_metadata(
                combination, propagate_run_number
            )
            file_meta_data_json = json.dumps(file_meta_data)
            data_output_pattern = f"Data/*-{div}*-{moon_str}*.simtel.zst"
            if self.only_corsika:
                data_output_pattern = "Data/*.corsika.zst"
            log_str = f"{moon_str}_{div_str}"
            self.verify_number_of_simtel_events(data_output_pattern, log_str)

            self.upload_and_register_data_file(
                meta_data_json,
                file_meta_data_json,
                data_output_pattern,
                log_str,
            )

            log_file_pattern = f"Data/*-{div}*-{moon_str}*.log_hist.tar"
            if self.only_corsika:
                log_file_pattern = "Data/*.corsika.log.gz"
            self.upload_and_register_log(
                meta_data_json,
                file_meta_data_json,
                log_file_pattern,
                log_str,
            )

    def run_dedicated_software(self) -> None:
        self.run_corsika_sim_telarray()

    def set_executable_sequence(
        self, debug: bool = False, define_n_showers=True
    ) -> None:
        super().set_executable_sequence(debug=debug)
        if define_n_showers:
            # Number of showers is passed via an environment variable
            self.setExecutionEnv({"NSHOW": f"{self.n_shower}"})


class MCPipeMuonJob(MCPipeJob):
    def __init__(self) -> None:
        super().__init__()
        self.array_layout = "Single-telescope"
        self.telescope = None
        self.sct = "True" if self.telescope == "SCT" else "False"

    def run_corsika_sim_telarray(self, debug=False) -> None:
        """Temporary condition on muon
        To be changed when the exe wrapper has been adapted"""
        prod_exe = "./dirac_prod6_muon_run"
        prod_args = f"--start_run {self.start_run_number} --run {self.run_number} "
        f"{self.moon} {self.degraded_mirror} {self.telescope} {self.site} "
        f"{self.particle} {self.pointing_dir} {self.zenith_angle}"

        step = self.setExecutable(
            prod_exe,
            arguments=prod_args,
            logFile="CorsikaSimtel_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_CorsikaSimtel"
        step["Value"]["descr_short"] = "Run Corsika piped into simtel"

    def set_metadata_and_register_data(self) -> None:
        meta_data_json: str = json.dumps(self.output_metadata)
        for degraded in self.degraded_values:
            data_output_pattern = f"Data/*dark-ref-degraded-{degraded:.2f}.simtel.zst"
            self.verify_number_of_simtel_events(data_output_pattern, "")

            file_meta_data = {"runNumber": self.run_number, "nsb": 1}
            file_meta_data_json = json.dumps(file_meta_data)
            log_str = f"dark_ref_degraded_{degraded:.2f}"
            self.upload_and_register_data_file(
                meta_data_json,
                file_meta_data_json,
                data_output_pattern,
                log_str,
            )

            log_file_pattern = f"Data/*dark-ref-degraded-{degraded:.2f}.log_hist.tar"
            self.upload_and_register_log(
                meta_data_json,
                file_meta_data_json,
                log_file_pattern,
                log_str,
            )

            if self.half_moon == "--with-half-moon":
                # Now switching to half moon NSB
                # Upload and register data - NSB=5 half moon
                file_meta_data = {"runNumber": self.run_number, "nsb": 5}
                file_meta_data_json = json.dumps(file_meta_data)
                data_output_pattern = (
                    f"Data/*moon-ref-degraded-{degraded:.2f}.simtel.zst"
                )
                log_str = f"moon_ref_degraded_{degraded:.2f}"
                self.upload_and_register_data_file(
                    meta_data_json,
                    file_meta_data_json,
                    data_output_pattern,
                    log_str,
                )

                log_file_pattern = (
                    f"Data/*moon-ref-degraded-{degraded:.2f}.log_hist.tar"
                )
                self.upload_and_register_log(
                    meta_data_json,
                    file_meta_data_json,
                    log_file_pattern,
                    log_str,
                )
