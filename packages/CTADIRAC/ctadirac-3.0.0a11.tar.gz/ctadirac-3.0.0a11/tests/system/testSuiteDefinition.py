""" Test definitions for submission and monitoring of jobs, transformations and productions
"""
import unittest
import subprocess as sp
import os
from glob import glob

import DIRAC
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog


from testJobDefinitions import (
    hello_world,
    hello_world_site_spec,
    mp_job,
    mandelbrot_simulation,
)
from testProdDefinitions import (
    create_prod_step1,
    clean_prod,
    start_prod,
    create_prod,
    get_prod_transformations,
)
from testTransDefinitions import (
    create_mc_transformation,
    get_trans,
    clean_trans,
    extend_trans,
    check_trans_status,
)
from testDMSDefinitions import (
    ClientDMS,
    DMSmetadata,
)
from testFileCatalogDefinitions import ClientFileCatalog

DIRAC.initialize()  # Initialize configuration

dirac = Dirac()

"""To add parser and running or skipping test using unittest
see: https://docs.python.org/3/library/unittest.html#skipping-tests-and-expected-failures
"""


class WMSTestCase(unittest.TestCase):
    """Base class for the Regression test cases"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_var()

    def init_var(
        self,
        sites=None,
        s_elements=None,
        test_dir="/ctao/tests/wms",
        input_file="WMS_TestInputFile.txt",
        output_file="WMS_TestOutputFile.txt",
        exe_script="exe_script.sh",
        trans_name="MCTransTest",
        prod_name="SeqProdTest",
        output_se="CSCS-Disk",
        prod_config="config/full_production_config.yml",
        n_tasks=21,
        test_to_skip=None,
    ):
        if not s_elements:
            self.s_elements = ["CSCS-Disk"]
        else:
            self.s_elements = s_elements
        if not sites:
            self.sites = [
                "CTAO.DESY-ZEUTHEN.de",
                "CTAO.PIC.es",
                "CTAO.CSCS.ch",
                "CTAO.FRASCATI.it",
            ]
        else:
            self.sites = sites
        self.test_dir = test_dir
        self.input_file = input_file
        self.output_file = output_file
        self.exe_script = exe_script
        self.inputLFN = os.path.join(self.test_dir, self.input_file)
        self.jobsSubmittedList = []
        self.trans_name = trans_name
        self.prod_name = prod_name
        self.output_se = output_se
        for dir, _, _ in os.walk(os.getcwd()):
            if glob(os.path.join(dir, prod_config)):
                self.prodConfigFile = os.path.join(dir, prod_config)
        self.n_tasks = n_tasks
        self.separation = (
            "----------------------------------------------------------------------"
        )
        self.test_to_skip = test_to_skip

    def setUp(
        self,
    ):  # to initialize the execution context. Called before the execution of each test method
        # a check on proxy for example can be added here
        pass

    def tearDown(
        self,
    ):  # called after the execution of each test method. To clean (close files, etc).
        pass


class JobExecutionTests(WMSTestCase):
    """submit jobs"""

    def test_submit_hello(self):
        """submit a hello world job, check status and logs"""
        print("\n")
        res = hello_world()
        self.assertTrue(res["OK"])
        # get job status
        jobid = res["Value"]
        res = Dirac().getJobStatus(jobid)
        self.assertTrue(res["OK"])
        # get logging informations
        res = Dirac().getJobLoggingInfo(jobid)
        self.assertTrue(res["OK"])

    def test_submit_sites(self):
        """submit a hello world job to a specific site"""
        print("\n")
        for site in self.sites:
            with self.subTest(i=site):
                res = hello_world_site_spec(site=site)
                self.assertTrue(res["OK"])

    def test_submit_mp(self):
        """submit a job requiring multiple cores"""
        print("\n")
        res = mp_job()
        self.assertTrue(res["OK"])

    def test_submit_mandelbrot_sim(self):
        """submit a mandelbrot simulation job"""
        print("\n")
        res = mandelbrot_simulation()
        self.assertTrue(res["OK"])


class TransformationExecutionTests(WMSTestCase):
    def test01_submit_transformation(self):
        print("\n")
        print(self.separation)
        res = get_trans(self.trans_name)
        if res["OK"]:
            print(f"Clean existing transformation {self.trans_name}")
            if res["Value"]["TransformationName"] == self.trans_name:
                res = clean_trans(self.trans_name)
                self.assertTrue(res["OK"])

        # create a MC transformation
        print("Create transformation")
        res = create_mc_transformation(self.trans_name)[0]
        self.assertTrue(res["OK"])

    def test02_extend_transformation(self):
        print("\n")
        print(self.separation)
        # extend the transformation
        print(f"Extend transformation {self.trans_name}")
        res = extend_trans(self.trans_name, self.n_tasks)
        self.assertTrue(res["OK"])

    def test03_monitor_transformation(self):
        print("\n")
        print(self.separation)
        # check the status of the transformation
        print(f"Check status of transformation {self.trans_name}")
        res = check_trans_status(self.trans_name)
        self.assertTrue(res["OK"])


class ProductionConfigurationTests(WMSTestCase):
    def test01_configure_production(self):
        print("\n")
        print(self.separation)
        prod_name = "prodTestFullProduction"
        res = sp.run(
            [f"cta-prod-submit {prod_name} {self.prodConfigFile} dry-run"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)


class ProductionExecutionTests(WMSTestCase):
    def test01_submit_production(self):
        print("\n")
        print(self.separation)
        print("Create Prod Step 1")
        res = create_prod_step1()[0]
        self.assertTrue(res["OK"])

        print(self.separation)
        print(f"Clean existing prod with name {self.prod_name}")
        res = clean_prod(prod_name=self.prod_name)
        self.assertTrue(res["OK"])

        print(self.separation)
        print(f"Create production {self.prod_name}")
        res = create_prod(prod_name=self.prod_name)
        self.assertTrue(res["OK"])

        print(self.separation)
        print(f"Start production {self.prod_name}")
        res = start_prod(prod_name=self.prod_name)
        self.assertTrue(res["OK"])

        print(self.separation)
        trans_list = get_prod_transformations(self.prod_name)
        for trans in trans_list:
            trans_id = trans["TransformationID"]
            print(f"Extend transformation {trans_id}")
            res = extend_trans(trans_id, n_tasks=self.n_tasks)
            self.assertTrue(res["OK"])

    def test02_monitor_production(self):
        print("\n")
        print(self.separation)
        res = sp.run(
            [f"dirac-prod-get {self.prod_name}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)

    def test03_monitor_production(self):
        print("\n")
        print(self.separation)
        res = sp.run(
            [f"dirac-prod-get-trans {self.prod_name}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)


class ProdSystemFullTests(WMSTestCase):
    """submit a full production composed of MC simulation, processing and 2 steps of merging"""

    def test_submit_full_prod(self):
        print("\n")
        print(self.separation)
        test_dir = "/ctao/tests/prodsys/MC"
        prod_name = "prodTestFullProduction"
        prod_test_dir = os.path.join(test_dir, "Prod5bTest/LaPalma/gamma-diffuse")

        # create test directory if not empty
        fc = FileCatalog()
        res = fc.createDirectory(prod_test_dir)
        if not res["OK"]:
            print(f"Failed to create directory {prod_test_dir}")
        self.assertTrue(res["OK"])
        # clean test directory
        res = sp.run(
            [f"dirac-dms-clean-directory {prod_test_dir}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)

        # create metadata fields
        dms_metadata = DMSmetadata()
        res = fc.createDirectory(dms_metadata.dataset_dir)
        self.assertTrue(res["OK"])
        res = dms_metadata.add_dir_md_in_dfc()
        self.assertTrue(res["OK"])
        res = dms_metadata.add_file_md_in_dfc()
        self.assertTrue(res["OK"])
        # clean an eventual existing production
        res = clean_prod(prod_name)
        self.assertTrue(res["OK"])
        res = sp.run(
            [f"cta-prod-submit {prod_name} {self.prodConfigFile}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)

        trans_list = get_prod_transformations(prod_name)
        for trans in trans_list:
            trans_id = trans["TransformationID"]
            res = get_trans(trans_id)
            trans_type = res["Value"]["Type"]
            if trans_type == "MCSimulation":
                print(f"Extend transformation {trans_id}")
                res = extend_trans(trans_id=trans_id, n_tasks=10)
                self.assertTrue(res["OK"])


class ClientDMSDatasetTests(WMSTestCase):
    """Test Client DMS using dataset"""

    def dirac_dms_metadata(self):
        print("\n")
        print(self.separation)
        dms_md = DMSmetadata()
        test_cases = dms_md.main()

        for tests in test_cases.keys():
            with self.subTest(i=tests):
                for res in test_cases[tests]():
                    if isinstance(res, dict):
                        self.assertTrue(res["OK"])
                    elif isinstance(res, bool):
                        self.assertTrue(res)

    def cta_prod_dataset(self):
        """Test dataset command line client"""
        print("\n")
        print(self.separation)
        test_dataset = "Prod5b_LaPalma_AdvancedBaseline_NSB1x_electron_North_20deg_R1"
        test_dataset_json = "datasets/Prod5b_LaPalma_AdvancedBaseline_NSB1x_electron_North_20deg_R1.json"

        commands = [
            f"cta-prod-add-dataset {test_dataset_json}",
            f"cta-prod-update-dataset {test_dataset}",
            f"cta-prod-show-dataset {test_dataset} -l",
        ]

        for cmd in commands:
            with self.subTest(i=cmd):
                res = sp.getstatusoutput(cmd)
                print(res[1])
                self.assertEqual(res[0], 0)

    def test_dms_client_dataset(self):
        self.dirac_dms_metadata()
        self.cta_prod_dataset()


class ClientDMSTests(WMSTestCase):
    """test data management"""

    def test_client_dms(self):
        dms = ClientDMS()
        dms.write_test_file()
        print("====== Using SE", dms.dest_se1, dms.dest_se2)
        print("\n")
        print("====== Using test LFN", dms.test_lfn)
        print(dms.test_dir)
        res = sp.run(
            [f"set -x; dirac-dms-clean-directory {dms.test_dir}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [
                f"set -x; dirac-dms-add-file {dms.test_lfn} ./{dms.test_file} {dms.dest_se1}"
            ],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        sp.run([f"mv {dms.test_file} {dms.test_file}.old"], shell=True, check=True)
        res = sp.run(
            [f"set -x; dirac-dms-replicate-lfn  {dms.test_lfn} {dms.dest_se2}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-catalog-metadata {dms.test_lfn}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-lfn-metadata {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-lfn-accessURL {dms.test_lfn} {dms.dest_se1}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-get-file {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run([f"ls {dms.test_file}"], shell=True, check=True)
        self.assertEqual(res.returncode, 0)
        if res.returncode:
            print("File downloaded properly")
        res = sp.run(
            [f"set -x; dirac-dms-lfn-replicas {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-remove-replicas {dms.test_lfn} {dms.dest_se2}"],
            shell=True,
            check=True,
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-lfn-replicas {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-remove-files {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        res = sp.run(
            [f"set -x; dirac-dms-lfn-replicas {dms.test_lfn}"], shell=True, check=True
        )
        self.assertEqual(res.returncode, 0)
        sp.run([f"rm {dms.test_file}"], shell=True, check=True)
        sp.run([f"rm {dms.test_file}.old"], shell=True, check=True)


class ClientRucioFileCatalogTests(WMSTestCase):
    """test Rucio file catalog"""

    def test_client_file_catalog(self):
        fc = ClientFileCatalog("RucioFileCatalog")
        fc.write_test_file()

        res = fc.create_directory()
        self.assertTrue(res["OK"])

        res = fc.list_directory()
        self.assertTrue(res["OK"])

        res = fc.register_file()
        self.assertTrue(res["OK"])

        res = fc.put_and_register()
        self.assertTrue(res["OK"])

        res = fc.remove_file()
        self.assertTrue(res["OK"])


class ClientDIRACFileCatalogTests(WMSTestCase):
    """test DIRAC file catalog"""

    def test_client_file_catalog(self):
        fc = ClientFileCatalog("DIRACFileCatalog")
        fc.write_test_file()

        res = fc.create_directory()
        self.assertTrue(res["OK"])

        res = fc.list_directory()
        self.assertTrue(res["OK"])

        res = fc.register_file()
        self.assertTrue(res["OK"])

        res = fc.remove_file()
        self.assertTrue(res["OK"])

        res = fc.put_and_register()
        self.assertTrue(res["OK"])

        res = fc.remove_file()
        self.assertTrue(res["OK"])
