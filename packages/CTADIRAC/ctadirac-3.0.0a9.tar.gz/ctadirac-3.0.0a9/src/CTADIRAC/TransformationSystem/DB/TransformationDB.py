from DIRAC.TransformationSystem.DB.TransformationDB import (
    TransformationDB as DIRACTransformationDB,
)


class TransformationDB(DIRACTransformationDB):
    """Add special features to TransformationDB"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get_tasks_by_file_status(self, trans_id, file_status, task_status=None):
        query = (
            "select TaskID from TransformationTasks "
            f"where TransformationID={trans_id} and TaskID in ("
            "select TaskID from TransformationFiles "
            f"where TransformationID={trans_id} and Status='{file_status}' "
            f"group by TaskID)"
        )
        if task_status:
            formatted_statuses = ", ".join(f"'{status}'" for status in task_status)
            query += f" and ExternalStatus in ({formatted_statuses})"
        result_query = self._query(query + ";")
        return result_query
