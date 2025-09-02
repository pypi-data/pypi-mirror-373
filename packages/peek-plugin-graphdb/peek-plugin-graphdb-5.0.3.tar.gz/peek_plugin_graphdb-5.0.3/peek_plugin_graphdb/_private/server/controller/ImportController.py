import logging
from typing import List

from twisted.internet.defer import inlineCallbacks, Deferred

from peek_plugin_graphdb._private.server.client_handlers.TraceConfigUpdateHandler import (
    TraceConfigUpdateHandler,
)
from peek_plugin_graphdb._private.worker.tasks import SegmentIndexImporterTask
from peek_plugin_graphdb._private.worker.tasks import TraceConfigImporterTask

logger = logging.getLogger(__name__)


class ImportController:
    def __init__(self, traceConfigUpdateHandler: TraceConfigUpdateHandler):
        self._traceConfigUpdateHandler = traceConfigUpdateHandler

    def shutdown(self):
        pass

    @inlineCallbacks
    def createOrUpdateSegments(self, graphSegmentEncodedPayload: bytes):
        yield SegmentIndexImporterTask.createOrUpdateSegments.delay(
            graphSegmentEncodedPayload
        )

    @inlineCallbacks
    def deleteSegment(self, modelSetKey: str, importGroupHashes: List[str]):
        yield SegmentIndexImporterTask.deleteSegment.delay(
            modelSetKey, importGroupHashes=importGroupHashes, segmentKeys=[]
        )

    @inlineCallbacks
    def deleteSegmentsBySegmentKeys(
        self, modelSetKey: str, segmentKeys: List[str]
    ):
        yield SegmentIndexImporterTask.deleteSegment.delay(
            modelSetKey, importGroupHashes=[], segmentKeys=segmentKeys
        )

    @inlineCallbacks
    def createOrUpdateTraceConfig(self, traceEncodedPayload: bytes) -> Deferred:
        insertedOrCreated = (
            yield TraceConfigImporterTask.createOrUpdateTraceConfigs.delay(
                traceEncodedPayload
            )
        )

        for modelSetKey, traceConfigKeys in insertedOrCreated.items():
            self._traceConfigUpdateHandler.sendCreatedOrUpdatedUpdates(
                modelSetKey, traceConfigKeys
            )

    @inlineCallbacks
    def deleteTraceConfig(
        self, modelSetKey: str, traceConfigKeys: List[str]
    ) -> Deferred:
        yield TraceConfigImporterTask.deleteTraceConfig.delay(
            modelSetKey, traceConfigKeys
        )

        self._traceConfigUpdateHandler.sendDeleted(modelSetKey, traceConfigKeys)
