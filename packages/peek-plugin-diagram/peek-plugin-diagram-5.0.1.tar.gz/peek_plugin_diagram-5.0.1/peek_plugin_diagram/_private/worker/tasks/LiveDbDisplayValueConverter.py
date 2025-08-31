import logging
from typing import Dict

from sqlalchemy import select

from peek_plugin_diagram._private.storage.Lookups import DispColorTable
from peek_plugin_diagram._private.storage.Lookups import DispLayerTable
from peek_plugin_diagram._private.storage.Lookups import DispLevelTable
from peek_plugin_diagram._private.storage.Lookups import DispLineStyleTable
from peek_plugin_diagram._private.storage.Lookups import DispTextStyleTable
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import (
    ImportLiveDbItemTuple,
)

logger = logging.getLogger(__name__)

textTable = DispTextStyleTable.__table__
lineTable = DispLineStyleTable.__table__
colorTable = DispColorTable.__table__
levelTable = DispLevelTable.__table__
layerTable = DispLayerTable.__table__


class LiveDbDisplayValueConverter:
    _colorIdByImportHash = None
    _lineStyleIdByImportHash = None

    @staticmethod
    def create(ormSession, modelSetId: int) -> "LiveDbDisplayValueConverter":
        self = LiveDbDisplayValueConverter()

        # self._textStyleIdByImportHash = self._loadLookupByModelSet(
        #     ormSessionCreator, modelSetId, textTable
        # )

        self._lineStyleIdByImportHash = self._loadLookupByModelSet(
            ormSession, modelSetId, lineTable
        )

        self._colorIdByImportHash = self._loadLookupByModelSet(
            ormSession, modelSetId, colorTable
        )

        # self._layerByImportHash = self._loadLookupByModelSet(
        #     ormSessionCreator, modelSetId, layerTable
        # )
        #
        return self

    def translate(self, dataType, rawValue):
        return self._liveDbTranslators[dataType](self, rawValue)

    @staticmethod
    def _loadLookupByModelSet(
        ormSession, modelSetId: int, table
    ) -> Dict[str, int]:
        resultSet = ormSession.execute(
            select(table.c.importHash, table.c.id).where(
                table.c.modelSetId == modelSetId
            )
        )

        return dict(resultSet.fetchall())

    def _liveDbValueTranslateColorId(self, value):
        return self._colorIdByImportHash.get(value)

    def _liveDbValueTranslateLineStyleId(self, value):
        return self._lineStyleIdByImportHash.get(value)

    def _liveDbValueTranslateLineWidth(self, value):
        return value

    def _liveDbValueTranslateText(self, value):
        return "" if value is None else value

    def _liveDbValueTranslateNumber(self, value):
        return value

    def _liveDbValueTranslateGroupId(self, value):
        raise NotImplementedError()

    _liveDbTranslators = {
        ImportLiveDbItemTuple.DATA_TYPE_COLOR: _liveDbValueTranslateColorId,
        ImportLiveDbItemTuple.DATA_TYPE_LINE_STYLE: _liveDbValueTranslateLineStyleId,
        ImportLiveDbItemTuple.DATA_TYPE_LINE_WIDTH: _liveDbValueTranslateLineWidth,
        ImportLiveDbItemTuple.DATA_TYPE_STRING_VALUE: _liveDbValueTranslateText,
        ImportLiveDbItemTuple.DATA_TYPE_NUMBER_VALUE: _liveDbValueTranslateNumber,
        ImportLiveDbItemTuple.DATA_TYPE_GROUP_PTR: _liveDbValueTranslateGroupId,
    }
