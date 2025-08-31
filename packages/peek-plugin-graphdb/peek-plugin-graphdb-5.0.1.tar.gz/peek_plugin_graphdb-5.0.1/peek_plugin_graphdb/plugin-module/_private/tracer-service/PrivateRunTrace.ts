/** Run Trace
 
 This module contains the logic to perform typescript side traces.
 
 NOTE: THIS FILE MUST BE KEPT IN SYNC WITH THE PYTHON VERSION AT :
 * peek_plugin_graphdb/_private/client/controller/RunTrace.py
 
 
 */
import {
    PrivateSegmentLoaderService,
    SegmentResultI,
} from "../segment-loader/PrivateSegmentLoaderService";
import { GraphDbLinkedVertex } from "../../GraphDbLinkedVertex";
import { GraphDbLinkedEdge } from "../../GraphDbLinkedEdge";
import { GraphDbTraceConfigTuple } from "../tuples/GraphDbTraceConfigTuple";
import { GraphDbTraceResultTuple } from "../../GraphDbTraceResultTuple";
import { GraphDbLinkedSegment } from "../../GraphDbLinkedSegment";
import { GraphDbTraceResultVertexTuple } from "../../GraphDbTraceResultVertexTuple";
import { GraphDbTraceResultEdgeTuple } from "../../GraphDbTraceResultEdgeTuple";
import { GraphDbTraceConfigRuleTuple } from "../tuples/GraphDbTraceConfigRuleTuple";
import * as moment from "moment";

// ----------------------------------------------------------------------------

export class _TraceAbortedWithMessageError extends Error {}

export interface _TraceEdgeParams {
    segment: GraphDbLinkedSegment;
    edge: GraphDbLinkedEdge;
    vertex: GraphDbLinkedVertex;
    isStartEdge: boolean | null;
}

export class PrivateRunTrace {
    private _alreadyTracedSet = new Set<string>();

    private _traceEdgeQueue: _TraceEdgeParams[] = [];

    private readonly _traceConfigKey: string;
    private readonly _traceRules: GraphDbTraceConfigRuleTuple[] = [];

    constructor(
        private _result: GraphDbTraceResultTuple,
        traceConfig: GraphDbTraceConfigTuple,
        private segmentLoader: PrivateSegmentLoaderService,
        private _startVertexOrEdgeKey: string,
        private _startSegmentKeys: string[],
        private _maxVertexes: null | number = null,
    ) {
        this._traceConfigKey = traceConfig.key;
        this._traceRules = traceConfig.rules.filter((r) => r.isEnabled);
        this._traceRules.sort(this._ruleSortCmp);
    }

    async run(): Promise<void> {
        const startTime = new Date();

        try {
            // Queue up the starting point and any segments it's in
            for (const segmentKey of this._startSegmentKeys) {
                const segment: GraphDbLinkedSegment = await this.segmentLoader //
                    .getSegment(this._result.modelSetKey, segmentKey);

                if (segment == null) {
                    throw new Error(`Could not find segment ${segmentKey} `);
                }

                const vertex = segment.vertexByKey[this._startVertexOrEdgeKey];
                if (vertex != null) {
                    await this._traceVertex(segment, vertex, {
                        isStartVertex: true,
                    });
                    continue;
                }

                const edge = segment.edgeByKey[this._startVertexOrEdgeKey];
                if (edge != null) {
                    this._traceEdgeQueue.push({
                        segment: segment,
                        edge: edge,
                        vertex: null,
                        isStartEdge: true,
                    });
                    continue;
                }

                // noinspection ExceptionCaughtLocallyJS
                throw new Error(
                    "Could not find vertex or edge" +
                        ` ${this._startVertexOrEdgeKey} of segment ${segmentKey} `,
                );
            }

            while (this._traceEdgeQueue.length !== 0) {
                const params = this._traceEdgeQueue.pop();
                await this._traceEdge(
                    params.segment,
                    params.edge,
                    params.vertex,
                );
            }
        } catch (e) {
            if (!(e instanceof _TraceAbortedWithMessageError)) throw e;
        }

        if (
            this._result.vertexes.length !== 0 &&
            this._result.edges.length === 0
        ) {
            this._result.traceAbortedMessage =
                "The trace stopped on the start device.";
        }

        if (
            this._result.vertexes.length === 0 &&
            this._result.edges.length !== 0
        ) {
            this._result.traceAbortedMessage =
                "The trace stopped on the start conductor.";
        }

        const duration = (new Date().getTime() - startTime.getTime()) / 1000;

        // Log the complete
        console.log(
            `Trace completed. Trace Config '${this._traceConfigKey}',` +
                ` Start Vertex or Edge '${this._startVertexOrEdgeKey}',` +
                ` ${this._result.vertexes.length} vertexes,` +
                ` ${this._result.edges.length} edges,` +
                ` error:'${this._result.traceAbortedMessage}',` +
                ` in ${duration}s`,
        );
    }

    // ---------------
    // Rule sort comparator

    private _ruleSortCmp(
        r1: GraphDbTraceConfigRuleTuple,
        r2: GraphDbTraceConfigRuleTuple,
    ): number {
        const R = new GraphDbTraceConfigRuleTuple();

        // First, Order the rules that apply to the start vertex first
        if (
            r1.applyTo == R.APPLY_TO_START_VERTEX &&
            r2.applyTo != R.APPLY_TO_START_VERTEX
        ) {
            return -1;
        }

        if (
            r1.applyTo != R.APPLY_TO_START_VERTEX &&
            r2.applyTo == R.APPLY_TO_START_VERTEX
        ) {
            return 1;
        }

        // Then just compare by order
        return r1.order == r2.order ? 0 : r1.order < r2.order ? -1 : 1;
    }

    // ---------------
    // Traversing methods

    private async _traceEdge(
        segment: GraphDbLinkedSegment,
        edge: GraphDbLinkedEdge,
        fromVertex: GraphDbLinkedVertex | null,
        isStartEdge: boolean = false,
    ): Promise<void> {
        if (this._checkAlreadyTraced({ edgeKey: edge.key })) {
            console.log(
                `Segment ${segment.key}` +
                    ` skipping already traced edge ${edge.key}`,
            );
            return;
        }

        if (isStartEdge === true) {
            this._addEdge(edge);

            // If the trace is starting on this edge, then we need to try
            // both directions.
            // SRC -> DST
            if (
                this._matchTraceRules(segment, {
                    edge: edge,
                    fromSrcVertex: true,
                })
            )
                await this._traceVertex(segment, edge.dstVertex, {
                    fromEdgeKey: edge.key,
                });

            // DST -> SRC
            if (
                this._matchTraceRules(segment, {
                    edge: edge,
                    fromSrcVertex: false,
                })
            )
                await this._traceVertex(segment, edge.srcVertex, {
                    fromEdgeKey: edge.key,
                });

            return;
        }

        const fromSrcVertex =
            fromVertex != null && edge.srcVertex.key == fromVertex.key;
        if (
            !this._matchTraceRules(segment, {
                edge: edge,
                fromSrcVertex: fromSrcVertex,
            })
        )
            return;

        this._addEdge(edge);

        // Assert that we have fromVertex
        console.assert(
            fromVertex != null,
            "Trace has no fromVertex and is not startEdge",
        );

        const toVertex = edge.getOtherVertex(fromVertex?.key);
        await this._traceVertex(segment, toVertex, { fromEdgeKey: edge.key });
    }

    private async _traceVertex(
        segment: GraphDbLinkedSegment,
        vertex: GraphDbLinkedVertex,
        params: {
            isStartVertex?: boolean;
            fromEdgeKey?: string;
        },
    ): Promise<void> {
        const isStartVertex = params.isStartVertex === true;
        const fromEdgeKey = params.fromEdgeKey;

        if (this._checkAlreadyTraced({ vertexKey: vertex.key })) {
            console.log(
                `Segment ${segment.key}` +
                    ` skipping already traced of vortex ${vertex.key}` +
                    ` from edge ${fromEdgeKey}`,
            );
            return;
        }

        this._addVertex(vertex);

        if (
            !isStartVertex &&
            !this._matchTraceRules(segment, {
                vertex: vertex,
                fromEdgeKey: fromEdgeKey,
            })
        )
            return;

        for (const edge of vertex.edges) {
            if (edge.key === fromEdgeKey) continue;
            this._queueEdge(
                {
                    segment: segment,
                    edge: edge,
                    vertex: vertex,
                    isStartEdge: false,
                },
                fromEdgeKey,
            );
        }

        for (const segmentKey of vertex.linksToSegmentKeys || []) {
            console.log(
                `Segment ${segment.key} tracing to new segment ${segmentKey}` +
                    ` via vertex ${vertex.key} from edge ${fromEdgeKey}`,
            );
            await this._traceEdgesInNextSegment(vertex.key, segmentKey);
        }
    }

    private _queueEdge(param: _TraceEdgeParams, fromEdgeKey): void {
        if (
            this._checkAlreadyTraced({
                edgeKey: param.edge.key,
                checkOnly: true,
            })
        ) {
            console.log(
                `Segment ${param.segment.key}` +
                    ` skipping already traced edge ${param.edge.key}` +
                    ` from vortex ${param.vertex.key} from edge ${fromEdgeKey}`,
            );
            return;
        }

        console.log(
            `Segment ${param.segment.key}` +
                ` queuing traced to edge ${param.edge.key}` +
                ` from vortex ${param.vertex.key} from edge ${fromEdgeKey}`,
        );
        this._traceEdgeQueue.push(param);
    }

    private async _traceEdgesInNextSegment(
        vertexKey: string,
        segmentKey: string,
    ): Promise<void> {
        const segment: GraphDbLinkedSegment = await this.segmentLoader //
            .getSegment(this._result.modelSetKey, segmentKey);

        if (segment == null) {
            throw new Error(`Segment ${segmentKey} is missing`);
        }

        const vertex = segment.vertexByKey[vertexKey];
        if (vertex == null) {
            throw new Error(
                `Segment ${segmentKey} is missing vertex ${vertexKey}`,
            );
        }

        for (const edge of vertex.edges) {
            this._traceEdgeQueue.push({
                segment: segment,
                edge: edge,
                vertex: vertex,
                isStartEdge: false,
            });
        }
    }

    // ---------------
    // Add to _result

    private _setTraceAborted(message: string) {
        this._result.traceAbortedMessage = message;
        throw new _TraceAbortedWithMessageError();
    }

    private _addEdge(edge: GraphDbLinkedEdge) {
        let newItem = new GraphDbTraceResultEdgeTuple();
        newItem.key = edge.key;
        newItem.srcVertexKey = edge.srcVertex.key;
        newItem.dstVertexKey = edge.dstVertex.key;
        newItem.props = edge.props;
        this._result.edges.push(newItem);
    }

    private _addVertex(vertex: GraphDbLinkedVertex) {
        if (
            this._maxVertexes &&
            this._result.vertexes.length >= this._maxVertexes
        ) {
            this._setTraceAborted(
                `Trace exceeded maximum vertexes of ${this._maxVertexes}`,
            );
        }

        let newItem = new GraphDbTraceResultVertexTuple();
        newItem.key = vertex.key;
        newItem.props = vertex.props;
        this._result.vertexes.push(newItem);
    }

    // ---------------
    // Already Traced State

    private _checkAlreadyTraced(params: {
        vertexKey?: string;
        edgeKey?: string;
        checkOnly?: boolean;
    }): boolean {
        const checkOnly = params.checkOnly === true;
        const val = `${params.vertexKey}, ${params.edgeKey}`;

        const traced = this._alreadyTracedSet.has(val);

        if (!traced && !checkOnly) {
            this._alreadyTracedSet.add(val);
        }

        return traced;
    }

    // ---------------
    // Match Vertex Rules
    private _matchTraceRules(
        segment: GraphDbLinkedSegment,
        params: {
            vertex?: GraphDbLinkedVertex;
            edge?: GraphDbLinkedEdge;
            fromSrcVertex?: boolean;
            fromEdgeKey?: string;
        },
    ): boolean {
        const vertex = params.vertex;
        const edge = params.edge;
        const fromSrcVertex = params.fromSrcVertex;
        const fromEdgeKey = params.fromEdgeKey;

        const isVertex = vertex != null;
        const isEdge = edge != null;
        const isStartVertex =
            isVertex && vertex.key == this._startVertexOrEdgeKey;

        const key = isVertex ? vertex.key : edge.key;
        let desc = isVertex ? "vertex " + key : "edge " + key;
        if (fromEdgeKey) {
            desc += " from edge " + fromEdgeKey;
        }

        const props = vertex != null ? vertex.props : edge.props;

        for (const rule of this._traceRules) {
            // Accept the conditions in which we'll run this rule
            if (rule.applyTo == rule.APPLY_TO_VERTEX && isVertex) {
                // pass
            } else if (rule.applyTo == rule.APPLY_TO_EDGE && isEdge) {
                // pass
            } else if (
                rule.applyTo == rule.APPLY_TO_START_VERTEX &&
                isStartVertex
            ) {
                // pass
            } else {
                // Else, this isn't the right rule for this thing,
                // move onto the next
                continue;
            }

            // If the rule doesn't match, then continue
            if (!this._matchProps(props, rule, fromSrcVertex, edge)) {
                continue;
            }

            // The rule has matched.

            // Apply the action - Continue
            if (rule.action == rule.ACTION_CONTINUE_TRACE) {
                console.log(
                    `Segment ${segment.key}` +
                        ` Applying rule Order ${rule.order} Action` +
                        ` Continue to ${desc}`,
                );
                return true;
            }

            // Apply the action - Abort
            if (rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE) {
                console.log(
                    `Segment ${segment.key}` +
                        ` Applying rule Order ${rule.order}` +
                        ` Action ABORT WITH MESSAGE` +
                        ` to ${desc}` +
                        ` message ${rule.actionData}`,
                );
                this._setTraceAborted(rule.actionData);
                return false;
            }

            // Apply the action - Stop
            if (rule.action == rule.ACTION_STOP_TRACE) {
                console.log(
                    `Segment ${segment.key}` +
                        ` Applying rule Order ${rule.order}` +
                        ` Action STOP` +
                        ` to ${desc}`,
                );
                return false;
            }
        }

        // No rules have decided either way, continue tracing
        console.log(`Segment ${segment.key} No rules applied to ${desc}`);
        return true;
    }

    // ---------------
    // Match The Properties
    private _matchProps(
        props: {},
        rule: GraphDbTraceConfigRuleTuple,
        fromSrcVertex?: boolean,
        edge?: GraphDbLinkedEdge,
    ) {
        const propVal = (props[rule.propertyName] || "").toString();

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_NO_PROPERTY_CHECK) {
            return true;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_SIMPLE) {
            return propVal == rule.propertyValue;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST) {
            return rule.preparedValueSet.has(propVal);
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX) {
            return rule.preparedRegex.exec(propVal);
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_BITMASK_AND) {
            try {
                return !!(parseInt(propVal) & parseInt(rule.propertyValue));
            } catch {}
            return false;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_DIRECTION) {
            if (edge == null) {
                this._setTraceAborted(
                    "Trace rule DIRECTION" +
                        " should not have applyTo=Vertex," +
                        " it only applies to edges",
                );
            }
            const goingUpstream = fromSrcVertex
                ? edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_DOWNSTREAM
                : edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_UPSTREAM;

            const goingDownstream = fromSrcVertex
                ? edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_UPSTREAM
                : edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_DOWNSTREAM;

            const goingBoth =
                edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_BOTH;

            let bitVal = 0;
            if (goingDownstream) {
                bitVal += rule.PROP_VAL_TRACE_DOWNSTREAM;
            }
            if (goingUpstream) {
                bitVal += rule.PROP_VAL_TRACE_UPSTREAM;
            }
            if (goingBoth) {
                bitVal += rule.PROP_VAL_TRACE_BOTH;
            }

            try {
                return Boolean(bitVal & parseInt(rule.propertyValue));
            } catch {}
            return false;
        }

        throw new Error(`rule.propertyValueType = ${rule.propertyValueType}`);
    }
}
