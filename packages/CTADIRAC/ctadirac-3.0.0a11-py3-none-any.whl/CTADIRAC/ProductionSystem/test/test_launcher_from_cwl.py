import unittest
import os
import CTADIRAC.ProductionSystem.scripts.cta_prod_submit_from_cwl as launcher_cwl


# TODO: rewrite this test using pytest:
class TestWorkflowStep(unittest.TestCase):
    def test_get_command_line(self):
        wf = launcher_cwl.WorkflowStep()
        input_cwl = "../CWL/setup-software.cwl"
        input_yaml = "../CWL/setup-software.yml"
        if os.path.isfile(input_yaml) and os.path.isfile(input_cwl):
            wf.get_command_line(input_cwl, input_yaml)
            actual = wf.command_line
            expected = "cta-prod-setup-software -p corsika_simtelarray -v 2022-08-03 -a simulations -g gcc83_matchcpu"
            self.assertEqual(actual, expected)
