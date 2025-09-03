from copy import deepcopy

from DIRAC.Interfaces.API.Job import Job

from CTADIRAC.Interfaces.API.CTAJob import MetadataDict
from CTADIRAC.Interfaces.API.CtapipeApplyModelsJob import CtapipeApplyModelsJob
from CTADIRAC.Interfaces.API.CtapipeMergeJob import CtapipeMergeJob
from CTADIRAC.Interfaces.API.CtapipeProcessJob import CtapipeProcessJob
from CTADIRAC.Interfaces.API.CtapipeTrainClassifierJob import CtapipeTrainClassifierJob
from CTADIRAC.Interfaces.API.CtapipeTrainEnergyJob import CtapipeTrainEnergyJob
from CTADIRAC.Interfaces.API.MCPipeJob import MCPipeJob
from CTADIRAC.Interfaces.API.MCSimTelProcessJob import MCSimTelProcessJob
from CTADIRAC.ProductionSystem.Client.WorkflowElement import (
    WorkflowElement,
    WorkflowElementDefinition,
)
from tests.unit.production import (
    COMMON_CONFIG,
    CTAPIPE_PROCESS_OUTPUT_METADATA,
    MERGING_CONFIG_1,
    PROCESSING_CONFIG,
    SIM_TELARRAY_PROCESSING_CONFIG,
    SIMULATION_CONFIG,
    SIMULATION_OUTPUT_METADATA,
    WORKFLOW_CONFIG,
)


def test_workflow_element_definition() -> None:
    workflow_elmt = WorkflowElementDefinition("mcsimulation")
    assert isinstance(workflow_elmt.job, MCPipeJob)

    workflow_elmt = WorkflowElementDefinition("simtelprocessing")
    assert isinstance(workflow_elmt.job, MCSimTelProcessJob)

    workflow_elmt = WorkflowElementDefinition("ctapipeprocessing")
    assert isinstance(workflow_elmt.job, CtapipeProcessJob)

    workflow_elmt = WorkflowElementDefinition("merging")
    assert isinstance(workflow_elmt.job, CtapipeMergeJob)

    workflow_elmt = WorkflowElementDefinition("ctapipetrainenergy")
    assert isinstance(workflow_elmt.job, CtapipeTrainEnergyJob)

    workflow_elmt = WorkflowElementDefinition("ctapipetrainclassifier")
    assert isinstance(workflow_elmt.job, CtapipeTrainClassifierJob)

    workflow_elmt = WorkflowElementDefinition("ctapipeapplymodels")
    assert isinstance(workflow_elmt.job, CtapipeApplyModelsJob)

    workflow_elmt = WorkflowElementDefinition("unknown")
    assert isinstance(workflow_elmt.job, Job)


def test_we_set_constrained_job_attribute() -> None:
    # Simulation
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    assert getattr(workflow_elmt_sim, "particle", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("particle", "gamma-diffuse")
    assert workflow_elmt_sim.job.particle == "gamma-diffuse"

    assert getattr(workflow_elmt_sim, "version", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("version", "2024-02-05")
    assert workflow_elmt_sim.job.version == "2024-02-05"

    assert getattr(workflow_elmt_sim, "pointing_dir", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("pointing_dir", "North")
    assert workflow_elmt_sim.job.pointing_dir == "North"

    assert getattr(workflow_elmt_sim, "layout", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("layout", "alpha")
    assert workflow_elmt_sim.job.layout == "--alpha"

    assert getattr(workflow_elmt_sim, "moon", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("moon", "dark, half")
    assert workflow_elmt_sim.job.output_file_metadata["nsb"] == [1, 5]
    workflow_elmt_sim.set_constrained_job_attribute("moon", "dark")
    assert workflow_elmt_sim.job.output_file_metadata["nsb"] == [1]

    assert getattr(workflow_elmt_sim, "sct", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("sct", "all")
    assert workflow_elmt_sim.job.sct == "--with-all-scts"
    workflow_elmt_sim.set_constrained_job_attribute("sct", "non-alpha")
    assert workflow_elmt_sim.job.sct == "--with-sct"

    assert getattr(workflow_elmt_sim, "only_corsika", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("only_corsika", True)
    assert workflow_elmt_sim.job.only_corsika == "--without-multipipe"
    assert workflow_elmt_sim.job.program_category == "airshower_sim"
    assert workflow_elmt_sim.job.prog_name == "corsika"

    assert getattr(workflow_elmt_sim, "magic", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("magic", True)
    assert workflow_elmt_sim.job.magic == "--with-magic"

    assert getattr(workflow_elmt_sim, "sequential", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("sequential", True)
    assert workflow_elmt_sim.job.sequential == "--sequential"

    assert getattr(workflow_elmt_sim, "div_ang", None) is None
    workflow_elmt_sim.set_constrained_job_attribute(
        "div_ang", "0.0022, 0.0043, 0.008, 0.01135, 0.01453"
    )
    assert workflow_elmt_sim.job.div_ang == [
        "0.0022",
        "0.0043",
        "0.008",
        "0.01135",
        "0.01453",
    ]

    assert getattr(workflow_elmt_sim, "random_mono_probability", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("random_mono_probability", 0.01)
    assert (
        workflow_elmt_sim.job.random_mono_probability
        == "--random-mono-probability 0.01"
    )

    assert getattr(workflow_elmt_sim, "instrument_random_seeds", None) is None
    workflow_elmt_sim.set_constrained_job_attribute("instrument_random_seeds", True)
    assert workflow_elmt_sim.job.instrument_random_seeds == "--instrument-random-seeds"

    # Processing of CORSIKA files with sim_telarray
    workflow_elmt_simtel = WorkflowElement(None, "simtelprocessing")
    assert getattr(workflow_elmt_simtel, "moon", None) is None
    workflow_elmt_simtel.set_constrained_job_attribute("moon", "dark")
    assert workflow_elmt_simtel.job.output_file_metadata["nsb"] == 1
    workflow_elmt_simtel.set_constrained_job_attribute(
        "systematic_uncertainty_to_test", "test"
    )
    assert workflow_elmt_simtel.job.systematic_uncertainty_to_test == "test"

    # Processing
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    assert getattr(workflow_elmt_proc, "moon", None) is None
    version = "v0.19.2"
    workflow_elmt_proc.set_constrained_job_attribute("version", "v0.19.2")
    assert workflow_elmt_proc.job.version == version


def test_build_input_data() -> None:
    # Simulation
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    assert workflow_elmt_sim.prod_step.Inputquery is None
    workflow_elmt_sim.build_input_data(SIMULATION_CONFIG)
    assert workflow_elmt_sim.prod_step.Inputquery == {}

    # Processing of CORSIKA files with sim_telarray
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_simtel = WorkflowElement(
        workflow_elmt_sim.prod_step, "simtelprocessing"
    )
    assert workflow_elmt_simtel.prod_step.Inputquery is None
    workflow_elmt_simtel.build_input_data(SIM_TELARRAY_PROCESSING_CONFIG)
    expected_simtel_input_query = workflow_elmt_sim.prod_step.Outputquery
    expected_simtel_input_query["nsb"] = 1
    assert workflow_elmt_simtel.prod_step.Inputquery == expected_simtel_input_query

    # Processing
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    assert workflow_elmt_proc.prod_step.Inputquery is None
    workflow_elmt_proc.build_input_data(PROCESSING_CONFIG)
    expected_proc_input_query = workflow_elmt_sim.prod_step.Outputquery
    expected_proc_input_query["nsb"] = 1
    assert workflow_elmt_proc.prod_step.Inputquery == expected_proc_input_query


def test_build_job_attributes() -> None:
    # Simulation
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    workflow_elmt_sim.build_input_data(SIMULATION_CONFIG)
    assert workflow_elmt_sim.job.output_file_metadata == MetadataDict()
    assert workflow_elmt_sim.job.MCCampaign == "ProdTest"

    workflow_elmt_sim.build_job_attributes(WORKFLOW_CONFIG, SIMULATION_CONFIG)
    assert workflow_elmt_sim.job.output_file_metadata == MetadataDict([("nsb", [1])])
    assert workflow_elmt_sim.job.MCCampaign == COMMON_CONFIG["MCCampaign"]

    # Processing of CORSIKA files with sim_telarray
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_simtel = WorkflowElement(
        workflow_elmt_sim.prod_step, "simtelprocessing"
    )
    workflow_elmt_simtel.build_input_data(SIM_TELARRAY_PROCESSING_CONFIG)
    assert workflow_elmt_simtel.job.output_file_metadata == MetadataDict()
    assert workflow_elmt_simtel.job.MCCampaign == "ProdTest"

    workflow_elmt_simtel.build_job_attributes(
        WORKFLOW_CONFIG, SIM_TELARRAY_PROCESSING_CONFIG
    )
    assert workflow_elmt_simtel.job.output_file_metadata == MetadataDict([("nsb", 1)])
    assert workflow_elmt_simtel.job.MCCampaign == COMMON_CONFIG["MCCampaign"]

    # Processing
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    workflow_elmt_proc.build_input_data(PROCESSING_CONFIG)
    assert workflow_elmt_proc.job.output_file_metadata == MetadataDict()
    assert workflow_elmt_proc.job.MCCampaign == "ProdTest"

    workflow_elmt_proc.build_job_attributes(WORKFLOW_CONFIG, PROCESSING_CONFIG)
    assert workflow_elmt_proc.job.output_file_metadata == MetadataDict([("nsb", 1)])
    assert workflow_elmt_proc.job.MCCampaign == COMMON_CONFIG["MCCampaign"]


def test_build_job_output_data() -> None:
    # Simulation
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    workflow_elmt_sim.build_input_data(SIMULATION_CONFIG)
    workflow_elmt_sim.build_job_attributes(WORKFLOW_CONFIG, SIMULATION_CONFIG)
    assert workflow_elmt_sim.job.output_metadata == MetadataDict()
    workflow_elmt_sim.build_job_output_data(SIMULATION_CONFIG)
    assert workflow_elmt_sim.job.output_metadata == SIMULATION_OUTPUT_METADATA

    # Processing of CORSIKA files with sim_telarray
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_simtel = WorkflowElement(
        workflow_elmt_sim.prod_step, "simtelprocessing"
    )
    workflow_elmt_simtel.build_input_data(SIM_TELARRAY_PROCESSING_CONFIG)
    workflow_elmt_simtel.build_job_attributes(
        WORKFLOW_CONFIG, SIM_TELARRAY_PROCESSING_CONFIG
    )
    assert workflow_elmt_simtel.job.output_metadata == MetadataDict()
    workflow_elmt_simtel.build_job_output_data(SIM_TELARRAY_PROCESSING_CONFIG)
    assert workflow_elmt_simtel.job.output_metadata == SIMULATION_OUTPUT_METADATA

    # Processing
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    workflow_elmt_proc.build_input_data(PROCESSING_CONFIG)
    workflow_elmt_proc.build_job_attributes(WORKFLOW_CONFIG, PROCESSING_CONFIG)
    assert workflow_elmt_proc.job.output_metadata == MetadataDict()
    workflow_elmt_proc.build_job_output_data(PROCESSING_CONFIG)
    assert workflow_elmt_proc.job.output_metadata == CTAPIPE_PROCESS_OUTPUT_METADATA


def test_build_element_config() -> None:
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    workflow_elmt_proc.prod_step.Outputquery = deepcopy(CTAPIPE_PROCESS_OUTPUT_METADATA)
    worflow_elmt_merge = WorkflowElement(workflow_elmt_proc.prod_step, "merging")
    worflow_elmt_merge.build_input_data(MERGING_CONFIG_1)
    worflow_elmt_merge.build_job_attributes(WORKFLOW_CONFIG, MERGING_CONFIG_1)
    worflow_elmt_merge.build_job_output_data(MERGING_CONFIG_1)
    worflow_elmt_merge.build_element_config(MERGING_CONFIG_1)
    assert worflow_elmt_merge.prod_step.GroupSize == 5
    # Get "descr_short" and remove empty ones
    descr_short: list[str] = [
        line.replace("<descr_short>", "").replace("</descr_short>", "")
        for line in worflow_elmt_merge.prod_step.Body.split("\n")
        if "descr_short" in line
        and line.replace("<descr_short>", "").replace("</descr_short>", "")
    ]
    expected_desc = {
        "Setup software",
        "Run ctapipe merge",
        "Run ctapipe check merge",
        "Save data files to SE and register them in DFC",
        "Tag files as unused if job failed",
    }
    assert set(descr_short).issubset(expected_desc)


def test_get_merging_level() -> None:
    workflow_elmt_sim = WorkflowElement(None, "mcsimulation")
    workflow_elmt_sim.prod_step.Outputquery = deepcopy(SIMULATION_OUTPUT_METADATA)
    workflow_elmt_proc = WorkflowElement(
        workflow_elmt_sim.prod_step, "ctapipeprocessing"
    )
    workflow_elmt_proc.prod_step.Outputquery = deepcopy(CTAPIPE_PROCESS_OUTPUT_METADATA)
    worflow_elmt_merge = WorkflowElement(workflow_elmt_proc.prod_step, "merging")
    assert worflow_elmt_merge.job.merged == 0
    res_merged = worflow_elmt_merge.get_merging_level()
    assert res_merged == 0
    worflow_elmt_merge.prod_step.ParentStep.Outputquery = deepcopy(
        CTAPIPE_PROCESS_OUTPUT_METADATA
    )
    worflow_elmt_merge.prod_step.ParentStep.Outputquery["merged"] = 6
    res_merged = worflow_elmt_merge.get_merging_level()
    assert res_merged == 6
