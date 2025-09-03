"""
    Class to handle a workflow described in CWL
"""

__RCSID__ = "$Id$"

import os
import schema_salad
from cwltool.context import LoadingContext
from cwltool.load_tool import load_tool
import cwltool.process
from CTADIRAC.ProductionSystem.CWL.CWLWorkflowStep import WorkflowStep
from CTADIRAC.ProductionSystem.CWL.CWLUtils import get_source_name, topological_sort


class Workflow:
    """Class for workflow made of one or more workflow steps"""

    #############################################################################

    def __init__(self):
        """Constructor"""
        self.ordered_steps = []
        self.process = None
        self.inputs = None
        self.ext_inputs = {}
        self.sources = {}
        self.sources_outputs = {}

    def load(self, input_cwl, input_yaml):
        uri = "file://" + os.path.abspath(input_yaml)
        loader = schema_salad.ref_resolver.Loader(
            {"@base": uri, "path": {"@type": "@id"}}
        )
        loading_context = LoadingContext({"strict": False, "debug": True})
        self.inputs, _ = loader.resolve_ref(uri)
        self.process = load_tool(input_cwl, loading_context)

    def get_ext_inputs(self):
        # Match each workflow input with the corresponding value in the yaml input file
        for inp in self.process.tool["inputs"]:
            self.ext_inputs[inp["id"]] = self.inputs[
                cwltool.process.shortname(inp["id"])
            ]

    def get_steps_order_and_sources(self):
        deps = []
        for step in self.process.steps:
            self.sources[step] = []
            self.sources_outputs[step] = []
            parent_steps_id = set()
            for inp in step.tool["inputs"]:
                # If the input is created in another step:
                if "source" in inp and inp["source"] not in self.ext_inputs:
                    self.sources[step].append(inp)
                    parent_step_id = get_source_name(inp["source"])
                    # Find step corresponding to the step id
                    for s in self.process.steps:
                        if s.id == parent_step_id:
                            parent_step_id = s
                            for out in parent_step_id.tool["outputs"]:
                                self.sources_outputs[step].append(out)
                    parent_steps_id.add(parent_step_id)
            deps.append([step, parent_steps_id])

        for step in topological_sort(deps):
            self.ordered_steps.append(step)

    def run_workflow(self, input_yaml):
        cmd_list = []
        self.get_ext_inputs()
        self.get_steps_order_and_sources()
        for ordered_step in self.ordered_steps:
            step = WorkflowStep()
            step.process = ordered_step
            step.sources = self.sources[ordered_step]
            step.sources_outputs = self.sources_outputs[ordered_step]
            input_cwl = step.process.tool["run"].replace("file://", "")
            step.load(
                input_cwl,
                input_yaml,
                sources=step.sources,
                sources_outputs=step.sources_outputs,
            )
            step = step.get_command_line(
                sources=step.sources, sources_outputs=step.sources_outputs
            )
            cmd_list.append(step.command_line)
        return cmd_list
