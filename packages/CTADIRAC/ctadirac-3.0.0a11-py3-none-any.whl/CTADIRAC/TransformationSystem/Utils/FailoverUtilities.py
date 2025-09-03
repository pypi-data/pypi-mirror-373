import time
from typing import Any, Union
from rich.console import Console
from rich.table import Table

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.ReturnValues import DOKReturnType, DErrorReturnType
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
from DIRAC.TransformationSystem.Client.Transformation import (
    Transformation,
)
from DIRAC.TransformationSystem.Client.TransformationClient import (
    TransformationClient,
)
from DIRAC.TransformationSystem.Agent.TransformationAgentsUtilities import (
    TransformationAgentsUtilities,
)
from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.WorkloadManagementSystem.Client import JobStatus
from CTADIRAC.Core.Utilities.return_values import DReportReturnType, s_report


class FailoverUtilities(TransformationAgentsUtilities):
    """
    Some useful methods used by TransformationFailoverAgent
    """

    def __init__(self, agent_name) -> None:
        TransformationAgentsUtilities.__init__(self)
        self.notif_client = NotificationClient()
        self.trans_client = TransformationClient()
        self.prod_client = ProductionClient()

        self.mail_from = None
        self.mail_to = None
        self.enabled = False

        self.attributes_of_interest: list[str] = [
            "Status",
            "MinorStatus",
            "ApplicationStatus",
            "Site",
        ]

    def get_eligible_transformation(
        self, status, type_list
    ) -> Union[Any, DOKReturnType]:
        """Select transformations of given status and type.
        using the TransformationClient"""
        cond_dict = {"Status": status, "Type": type_list}
        if not type_list:
            cond_dict = {"Status": status}
        res = self.trans_client.getTransformations(condDict=cond_dict)
        if not res["OK"]:
            return res
        transformations = {}
        for trans_info in res["Value"]:
            trans_id = trans_info["TransformationID"]
            transformations[str(trans_id)] = trans_info
        return S_OK(transformations)

    def get_transformation_tasks(self, trans_id: int) -> Union[Any, DOKReturnType]:
        """get transformations tasks
        using the TransformationClient"""
        res = self.trans_client.getTransformationTasks({"TransformationID": trans_id})
        if not res["OK"]:
            gLogger.error(res["Message"])

        if len(res["Value"]) == 0:
            gLogger.notice(f"[{trans_id}] No tasks selected")

        return res

    def get_transformation_files(self, cond_dict) -> Union[Any, list]:
        """Get the transformation files
        using the TransformationClient"""

        res = self.trans_client.getTransformationFiles(cond_dict)
        return res

    def is_transformation_processed(self, trans_id: int) -> bool:
        res_trans_stat = self.trans_client.getTransformationStats(trans_id)
        is_processed = False
        if res_trans_stat["OK"]:
            try:
                if (
                    res_trans_stat["Value"]["Processed"]
                    == res_trans_stat["Value"]["Total"]
                ):
                    is_processed = True
            except KeyError:
                gLogger.info(f"[{trans_id}] Transformation got no 'Processed' files.")
        else:
            gLogger.error(
                f"[{trans_id}] Can't getTransformationStats: {res_trans_stat}"
            )
        return is_processed

    def complete_transformation(
        self, trans_id: int
    ) -> Union[DReportReturnType, DErrorReturnType]:
        res_complete = self.trans_client.completeTransformation(trans_id)
        if res_complete["OK"]:
            return s_report(False, f"[{trans_id}] Transformation Completed.")
        else:
            return S_ERROR(
                f"[{trans_id}]: Can't complete transformation: {res_complete}"
            )

    def get_parent_transformation_id(self, trans_id: int) -> Union[int, None]:
        res = self.prod_client.get_parent_transformation(trans_id)
        if res["OK"]:
            if res["Value"]:
                try:
                    parent_id = res["Value"][0][0]
                    if isinstance(parent_id, int):
                        return parent_id
                except (TypeError, IndexError):
                    gLogger.error(
                        f"[{trans_id}] Error while getting parent transformation: {res}"
                    )
                    return None
            else:
                gLogger.info(f"[{trans_id}] Parent ID has empty value")
                return None
        else:
            gLogger.error(
                f"[{trans_id}] Error while getting parent transformation: {res}"
            )
            return None

    def get_parent_type(self, parent_id: int) -> Union[Any, None]:
        res = self.trans_client.getTransformations(
            condDict={"TransformationID": parent_id}
        )
        if res["OK"]:
            return res["Value"][0]["Type"]

    def set_task_status(self, trans_id: int, task_id: int, status: str):
        transformation = Transformation(transID=trans_id, transClient=self.trans_client)
        return transformation.setTaskStatus(taskID=task_id, status=status)

    def sorting_key(self, index1, index2):
        return lambda item: (item[index1], item[index2])

    def create_mail_message(
        self, transformation_reports: dict[str, dict[str, str]], html=False
    ):
        if html:
            return self.create_html_mail_message(transformation_reports)
        else:
            return self.create_text_mail_message(transformation_reports)

    def create_text_mail_message(
        self, transformation_reports: dict[str, dict[str, str]]
    ) -> str:
        """Sort the transformation by types
        and create the text string message"""
        message = ""
        for trans_type in transformation_reports:
            message += f"Report on {trans_type} transformations:"
            for report in transformation_reports[trans_type].values():
                message += report + "\n"
        return message

    def create_html_mail_message(
        self, transformation_reports: dict[str, dict[str, str]]
    ) -> str:
        """Sort the transformation by types
        and create the html string message"""

        message = ""
        for trans_type in transformation_reports:
            message += """<!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
            .r1 {font-style: italic}
            .r2 {font-weight: bold}
            .r3 {color: #008000; text-decoration-color: #008000; font-weight: bold}
            .r4 {color: #800000; text-decoration-color: #800000; font-weight: bold}
            body {
                color: #000000;
                background-color: #ffffff;
            }
            </style>
            </head>
            <body>
                <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code><span class="r1">"""
            message += f"Report on {trans_type} transformations:"
            message += """</span>
            </code></pre>
            </body>
            </html>"""
            for report in transformation_reports[trans_type].values():
                message += report + "\n"
        return message

    def init_rich_table(self, title: str, fields: list[str]) -> Table:
        """Init Rich Table:"""
        table = Table(title=title, style="bold")
        for f in fields:
            table.add_column(f)
        return table

    def generate_table(self, table: Table, html=False) -> str:
        """Export rich table"""
        console = Console(record=True, width=200)
        console.print(table)
        if html:
            html_output: str = console.export_html()
        else:
            html_output: str = console.export_text()
        return html_output

    def create_transformation_jobs_report(
        self,
        trans_id: int,
        count_status_type: dict,
        count_minor_status: dict,
        count_status: dict,
        total_nb_jobs: int,
    ) -> str:
        """Create the Rich transformation jobs report"""
        title: str = f"Transformation: {trans_id}"
        fields: list[str] = self.attributes_of_interest + ["Total"]
        table: Table = self.init_rich_table(title, fields)

        self.add_rows_in_table(
            count_minor_status,
            count_status,
            count_status_type,
            total_nb_jobs,
            table,
        )

        return self.generate_table(table, self.html)

    def add_rows_in_table(
        self,
        count_minor_status: dict,
        count_status: dict,
        count_status_type: dict,
        total_nb_jobs: int,
        table: Table,
    ) -> None:
        """Add rows in the table"""
        next_minor_status = ""
        next_status = ""
        # Sort the StatusType by Status then by MinorStatus:
        count_status_type_sorted: list = sorted(
            count_status_type,
            key=lambda x: (
                x[self.attributes_of_interest.index("Status")],
                x[self.attributes_of_interest.index("MinorStatus")],
            ),
        )
        N: int = len(count_status_type_sorted)
        n = 0
        for status_tuple in count_status_type_sorted:
            row = list(status_tuple) + [str(count_status_type[status_tuple])]
            table.add_row(*row)
            # Add Total
            if n + 1 <= N:
                if n + 1 < N:
                    next_status, next_minor_status = self.get_next_status(
                        n, count_status_type_sorted
                    )
                # Add minor_status total
                if self.should_add_minor_status_total(
                    n, next_minor_status, status_tuple, N
                ):
                    row = self.minor_status_total_row(
                        row, count_minor_status, status_tuple, count_status
                    )
                    table.add_row(*row, style="bold yellow")
                # Add status total
                if self.should_add_status_total(n, next_status, status_tuple, N):
                    row, style = self.status_total_row(
                        row, count_status, status_tuple, total_nb_jobs
                    )
                    table.add_row(*row, style=style)
            n += 1
        final_row: list[str] = self.final_row(total_nb_jobs)
        table.add_row(*final_row, style="bold")

    def get_next_status(
        self, n: int, count_status_type_sorted: list
    ) -> tuple[Any, Any]:
        """Get the next job status"""
        next_status: str = (
            count_status_type_sorted[n + 1][0]
            if n + 1 < len(count_status_type_sorted)
            else ""
        )
        next_minor_status: str = (
            count_status_type_sorted[n + 1][1]
            if n + 1 < len(count_status_type_sorted)
            else ""
        )
        return next_status, next_minor_status

    def should_add_minor_status_total(
        self, n: int, next_minor_status: str, status_tuple: tuple, tot: int
    ) -> Union[Any, bool]:
        """Condition to add the total of minor status"""
        return (next_minor_status != status_tuple[1] and next_minor_status != "") or (
            n + 1 == tot
        )

    def minor_status_total_row(
        self,
        row: list,
        count_minor_status: dict,
        status_tuple: tuple,
        count_status: dict,
    ) -> list[str]:
        """Create the minor status total row"""
        row[1] = f"Total: {row[1]}"
        row[-1] = (
            f"{count_minor_status[status_tuple[1]]} "
            f"({round(count_minor_status[status_tuple[1]]/count_status[status_tuple[0]]*100, 1)}%)"
        )
        row[-2] = "-"
        row[-3] = "-"
        return row

    def should_add_status_total(
        self, n: int, next_status: str, status_tuple: tuple, tot: int
    ) -> Union[Any, bool, str]:
        """Condition on creating the total status"""
        return (next_status != status_tuple[0] and next_status) or (n + 1 == tot)

    def status_total_row(
        self, row: list, count_status: dict, status_tuple: tuple, total_nb_jobs: int
    ) -> tuple[list, str]:
        """Create the status total row"""
        row[0] = f"Total: {row[0]}"
        row[-1] = (
            f"{count_status[status_tuple[0]]} "
            f"({round(count_status[status_tuple[0]]/total_nb_jobs*100, 1)}%)"
        )
        row[1] = "-"
        if any(status in row[0] for status in [JobStatus.FAILED, JobStatus.KILLED]):
            style = "bold red"
        elif any(status in row[0] for status in [JobStatus.DONE, JobStatus.COMPLETED]):
            style = "bold green"
        else:
            style = "bold orange3"
        return row, style

    def final_row(self, total_nb_jobs: int) -> list[str]:
        """Create the final row with total number of jobs"""
        final_row: list[str] = [
            "Total # tasks:",
            "-",
            "-",
            "-",
            str(total_nb_jobs),
        ]
        return final_row

    def create_reassigned_lfn_report(
        self, trans_id: int, reassigned_lfns: dict[int, list]
    ) -> str:
        """Create report on reassigned files"""
        n_lfns: int = sum(len(lfns) for lfns in reassigned_lfns.values())
        table: Table = self.init_rich_table(
            title=f"Reassigned {n_lfns} LFNs on transformation {trans_id}:",
            fields=["taskID", "LFN"],
        )
        for taskid, lfns_list in reassigned_lfns.items():
            for lfn in lfns_list:
                table.add_row(*[str(taskid), str(lfn)])
        return self.generate_table(table)

    def send_mail(self, subject: str, message: str, html=False) -> None:
        gLogger.info(f"Sending mail from {self.mail_from} to {self.mail_to}")
        res = self.notif_client.sendMail(
            self.mail_to, subject, message, self.mail_from, localAttempt=True, html=html
        )
        if res["OK"]:
            gLogger.info(f"Report succesfully sent to {self.mail_to}")
        else:
            gLogger.error(res)

    @classmethod
    def measure_time(cls, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            gLogger.info(f"{func.__name__} took {elapsed_time:.2f} seconds to execute")
            return result

        return wrapper
