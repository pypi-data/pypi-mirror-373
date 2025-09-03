from DIRAC.ProductionSystem.DB.ProductionDB import ProductionDB as DIRACProductionDB


class ProductionDB(DIRACProductionDB):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get_parent_transformation(self, trans_id, connection=False):
        connection = self.__getConnection(connection)
        req = f"SELECT ParentTransformationID FROM ProductionTransformationLinks WHERE TransformationID={trans_id}"
        res = self._query(req, conn=connection)
        return res
