from DIRAC.TransformationSystem.Service.TransformationManagerHandler import (
    TransformationManagerHandler as TManagerBase,
)


class TransformationManagerHandlerMixin:
    types_get_tasks_by_file_status = [int, str]

    @classmethod
    def export_get_tasks_by_file_status(cls, trans_id, file_status, task_status=None):
        return cls.transformationDB.get_tasks_by_file_status(
            trans_id, file_status, task_status
        )


class TransformationManagerHandler(TransformationManagerHandlerMixin, TManagerBase):
    pass
