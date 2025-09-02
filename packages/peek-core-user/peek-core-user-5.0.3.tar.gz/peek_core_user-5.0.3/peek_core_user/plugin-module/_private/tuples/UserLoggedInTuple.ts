import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";
import { UserListItemTuple } from "../../tuples/UserListItemTuple";

/** User Logged In Tuple
 *
 * This tuple is sent to the devices when a user logs in.
 *
 * If the device receives this tuple and the deviceToken doesn't match the current
 * device, then the user is logged off.
 *
 */
@addTupleType
export class UserLoggedInTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserLoggedInTuple";
    userDetails: UserListItemTuple;
    userGroups: string[];
    deviceToken: string;

    constructor() {
        super(UserLoggedInTuple.tupleName); // Matches server side
    }
}
