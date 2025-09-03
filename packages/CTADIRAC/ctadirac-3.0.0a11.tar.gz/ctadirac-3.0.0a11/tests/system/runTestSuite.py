#!/usr/bin/env python

"""
Run unittest test suite

Usage:
    python runTestSuite.py JobExecutionTests"""

import unittest
from DIRAC.Core.Base.Script import Script

# import test suite definition
from testSuiteDefinition import (
    JobExecutionTests,
    TransformationExecutionTests,
    ProductionExecutionTests,
    ProductionConfigurationTests,
    ProdSystemFullTests,
    ClientDMSTests,
    ClientDIRACFileCatalogTests,
    ClientRucioFileCatalogTests,
    ClientDMSDatasetTests,
)

test_cases = [
    "JobExecutionTests TransformationExecutionTests ProductionExecutionTests "
    "ProductionConfigurationTests ProdSystemFullTests ClientDMSTests ClientDIRACFileCatalogTests "
    "ClientRucioFileCatalogTests ClientDMSDatasetTests "
]

Script.registerArgument(description=["tests: Test cases list"], values=test_cases)
Script.parseCommandLine()

from DIRAC import gLogger

argss = Script.getPositionalArgs()
if len(argss) < 1:
    Script.showHelp()

debug = Script.localCfg.getDebugMode()

if debug > 0:
    log_file = "TestJobs.log"
    gLogger.registerBackend("file", {"FileName": f"{log_file}"})
    gLogger.setLevel(debug)


suite = unittest.TestSuite()

for case in argss:
    test = unittest.defaultTestLoader.loadTestsFromTestCase(eval(case))
    suite.addTest(test)

testResult = unittest.TextTestRunner(verbosity=2).run(suite)

if not testResult.wasSuccessful():
    exit(1)
