import { addTupleType, Tuple } from "@synerty/vortexjs";
import { graphDbTuplePrefix } from "../PluginNames";

@addTupleType
export class GraphDbTraceConfigRuleTuple extends Tuple {
    public static readonly tupleName =
        graphDbTuplePrefix + "GraphDbTraceConfigRuleTuple";

    //  The processing order of this rule
    order: number;

    //  What should this rule look for
    applyTo: number = 1;
    readonly APPLY_TO_VERTEX = 1;
    readonly APPLY_TO_EDGE = 2;
    readonly APPLY_TO_START_VERTEX = 3;

    //  What action should be taken when this rule is met
    action: number = 1;
    readonly ACTION_STOP_TRACE = 1;
    readonly ACTION_CONTINUE_TRACE = 2;
    readonly ACTION_ABORT_TRACE_WITH_MESSAGE = 3;

    //  Data to go with actions that require it
    actionData: string | null;

    //  The name of the property to apply the rule to
    propertyName: string;

    //  A comma separated list of property values to match
    propertyValue: string;

    // The type of value in the property value
    propertyValueType: number = 1;
    readonly PROP_VAL_TYPE_SIMPLE = 1;
    readonly PROP_VAL_TYPE_COMMA_LIST = 2;
    readonly PROP_VAL_TYPE_REGEX = 3;
    readonly PROP_VAL_TYPE_BITMASK_AND = 4;
    readonly PROP_VAL_TYPE_DIRECTION = 5;
    // Don't do any property comparisons
    readonly PROP_VAL_TYPE_NO_PROPERTY_CHECK = 6;

    //  Trace edge src/dst direction
    readonly PROP_VAL_TRACE_UPSTREAM = 2 ** 0;
    readonly PROP_VAL_TRACE_DOWNSTREAM = 2 ** 1;
    readonly PROP_VAL_TRACE_BOTH = 2 ** 2;

    //  The comment for this rule
    comment: string | null;

    //  Is this rule enabled
    isEnabled: boolean = true;

    // Prepeared property values, these are used for matching the this.
    preparedRegex: RegExp | null = null;
    preparedValueSet: Set<string> | null = null;

    constructor() {
        super(GraphDbTraceConfigRuleTuple.tupleName);
    }

    prepare() {
        if (this.propertyValueType == this.PROP_VAL_TYPE_COMMA_LIST) {
            let splitVals = this.propertyValue.split(",");
            this.preparedValueSet = new Set<string>();
            for (let val of splitVals) {
                this.preparedValueSet.add(val);
            }
        } else if (this.propertyValueType == this.PROP_VAL_TYPE_REGEX) {
            this.preparedRegex = new RegExp(this.propertyValue);
        }
    }
}
