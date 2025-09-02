import { Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../_private/PluginNames";

export class GroupDetailTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "GroupDetailTuple";
    // ID
    id: number;
    //  The name of the group, EG C917
    groupName: string;
    //  The title of the group, EG 'Chief Wiggum'
    groupTitle: string;

    constructor() {
        super(GroupDetailTuple.tupleName); // Matches server side
    }
}
