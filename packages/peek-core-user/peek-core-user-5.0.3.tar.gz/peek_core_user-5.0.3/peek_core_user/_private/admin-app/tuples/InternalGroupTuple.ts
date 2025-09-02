import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class InternalGroupTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "InternalGroupTuple";

    //  Description of date1
    id: number;

    //  The unique name of the group
    groupName: string;

    //  The unique display name of the group
    groupTitle: string;

    constructor() {
        super(InternalGroupTuple.tupleName);
    }
}
