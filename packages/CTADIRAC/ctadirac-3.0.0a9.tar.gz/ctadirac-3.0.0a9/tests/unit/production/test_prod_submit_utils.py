import json
import pytest
from CTADIRAC.Interfaces.API.MCPipeJob import MCPipeJob
from CTADIRAC.ProductionSystem.Client.Utilities.production_utils import (
    check_and_sort_workflow_config,
    check_destination_catalogs,
    check_id,
    check_parents,
    find_parent_prod_step,
    get_parents_list,
    instanciate_and_build_workflow_element,
    instantiate_workflow_element_from_type,
    sort_by_id,
)
from CTADIRAC.ProductionSystem.Client.WorkflowElement import WorkflowElement

from DIRAC.ProductionSystem.Client.ProductionStep import ProductionStep

from tests.unit.production import SIMULATION_CONFIG, WORKFLOW_CONFIG


def test_sort_by_id() -> None:
    output = sort_by_id([{"ID": 2}, {"ID": 1}])
    assert output == [{"ID": 1}, {"ID": 2}]


def test_check_id() -> None:
    with pytest.raises(SystemExit) as exc_info:
        check_id([{"ID": ""}])
    assert str(exc_info.value) == "-1"

    with pytest.raises(SystemExit) as exc_info:
        check_id([{"site": "Paranal"}])
    assert str(exc_info.value) == "-1"

    assert check_id([{"ID": 2}, {"ID": 1}]) is True


def test_check_parents() -> None:
    with pytest.raises(SystemExit) as exc_info:
        check_parents(
            [{"ID": 2, "input_meta_query": {"parentID": 3}, "job_config": {}}]
        )
    assert str(exc_info.value) == "-1"

    workflow_config = [
        {"ID": 1, "input_meta_query": {}, "job_config": {}},
        {"ID": 2, "input_meta_query": {"parentID": 1}, "job_config": {}},
    ]
    assert check_parents(workflow_config) is True


def test_instantiate_workflow_element_from_type() -> None:
    # Wrong WorkflowElement type:
    workflow_step = {
        "ID": 1,
        "input_meta_query": {},
        "job_config": {"type": "erroneous"},
    }
    with pytest.raises(SystemExit) as exc_info:
        instantiate_workflow_element_from_type(workflow_step, 1)
    assert str(exc_info.value) == "-1"

    # MCSimulation:
    workflow_step = {
        "ID": 1,
        "input_meta_query": {},
        "job_config": {"type": "MCSimulation"},
    }
    assert isinstance(
        instantiate_workflow_element_from_type(workflow_step, 1),
        WorkflowElement,
    )

    # CtapipeProcessing:
    workflow_step = {
        "ID": 1,
        "input_meta_query": {},
        "job_config": {"type": "CtapipeProcessing"},
    }
    assert isinstance(
        instantiate_workflow_element_from_type(workflow_step, 1),
        WorkflowElement,
    )

    # EvnDispProcessing:
    workflow_step = {
        "ID": 1,
        "input_meta_query": {},
        "job_config": {"type": "EvnDispProcessing"},
    }
    assert isinstance(
        instantiate_workflow_element_from_type(workflow_step, 1),
        WorkflowElement,
    )

    # Merging:
    workflow_step = {"ID": 1, "input_meta_query": {}, "job_config": {"type": "Merging"}}
    assert isinstance(
        instantiate_workflow_element_from_type(workflow_step, 1),
        WorkflowElement,
    )


def test_find_parent_prod_step() -> None:
    workflow_element_list: list[WorkflowElement] = [
        WorkflowElement(ProductionStep(), "merging"),
        WorkflowElement(ProductionStep(), "merging"),
    ]
    workflow_step = {"ID": 1, "input_meta_query": {}, "job_config": {"type": "Merging"}}
    assert find_parent_prod_step(workflow_element_list, workflow_step) is None

    workflow_step = {"ID": 1, "input_meta_query": {"parentID": None}, "job_config": {}}
    assert find_parent_prod_step(workflow_element_list, workflow_step) is None

    workflow_step = {"ID": 2, "input_meta_query": {"parentID": 1}, "job_config": {}}
    assert isinstance(
        find_parent_prod_step(workflow_element_list, workflow_step),
        ProductionStep,
    )


def test_get_parents_list() -> None:
    cases = [
        {
            "config": [
                {"ID": 1, "input_meta_query": {}, "job_config": {}},
                {"ID": 2, "input_meta_query": {"parentID": 1}, "job_config": {}},
            ],
            "expected_result": [1],
        },
        {
            "config": [
                {"ID": 1, "input_meta_query": {}, "job_config": {}},
                {"ID": 2, "input_meta_query": {"parentID": 1}, "job_config": {}},
                {"ID": 3, "input_meta_query": {"parentID": 1}, "job_config": {}},
            ],
            "expected_result": [1, 1],
        },
        {
            "config": [
                {"ID": 1, "input_meta_query": {}, "job_config": {}},
                {"ID": 2, "input_meta_query": {"parentID": 1}, "job_config": {}},
                {"ID": 3, "input_meta_query": {"parentID": 2}, "job_config": {}},
            ],
            "expected_result": [1, 2],
        },
    ]
    for case in cases:
        assert get_parents_list(case["config"]) == case["expected_result"]


def test_check_input_source_unicity() -> None:
    workflow_config = [
        {
            "ID": 1,
            "input_meta_query": {"parentID": 3, "dataset": "DATASET"},
            "job_config": {},
        }
    ]
    with pytest.raises(SystemExit) as exc_info:
        check_parents(workflow_config)
    assert str(exc_info.value) == "-1"

    workflow_config = [
        {
            "ID": 1,
            "input_meta_query": {"parentID": 1, "dataset": None},
            "job_config": {},
        },
    ]
    assert check_parents(workflow_config) is True

    workflow_config = [
        {
            "ID": 1,
            "input_meta_query": {"parentID": 1, "job_config": {}},
        },
    ]
    assert check_parents(workflow_config) is True


def test_check_destination_catalogs() -> None:
    default_catalogs = json.dumps(["DIRACFileCatalog", "TSCatalog"])
    workflow_element = WorkflowElement(ProductionStep(), "mcsimulation")
    workflow_element.job.catalogs = default_catalogs
    parents_list = [1]
    with pytest.raises(SystemExit) as exc_info:
        check_destination_catalogs(
            workflow_element,
            {
                "ID": 1,
                "input_meta_query": {},
                "job_config": {"catalogs": "DIRACFileCatalog"},
            },
            parents_list,
        )
    assert str(exc_info.value) == "-1"

    workflow_step = {
        "ID": 2,
        "input_meta_query": {},
        "job_config": {"catalogs": "DIRACFileCatalog"},
    }
    assert (
        check_destination_catalogs(workflow_element, workflow_step, parents_list)
        is True
    )

    workflow_step = {
        "ID": 1,
        "input_meta_query": {},
        "job_config": {"catalogs": "DIRACFileCatalog, TSCatalog"},
    }
    assert (
        check_destination_catalogs(workflow_element, workflow_step, parents_list)
        is True
    )
    workflow_step = {"ID": 1, "input_meta_query": {}, "job_config": {}}
    assert (
        check_destination_catalogs(workflow_element, workflow_step, parents_list)
        is True
    )


def test_check_and_sort_workflow_config() -> None:
    workflow_config = {
        "ProdSteps": [
            {
                "ID": 1,
                "input_meta_query": {"parentID": None, "dataset": None},
                "job_config": {},
            },
            {
                "ID": 2,
                "input_meta_query": {"parentID": 3, "moon": "dark"},
                "job_config": {},
            },
        ]
    }
    with pytest.raises(SystemExit) as exc_info:
        check_and_sort_workflow_config(workflow_config)
    assert str(exc_info.value) == "-1"


def test_instanciate_and_build_workflow_element() -> None:
    res_we = instanciate_and_build_workflow_element(
        SIMULATION_CONFIG, WORKFLOW_CONFIG, None, [1, 2, 3], "ps"
    )
    assert isinstance(res_we, WorkflowElement)
    assert isinstance(res_we.job, MCPipeJob)
