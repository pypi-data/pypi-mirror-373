import concurrent.futures
from collections import defaultdict
from typing import Any, Union
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.ReturnValues import DOKReturnType, DErrorReturnType
from DIRAC.Core.Base.AgentModule import AgentModule

from DIRAC.TransformationSystem.Client import (
    TransformationStatus,
    TransformationFilesStatus,
)
from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import (
    JobMonitoringClient,
)
from DIRAC.WorkloadManagementSystem.Client import JobStatus
from CTADIRAC.TransformationSystem.Utils.FailoverUtilities import FailoverUtilities
from CTADIRAC.Core.Utilities.return_values import s_report, DReportReturnType

AGENT_NAME = "Transformation/TransformationFailoverAgent"


class TransformationFailoverAgent(AgentModule, FailoverUtilities):
    """TransformationFailoverAgent:
    An Agent to manage failovers during Transformations
    Sends report, reassign files, complete or flush transfomations depending on configuration.
    Need a specific configuration for the agent:
    - TransformationStatus: Check the transformations with specific status (default: 'Active')
    - TransformationTypes: Check the transformations with specific types (default: None)
    - Report: Transformation type to report (default == TransformationTypes)
    - Complete: Complete transformation with specified type if conditions (default: None)
    - MaxFlush: Maximum times a transformation can be flushed (default: 2)
    - Flush: Flush transformation with specified type if conditions are fullfilled (default: None)
    - Reassign: Reassigned files to create new tasks when there is failed tasks in the transformation with specified type (default: None)
    - MaxReassign: Maximum number of reassigning files (default: 2)
    - maxThreadsInPool: Number of threads used by the agent
    - MailTo: Send report to sepcified mail adress
    - htmlReport: Return the report as html format (default: True)
    """

    def __init__(self, *args, **kwargs) -> None:
        AgentModule.__init__(self, *args, **kwargs)
        FailoverUtilities.__init__(self, agent_name=AGENT_NAME)

        self.trigger_job_status: list[str] = [JobStatus.FAILED, JobStatus.KILLED]
        self.failed_final_task_status: list[str] = [JobStatus.FAILED, JobStatus.KILLED]
        self.jobs_final_status: list[str] = [
            JobStatus.DONE,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.KILLED,
        ]
        self.default_transformation_status: list[str] = [TransformationStatus.ACTIVE]
        self.file_status_to_check = TransformationFilesStatus.ASSIGNED
        self.trans_with_no_input: list = ["MCSimulation"]
        self.html = True

        self.job_mon = JobMonitoringClient()

        self.get_cs_options()

        self.mail_to = ""
        self.mail_from = "noreply@ctao.dirac"
        self.subject = "[TransformationFailoverAgent]"

        self.reassign_count = {}
        self.flush_count = {}

    def initialize(self) -> DOKReturnType[None]:
        """Agent's initialisation"""
        self.mail_from = self.am_getOption("MailFrom", self.mail_from)
        self.mail_to = self.am_getOption("MailTo", self.mail_to)

        max_number_of_threads = self.am_getOption("maxThreadsInPool", 15)
        gLogger.info(f"Multithreaded with {max_number_of_threads} threads")
        self.thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_number_of_threads
        )
        return S_OK()

    def get_cs_options(self) -> None:
        """Re initialize before execution"""

        self.html = self.am_getOption("htmlReport", self.html)
        self.transformation_status = self.am_getOption(
            "TransformationStatus", self.default_transformation_status
        )

        self.transformation_types = self.am_getOption("TransformationTypes", [])
        self.transformation_to_report = self.am_getOption(
            "Report", self.transformation_types
        )
        self.transformations_to_complete = self.am_getOption("Complete", [])
        self.transformation_to_flush = self.am_getOption("Flush", [])
        self.transformation_to_reassign = self.am_getOption("Reassign", [])

        self.max_flush = self.am_getOption("MaxFlush", 2)
        self.max_reassign = self.am_getOption("MaxReassign", 2)

    def should_complete_transformation(
        self, trans_type: str, trans_id: int, parent_id: int
    ) -> bool:
        """Check if transformation should be completed.
        i.e. has input, is processed and has no parent
        or parent is processed"""
        not_completed_message: str = (
            f"[{trans_id}] Do not complete transformation: requirement not satisfied"
        )
        if (
            trans_type in self.trans_with_no_input
            or trans_type not in self.transformations_to_complete
            or parent_id is None
        ):
            gLogger.info(not_completed_message)
            return False

        if self.is_transformation_processed(trans_id) and (
            parent_id == -1
            or (parent_id != -1 and self.is_transformation_processed(parent_id))
            or (parent_id != -1 and self.get_parent_type(parent_id) == "MCSimulation")
        ):
            gLogger.info(f"[{trans_id}] Completing transformation...")
            return True

        gLogger.info(not_completed_message)
        return False

    def execute_transformation_check(
        self, trans_id: int, trans_info_dict: dict
    ) -> Union[DReportReturnType, DErrorReturnType, DOKReturnType[dict], Any]:
        """Check transformation before creating a report
        if necessary flush and reassign files"""
        gLogger.info(f"[{trans_id}] Treating Transformation...")

        trans_type = trans_info_dict["Type"]
        parent_id = self.get_parent_transformation_id(trans_id)
        reassigned_lfns: dict = {}
        no_report: str = f"[{trans_id}] Report not created"

        tasks_infos = self.get_transformation_tasks(trans_id)["Value"]

        jobs_id: list = [
            job["ExternalID"] for job in tasks_infos if job["ExternalID"] != "0"
        ]
        res_jobs_attributes = self.job_mon.getJobsParameters(
            jobs_id, self.attributes_of_interest
        )
        if not res_jobs_attributes["OK"]:
            return s_report(False, f"{res_jobs_attributes}")

        jobs_attributes: dict = res_jobs_attributes["Value"]

        is_there_updated_tasks: bool = self.update_tasks_status(
            trans_id, jobs_attributes, tasks_infos
        )
        if is_there_updated_tasks:
            tasks_infos = self.get_transformation_tasks(trans_id)["Value"]

        # Do nothing if all files are processed and complete transformation:
        if self.should_complete_transformation(trans_type, trans_id, parent_id):
            return self.complete_transformation(trans_id)

        if (
            trans_type not in self.trans_with_no_input
            and self.is_transformation_processed(trans_id)
        ):
            return s_report(False, f"[{trans_id}] is processed")

        # Check if transformation needs to be flushed
        has_been_flushed = False
        if (
            trans_type in self.transformation_to_flush
            and self.flush_count.setdefault(trans_id, 0) < self.max_flush
        ):
            group_size: int = trans_info_dict["GroupSize"]
            has_been_flushed: bool = self.flush_transformation(
                trans_id, group_size, parent_id, tasks_infos
            )

        # Set files status to unused if associated tasks failed or killed
        if trans_type in self.transformation_to_reassign and not has_been_flushed:
            reassigned_lfns = self.reassign_lfn(trans_id)

        if trans_type not in self.transformation_to_report:
            return s_report(
                False, f"{no_report}: {trans_type} type should not be reported"
            )

        # Create Report on transformation
        report_result = self.parse_transformation_jobs_attributes(
            trans_id, jobs_attributes
        )

        if not report_result["OK"]:
            return report_result

        if reassigned_lfns:
            report_lfns: str = self.create_reassigned_lfn_report(
                trans_id, reassigned_lfns
            )
            return s_report(True, report_result["Value"] + report_lfns)

        return s_report(True, report_result["Value"])

    def update_tasks_status(
        self, trans_id: int, jobs_attributes: dict, tasks_infos: list
    ) -> bool:
        """Update task status in TransformationDB"""
        tasks_status_dict = {}
        has_been_updated = False
        for task in tasks_infos:
            tasks_status_dict[int(task["ExternalID"])] = {
                "ExternalStatus": task["ExternalStatus"],
                "TransformationID": task["TransformationID"],
                "TaskID": task["TaskID"],
            }
        for job_id, job_info in jobs_attributes.items():
            try:
                if tasks_status_dict[job_id]["ExternalStatus"] != job_info["Status"]:
                    gLogger.verbose(
                        f"[{trans_id}] Setting new task [{tasks_status_dict[job_id]['TaskID']}] status"
                    )
                    res = self.set_task_status(
                        tasks_status_dict[job_id]["TransformationID"],
                        tasks_status_dict[job_id]["TaskID"],
                        job_info["Status"],
                    )
                    if not res["OK"]:
                        gLogger.error(f"[{trans_id}] {res}")
                        continue
                    else:
                        gLogger.verbose(
                            f"[{trans_id}] Task [{tasks_status_dict[job_id]['TaskID']}] status changed: {tasks_status_dict[job_id]['ExternalStatus']} => {job_info['Status']}"
                        )
                        has_been_updated = True
            except KeyError as ke:
                gLogger.error(f"[{trans_id}] {ke}")
                continue
        return has_been_updated

    def get_lfns_to_assign(self, trans_id: int, failed_tasks: list) -> dict[int, str]:
        """Get LFNs to assign based on failed tasks"""
        lfns_to_assign = {}
        if not isinstance(failed_tasks, list):
            failed_tasks_list = [task[0] for task in failed_tasks]
        else:
            failed_tasks_list = failed_tasks
        res_trans_files = self.get_transformation_files(
            {"TransformationID": trans_id, "TaskID": failed_tasks_list}
        )
        if res_trans_files["OK"]:
            for trans_file in res_trans_files["Value"]:
                lfn = trans_file["LFN"]
                if (
                    lfn not in self.reassign_count
                    or self.reassign_count[lfn] <= self.max_reassign
                ):
                    index = trans_file["TaskID"]
                    lfns_to_assign.setdefault(index, [])
                    lfns_to_assign[index] += [lfn]
                    self.update_reassign_count(lfn)
        else:
            gLogger.error(
                f"[{trans_id}] Failed to getTransformationFiles: {res_trans_files}"
            )
        return lfns_to_assign

    def update_reassign_count(self, lfn: str) -> None:
        """Update reassign count for the specified LFN"""
        if lfn in self.reassign_count:
            self.reassign_count[lfn] += 1
        else:
            self.reassign_count[lfn] = 1

    def reassign_lfn(self, trans_id: int) -> dict[int, list]:
        """Set LFNs to Unused if failed or killed tasks"""
        lfns_to_assign: dict = {}
        reassigned_lfns: dict = {}
        res_assigned_tasks_status = self.trans_client.get_tasks_by_file_status(
            trans_id, self.file_status_to_check, self.failed_final_task_status
        )
        if res_assigned_tasks_status["OK"]:
            failed_tasks = res_assigned_tasks_status["Value"]
            if failed_tasks:
                lfns_to_assign = self.get_lfns_to_assign(trans_id, failed_tasks)
                lfns = [
                    lfn for tasks_lnfs in lfns_to_assign.values() for lfn in tasks_lnfs
                ]
                gLogger.verbose(
                    f"[{trans_id}] Changing files status to unused on lnfs: {lfns_to_assign}"
                )
                res = self.trans_client.setFileStatusForTransformation(
                    trans_id,
                    newLFNsStatus=TransformationFilesStatus.UNUSED,
                    lfns=lfns,
                    force=True,
                )
                if not res["OK"]:
                    gLogger.error(f"[{trans_id}] {res}")
                else:
                    gLogger.info(f"[{trans_id}] Files status changed successfully")
                    reassigned_lfns = lfns_to_assign
        else:
            gLogger.error(f"{trans_id}: {res_assigned_tasks_status}")

        return reassigned_lfns

    def flush_transformation(
        self, trans_id: int, group_size: dict, parent_id: int, tasks_infos: list
    ) -> bool:
        """Flush transformation if necessary conditions are fullfilled"""
        parent_status = None
        res_parent_trans = self.trans_client.getTransformation(parent_id)
        if res_parent_trans["OK"]:
            parent_status = res_parent_trans["Value"]["Status"]

        flush_trans, message = self.should_flush_transformation(
            trans_id, parent_id, parent_status, group_size, tasks_infos
        )
        if flush_trans:
            self.execute_flush(trans_id, message)
        return flush_trans

    def execute_flush(self, trans_id: int, message: str):
        """Actually flush the transformation"""
        res_flush = self.trans_client.setTransformationParameter(
            trans_id, paramName="Status", paramValue=TransformationStatus.FLUSH
        )
        if res_flush["OK"]:
            self.send_mail(
                subject=self.subject + f"Flush Transformation {trans_id}",
                message=message,
            )
            self.flush_count[trans_id] += 1
            gLogger.info(f"[{trans_id}] {message}")
        else:
            gLogger.error(res_flush)

    def should_flush_transformation(
        self,
        trans_id: int,
        parent_id: int,
        parent_status: str,
        group_size: int,
        tasks_infos: list,
    ) -> tuple[bool, str]:
        flush_trans = False
        count_unused = 0
        message = ""
        if parent_id != -1 and parent_status != TransformationStatus.COMPLETED:
            gLogger.info(
                f"[{trans_id}] Parent Transformation {parent_id} is not complete yet."
            )
        else:
            count_unused: int = self.get_count_size(trans_id)
            if count_unused != 0 and group_size > count_unused:
                flush_trans = True
                message: str = (
                    "Nb of files with Status 'Unused' "
                    f"({count_unused}) < GroupSize ({group_size})\n"
                    f"The Transformation {trans_id} has been Flushed"
                )
            elif count_unused != 0 and group_size <= count_unused and tasks_infos:
                task_in_final_state = True
                for task in tasks_infos:
                    if task["ExternalStatus"] not in self.jobs_final_status:
                        task_in_final_state = False
                        break
                flush_trans = task_in_final_state
                message: str = (
                    "Nb of files with Status 'Unused' "
                    f"({count_unused}) > GroupSize ({group_size})"
                    "and all jobs are in final states.\n"
                    f"The Transformation {trans_id} has been Flushed"
                )
        return flush_trans, message

    def get_count_size(self, trans_id: int) -> int:
        unused_trans_files = self.get_transformation_files(
            {"TransformationID": trans_id, "Status": "Unused"}
        )
        if not unused_trans_files["OK"]:
            gLogger.error(f"[{trans_id}] {unused_trans_files}")
            return 0
        return len(unused_trans_files["Value"])

    def parse_transformation_jobs_attributes(
        self, trans_id: int, jobs_attributes: list, create_report: bool = True
    ) -> Union[DOKReturnType[dict], Any, DErrorReturnType]:
        """Create a transformation report giving the number of jobs
        with a given application status by sites"""

        count_status_type: dict = {}
        count_minor_status: dict = {}
        count_status: dict = {}

        total_nb_jobs: int = len(jobs_attributes.keys())

        # Count jobs by status type:
        for job_id, job_info in jobs_attributes.items():
            job_attributes_tuple = tuple(
                job_info[attr] for attr in self.attributes_of_interest
            )

            status_counts = count_status_type.get(job_attributes_tuple, 0)
            count_status_type[job_attributes_tuple] = status_counts + 1

            count_minor_status[job_info["MinorStatus"]] = (
                count_minor_status.get(job_info["MinorStatus"], 0) + 1
            )
            count_status[job_info["Status"]] = (
                count_status.get(job_info["Status"], 0) + 1
            )
        if not count_status_type:
            return S_ERROR(f"[{trans_id}] Empty Transformation")

        if create_report:
            transformation_report: str = self.create_transformation_jobs_report(
                trans_id,
                count_status_type,
                count_minor_status,
                count_status,
                total_nb_jobs,
            )
            return S_OK(transformation_report)
        else:
            return S_OK()

    def create_threads_for_each_transformations(self, transformations) -> dict:
        """Create the future threads to check each transformation"""
        future_to_trans_id: dict = {}
        for trans_id, trans_info_dict in transformations["Value"].items():
            trans_type = trans_info_dict["Type"]
            trans_id = int(trans_id)
            try:
                future = self.thread_pool_executor.submit(
                    self.execute_transformation_check, trans_id, trans_info_dict
                )
                future_to_trans_id[future] = (trans_id, trans_type)
            except Exception.error as e:
                gLogger.info(e)
        return future_to_trans_id

    def before_executing(self) -> None:
        self.get_cs_options()

    def execute(self) -> Union[DErrorReturnType, DOKReturnType[None]]:
        """Execution in one agent's cycle"""
        self.before_executing()

        transformations = self.get_eligible_transformation(
            self.transformation_status, self.transformation_types
        )
        if not transformations["OK"]:
            gLogger.error("Failure to get transformations")
            return S_ERROR(transformations["Message"])

        future_to_trans_id = self.create_threads_for_each_transformations(
            transformations
        )

        # Get results:
        # TODO: Simplify the output parsing
        transformation_reports: dict[str, dict[str, str]] = defaultdict(dict)
        for future in concurrent.futures.as_completed(future_to_trans_id):
            trans_id, trans_type = future_to_trans_id[future]
            try:
                result = future.result()
                if result["OK"]:
                    trans_report = result["Value"]
                    if trans_report["Report"]:
                        transformation_reports[trans_type][trans_id] = trans_report[
                            "Message"
                        ]
                        gLogger.info(f"Report for transformation {trans_id} created")
                    else:
                        gLogger.info(trans_report["Message"])
                else:
                    gLogger.error(result)
            except Exception as exc:
                gLogger.error(f"{trans_id} generated an exception: {exc}")
                gLogger.debug(future.result())
            else:
                gLogger.info(f"Processed transformation {trans_id}")

        if transformation_reports:
            message: str = self.create_mail_message(
                transformation_reports, html=self.html
            )
            self.send_mail(
                subject=(
                    f"{self.subject} Report on "
                    f"{self.transformation_status} transformations"
                ),
                message=message,
                html=self.html,
            )
        return S_OK()

    def finalize(self) -> DOKReturnType[None]:
        """Final step before shutdown the agent"""
        try:
            self.thread_pool_executor.shutdown()
        except Exception.error as e:
            gLogger.error(f"Threads shutdown failed: {e}")
        else:
            gLogger.info("Finishing threads")
        return S_OK()
