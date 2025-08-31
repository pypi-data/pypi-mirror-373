""" Run Trace

This module contains the logic to perform python side traces.

NOTE: THIS FILE MUST BE KEPT IN SYNC WITH THE TYPESCRIPT VERSION AT :
* peek_plugin_graphdb/plugin-module/_private/tracer-service/PrivateRunTrace.ts


"""

import logging
from collections import namedtuple
from datetime import datetime
from functools import cmp_to_key
from typing import List, Dict, Optional

import pytz

from peek_plugin_graphdb._private.client.controller.FastGraphDb import (
    FastGraphDbModel,
)
from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedSegment import GraphDbLinkedSegment
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex
from peek_plugin_graphdb.tuples.GraphDbTraceConfigRuleTuple import (
    GraphDbTraceConfigRuleTuple,
)
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import (
    GraphDbTraceConfigTuple,
)
from peek_plugin_graphdb.tuples.GraphDbTraceResultEdgeTuple import (
    GraphDbTraceResultEdgeTuple,
)
from peek_plugin_graphdb.tuples.GraphDbTraceResultTuple import (
    GraphDbTraceResultTuple,
)
from peek_plugin_graphdb.tuples.GraphDbTraceResultVertexTuple import (
    GraphDbTraceResultVertexTuple,
)

logger = logging.getLogger(__name__)

_TraceEdgeParams = namedtuple(
    "_TraceEdgeParams", ["segment", "edge", "vertex", "isStartEdge"]
)


class _TraceAbortedWithMessageException(Exception):
    pass


class PrivateRunTrace:
    def __init__(
        self,
        result: GraphDbTraceResultTuple,
        traceConfig: GraphDbTraceConfigTuple,
        fastDb: FastGraphDbModel,
        startVertexOrEdgeKey: str,
        startSegmentKeys: List[str],
        maxVertexes: Optional[int] = None,
    ) -> None:
        self._traceConfigKey = traceConfig.key
        self._traceRules = list(
            filter(lambda r: r.isEnabled, traceConfig.rules)
        )
        self._traceRules.sort(key=cmp_to_key(self._ruleSortCmp))

        self._fastDb = fastDb
        self._startVertexOrEdgeKey = startVertexOrEdgeKey
        self._startSegmentKeys = startSegmentKeys
        self._maxVertexes = maxVertexes

        self._alreadyTracedSet = set()
        self._result = result

        self._traceEdgeQueue: List[_TraceEdgeParams] = []

    def run(self) -> None:
        # Sort and filter the rules
        startTime = datetime.now(pytz.utc)

        try:
            # Queue up the starting point and any segments it's in
            for segmentKey in self._startSegmentKeys:
                segment = self._fastDb.getSegment(segmentKey)
                if not segment:
                    raise Exception("Segment %s is missing", segmentKey)

                vertex = segment.vertexByKey.get(self._startVertexOrEdgeKey)
                if vertex:
                    self._traceVertex(segment, vertex, isStartVertex=True)
                    continue

                edge = segment.edgeByKey.get(self._startVertexOrEdgeKey)
                if edge:
                    self._traceEdgeQueue.append(
                        _TraceEdgeParams(segment, edge, None, isStartEdge=True)
                    )
                    continue

                raise Exception(
                    "Segment % could not find vertex/edge with key %s",
                    segment.key,
                    self._startVertexOrEdgeKey,
                )

            # Drain the trace queue
            while self._traceEdgeQueue:
                params = self._traceEdgeQueue.pop()
                self._traceEdge(
                    params.segment,
                    params.edge,
                    params.vertex,
                    isStartEdge=params.isStartEdge,
                )

        except _TraceAbortedWithMessageException:
            pass

        if len(self._result.vertexes) and not self._result.edges:
            self._result.traceAbortedMessage = (
                "The trace stopped on the start device."
            )

        if len(self._result.edges) and not self._result.vertexes:
            self._result.traceAbortedMessage = (
                "The trace stopped on the start conductor."
            )

        # Log the complete
        logger.debug(
            "Trace completed. Trace Config '%s',"
            " Start Vertex or Edge '%s'"
            " %s vertexes,"
            " %s edges,"
            " error:'%s',"
            " in %s",
            self._traceConfigKey,
            self._startVertexOrEdgeKey,
            len(self._result.vertexes),
            len(self._result.edges),
            self._result.traceAbortedMessage,
            (datetime.now(pytz.utc) - startTime),
        )

    # ---------------
    # Rule sort comparator

    def _ruleSortCmp(self, r1, r2):
        R = GraphDbTraceConfigRuleTuple

        # First, Order the rules that apply to the start vertex first
        if (
            r1.applyTo == R.APPLY_TO_START_VERTEX
            and r2.applyTo != R.APPLY_TO_START_VERTEX
        ):
            return -1

        if (
            r1.applyTo != R.APPLY_TO_START_VERTEX
            and r2.applyTo == R.APPLY_TO_START_VERTEX
        ):
            return 1

        # Then just compare by order
        if r1.order == r2.order:
            return 0
        return -1 if r1.order < r2.order else 1

    # ---------------
    # Traversing methods

    def _traceEdge(
        self,
        segment: GraphDbLinkedSegment,
        edge: GraphDbLinkedEdge,
        fromVertex: Optional[GraphDbLinkedVertex] = None,
        isStartEdge: bool = False,
    ):
        # Check and Mark if this edge has been traced
        if self._checkAlreadyTraced(None, edge.key):
            logger.debug(
                "Segment %s skipping already traced edge %s",
                segment.key,
                edge.key,
            )
            return

        if isStartEdge:
            self._addEdge(edge)

            # If the trace is starting on this edge, then we need to try
            # both directions.
            # SRC -> DST
            if self._matchTraceRules(segment, edge=edge, fromSrcVertex=True):
                self._traceVertex(segment, edge.dstVertex, fromEdgeKey=edge.key)

            # DST -> SRC
            if self._matchTraceRules(segment, edge=edge, fromSrcVertex=False):
                self._traceVertex(segment, edge.srcVertex, fromEdgeKey=edge.key)

            return

        # Apply the rules
        fromSrcVertex = fromVertex and edge.srcVertex.key == fromVertex.key
        if not self._matchTraceRules(
            segment, edge=edge, fromSrcVertex=fromSrcVertex
        ):
            return

        # Add the edge to the results
        self._addEdge(edge)

        # Assert that we have fromVertex
        assert fromVertex, "Trace has no fromVertex and is not startEdge"

        # Trace to the next vertex
        toVertex = edge.getOtherVertex(fromVertex.key)
        self._traceVertex(segment, toVertex, fromEdgeKey=edge.key)

    def _traceVertex(
        self,
        segment: GraphDbLinkedSegment,
        vertex: GraphDbLinkedVertex,
        isStartVertex=False,
        fromEdgeKey=None,
    ) -> None:
        if self._checkAlreadyTraced(vertex.key, None):
            logger.debug(
                f"Segment {segment.key}"
                f" skipping already traced of vortex {vertex.key}"
                f" from edge {fromEdgeKey}"
            )
            return

        self._addVertex(vertex)

        if not isStartVertex and not self._matchTraceRules(
            segment, vertex=vertex, fromEdgeKey=fromEdgeKey
        ):
            return

        for edge in vertex.edges:
            if edge.key == fromEdgeKey:
                continue
            self._queueEdge(
                _TraceEdgeParams(segment, edge, vertex, False), fromEdgeKey
            )

        for segmentKey in vertex.linksToSegmentKeys:
            logger.debug(
                f"Segment {segment.key} tracing to new segment {segmentKey}"
                f" via vertex {vertex.key} from edge {fromEdgeKey}"
            )
            self._traceEdgesInNextSegment(vertex.key, segmentKey)

    def _queueEdge(self, param: _TraceEdgeParams, fromEdgeKey):
        if self._checkAlreadyTraced(None, param.edge.key, checkOnly=True):
            logger.debug(
                f"Segment {param.segment.key}"
                f" skipping already traced edge {param.edge.key}"
                f" from vortex {param.vertex.key} from edge {fromEdgeKey}"
            )
            return

        logger.debug(
            f"Segment {param.segment.key}"
            f" queuing traced to edge {param.edge.key}"
            f" from vortex {param.vertex.key} from edge {fromEdgeKey}"
        )
        self._traceEdgeQueue.append(param)

    def _traceEdgesInNextSegment(self, vertexKey: str, segmentKey: str):
        logger.debug("Segment %s entered from vortex %s", segmentKey, vertexKey)

        segment = self._fastDb.getSegment(segmentKey)
        if not segment:
            raise Exception("Segment %s is missing", segmentKey)

        vertex = segment.vertexByKey.get(vertexKey)
        if not vertex:
            raise Exception(
                f"Segment {segmentKey} is missing vertex {vertexKey}"
            )

        for edge in vertex.edges:
            self._traceEdgeQueue.append(
                _TraceEdgeParams(segment, edge, vertex, False)
            )

    # ---------------
    # Add to result

    def _setTraceAborted(self, message: str):
        self._result.traceAbortedMessage = message
        raise _TraceAbortedWithMessageException()

    def _addEdge(self, edge: GraphDbLinkedEdge):
        self._result.edges.append(
            GraphDbTraceResultEdgeTuple(
                key=edge.key,
                srcVertexKey=edge.srcVertex.key,
                dstVertexKey=edge.dstVertex.key,
                props=edge.props,
            )
        )

    def _addVertex(self, vertex: GraphDbLinkedVertex):
        if (
            self._maxVertexes
            and len(self._result.vertexes) >= self._maxVertexes
        ):
            self._setTraceAborted(
                f"Trace exceeded maximum vertexes of {self._maxVertexes}"
            )

        self._result.vertexes.append(
            GraphDbTraceResultVertexTuple(key=vertex.key, props=vertex.props)
        )

    # ---------------
    # Already Traced State

    def _checkAlreadyTraced(
        self, vertexKey: Optional[str], edgeKey: Optional[str], checkOnly=False
    ) -> bool:
        traced = (vertexKey, edgeKey) in self._alreadyTracedSet
        if not traced and not checkOnly:
            self._alreadyTracedSet.add((vertexKey, edgeKey))

        return traced

    # ---------------
    # Match The Properties
    def _matchTraceRules(
        self,
        segment: GraphDbLinkedSegment,
        vertex: Optional[GraphDbLinkedVertex] = None,
        edge: Optional[GraphDbLinkedEdge] = None,
        fromSrcVertex: Optional[bool] = None,
        fromEdgeKey: Optional[str] = None,
    ) -> bool:
        isVertex = vertex is not None
        isEdge = edge is not None
        isStartVertex = isVertex and vertex.key == self._startVertexOrEdgeKey

        key = vertex.key if isVertex else edge.key
        desc = "vertex %s" % key if isVertex else "edge %s" % key
        if fromEdgeKey:
            desc += " from edge %s" % fromEdgeKey

        props = vertex.props if vertex else edge.props

        for rule in self._traceRules:
            # Accept the conditions in which we'll run this rule
            if rule.applyTo == rule.APPLY_TO_VERTEX and isVertex:
                pass

            elif rule.applyTo == rule.APPLY_TO_EDGE and isEdge:
                pass

            elif rule.applyTo == rule.APPLY_TO_START_VERTEX and isStartVertex:
                pass

            else:
                # Else, this isn't the right rule for this thing
                # move onto the next
                continue

            # If the rule doesn't match, then continue
            if not self._matchProps(props, rule, fromSrcVertex, edge):
                continue

            # The rule has matched.

            # Apply the action - Continue
            if rule.action == rule.ACTION_CONTINUE_TRACE:
                logger.debug(
                    f"Segment {segment.key}"
                    f" Applying rule Order {rule.order} Action"
                    f" Continue to {desc}"
                )
                return True

            # Apply the action - Abort
            if rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE:
                logger.debug(
                    f"Segment {segment.key}"
                    f" Applying rule Order {rule.order}"
                    f" Action ABORT WITH MESSAGE"
                    f" to {desc}"
                    f" message {rule.actionData}"
                )
                self._setTraceAborted(rule.actionData)
                return False

            # Apply the action - Stop
            if rule.action == rule.ACTION_STOP_TRACE:
                logger.debug(
                    f"Segment {segment.key}"
                    f" Applying rule Order {rule.order}"
                    f" Action STOP"
                    f" to {desc}"
                )
                return False

        # No rules have decided either way, continue tracing
        logger.debug(f"Segment {segment.key} No rules applied to {desc}")
        return True

    # ---------------
    # Match Vertex Rules
    def _matchProps(
        self,
        props: Dict,
        rule: GraphDbTraceConfigRuleTuple,
        fromSrcVertex: Optional[bool],
        edge: Optional[GraphDbLinkedEdge],
    ):
        propVal = str(props.get(rule.propertyName))

        if rule.propertyValueType == rule.PROP_VAL_TYPE_NO_PROPERTY_CHECK:
            return True

        if rule.propertyValueType == rule.PROP_VAL_TYPE_SIMPLE:
            return propVal == rule.propertyValue

        if rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST:
            return propVal in rule.preparedValueSet

        if rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX:
            return rule.preparedRegex.match(propVal)

        if rule.propertyValueType == rule.PROP_VAL_TYPE_BITMASK_AND:
            try:
                return bool(int(propVal) & int(rule.propertyValue))

            except ValueError:
                pass

            return False

        if rule.propertyValueType == rule.PROP_VAL_TYPE_DIRECTION:
            if not edge:
                self._setTraceAborted(
                    "Trace rule DIRECTION"
                    " should not have applyTo=Vertex,"
                    " it only applies to edges"
                )

            E = GraphDbLinkedEdge
            goingUpstream = (
                edge.srcDirection == E.DIR_SRC_IS_DOWNSTREAM
                if fromSrcVertex
                else edge.srcDirection == E.DIR_SRC_IS_UPSTREAM
            )

            goingDownstream = (
                edge.srcDirection == E.DIR_SRC_IS_UPSTREAM
                if fromSrcVertex
                else edge.srcDirection == E.DIR_SRC_IS_DOWNSTREAM
            )

            goingBoth = edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_BOTH

            bitVal = 0
            if goingDownstream:
                bitVal += rule.PROP_VAL_TRACE_DOWNSTREAM
            if goingUpstream:
                bitVal += rule.PROP_VAL_TRACE_UPSTREAM
            if goingBoth:
                bitVal += rule.PROP_VAL_TRACE_BOTH

            try:
                return bool(bitVal & int(rule.propertyValue))

            except ValueError:
                pass

            return False

        raise NotImplementedError(
            f"rule.propertyValueType  = {rule.propertyValueType}"
        )
