import json
from CTADIRAC.ProductionSystem.Client.WorkflowElement import (
    WorkflowElement,
    WorkflowElementTypes,
)
import DIRAC


def check_id(workflow_config):
    """Check step ID values"""
    for workflow_step in workflow_config:
        if not workflow_step.get("ID"):
            DIRAC.gLogger.error("Unknown step ID")
            DIRAC.exit(-1)
        elif not isinstance(workflow_step["ID"], int):
            DIRAC.gLogger.error("step ID must be integer")
            DIRAC.exit(-1)
    return True


def sort_by_id(workflow_config):
    """Sort workflow steps by ID"""
    return sorted(workflow_config, key=lambda k: k["ID"])


def check_parents(workflow_config):
    """Check if parent step is listed before child step"""
    for workflow_step in workflow_config:
        if workflow_step["input_meta_query"].get("parentID"):
            if workflow_step["input_meta_query"]["parentID"] > workflow_step["ID"]:
                DIRAC.gLogger.error(
                    "A step can only have a parent which ID is inferior to its ID"
                )
                DIRAC.exit(-1)
    return True


def instantiate_workflow_element_from_type(workflow_step, parent_prod_step):
    """Instantiate workflow element class based on the step type required"""
    wf_elt = None
    we_type: str = workflow_step["job_config"]["type"].lower()
    if we_type in WorkflowElementTypes.we_types:
        wf_elt = WorkflowElement(parent_prod_step, we_type)
    else:
        DIRAC.gLogger.error("Unknown step type")
        DIRAC.exit(-1)
    return wf_elt


def find_parent_prod_step(workflow_element_list, workflow_step):
    """Find parent prod step for a given workflow element"""
    parent_prod_step = None
    if workflow_step["input_meta_query"].get("parentID"):
        parent_prod_step = workflow_element_list[
            workflow_step["input_meta_query"]["parentID"] - 1
        ].prod_step  # Python starts indexing at 0
    return parent_prod_step


def get_parents_list(workflow_config):
    parents_list = []
    for workflow_step in workflow_config:
        if workflow_step["input_meta_query"].get("parentID"):
            parents_list.append(workflow_step["input_meta_query"]["parentID"])
    return parents_list


def check_input_source_unicity(workflow_config):
    for workflow_step in workflow_config:
        if workflow_step["input_meta_query"].get("parentID"):
            if workflow_step["input_meta_query"].get("dataset"):
                DIRAC.gLogger.error(
                    "A step cannot have input data from a dataset and from a parent"
                )
                DIRAC.exit(-1)
    return True


def check_destination_catalogs(workflow_element, workflow_step, parents_list):
    """If a change in the destination catalogs is asked by the user, check that the step does not have any children.
    This function needs to be called before setting job attributes."""
    if workflow_step["job_config"].get("catalogs"):
        if workflow_step["ID"] in parents_list:
            # Check that the default catalogs value is different from the catalogs value asked by the user
            # to issue an error
            if workflow_element.job.catalogs != json.dumps(
                workflow_step["job_config"]["catalogs"]
                .replace(", ", ",")
                .split(sep=",")
            ):
                DIRAC.gLogger.error(
                    "Catalogs can only be changed for production steps without any children."
                )
                DIRAC.exit(-1)
    return True


def check_and_sort_workflow_config(workflow_config):
    check_id(workflow_config["ProdSteps"])
    workflow_config["ProdSteps"] = sort_by_id(workflow_config["ProdSteps"])
    check_parents(workflow_config["ProdSteps"])


def instanciate_and_build_workflow_element(
    workflow_step,
    workflow_config,
    parent_prod_step,
    parents_list,
    mode,
):
    workflow_element = instantiate_workflow_element_from_type(
        workflow_step, parent_prod_step
    )
    # Temporary : later maybe remove if we allow only DFC
    # check_destination_catalogs(workflow_element, workflow_step, parents_list)
    DIRAC.gLogger.notice(
        f"\nBuilding Production step: {workflow_step['job_config']['type']} ..."
    )
    # The order of the following instructions matters
    workflow_element.build_input_data(workflow_step)
    workflow_element.build_job_attributes(workflow_config, workflow_step)
    workflow_element.build_job_output_data(workflow_step)
    workflow_element.build_element_config(workflow_step)
    workflow_element.build_output_data()
    workflow_element.build_job_input_data(mode)
    return workflow_element
