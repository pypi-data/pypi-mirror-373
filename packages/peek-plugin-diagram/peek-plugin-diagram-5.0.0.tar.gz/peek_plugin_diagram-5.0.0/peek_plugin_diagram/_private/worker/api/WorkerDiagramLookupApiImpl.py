from typing import List

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_diagram.tuples.lookup_tuples.ShapeLayerTuple import (
    ShapeLayerTuple,
)


class WorkerDiagramLookupApiImpl:
    def __init__(self):
        pass

    @classmethod
    def getColors(cls) -> List[DispColorTable]:
        ormSession = TaskDbConn.getDbSession()
        try:
            rows = ormSession.query(DispColorTable).all()

            tuples = []

            for row in rows:
                tuple_ = row.toTuple()
                tuples.append(tuple_)

            return tuples

        finally:
            ormSession.close()

    @classmethod
    def getLineStyles(cls) -> List[DispLineStyleTable]:
        ormSession = TaskDbConn.getDbSession()
        try:
            rows = ormSession.query(DispLineStyleTable).all()

            tuples = []
            for row in rows:
                tuple_ = row.toTuple()
                tuples.append(tuple_)

            return tuples

        finally:
            ormSession.close()

    @classmethod
    def getTextStyles(cls) -> List[DispTextStyleTable]:
        ormSession = TaskDbConn.getDbSession()
        try:
            rows = ormSession.query(DispTextStyleTable).all()

            tuples = []
            for row in rows:
                tuple_ = row.toTuple()
                tuples.append(tuple_)

            return tuples

        finally:
            ormSession.close()

    @classmethod
    def getLayers(cls) -> List[ShapeLayerTuple]:
        ormSession = TaskDbConn.getDbSession()
        try:
            rows = (
                ormSession.query(DispLayerTable)
                .order_by(DispLayerTable.order, DispLayerTable.id)
                .all()
            )

            tuples = []
            tuplesById = {}
            for row in rows:
                tuple_ = row.toTuple()
                tuples.append(tuple_)
                tuplesById[tuple_.key] = tuple_

            # Link parent and child relationships
            for tuple_ in tuples:
                if tuple_.parentKey:
                    parentTuple = tuplesById.get(tuple_.parentKey)
                    if parentTuple:
                        tuple_.parentLayer = parentTuple
                        parentTuple.childLayers.append(tuple_)

            return tuples

        finally:
            ormSession.close()

    @classmethod
    def getLevels(cls) -> List[DispLevelTable]:
        ormSession = TaskDbConn.getDbSession()
        try:
            rows = (
                ormSession.query(DispLevelTable)
                .order_by(DispLevelTable.order, DispLevelTable.id)
                .all()
            )

            tuples = []
            for row in rows:
                tuple_ = row.toTuple()
                tuples.append(tuple_)

            return tuples

        finally:
            ormSession.close()
