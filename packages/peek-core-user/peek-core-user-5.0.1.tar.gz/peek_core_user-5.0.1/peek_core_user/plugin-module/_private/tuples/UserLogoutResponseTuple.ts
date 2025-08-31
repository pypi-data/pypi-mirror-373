import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class UserLogoutResponseTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserLogoutResponseTuple";
    userName: string;
    deviceToken: string;
    deviceDescription: string;
    succeeded: boolean = true;
    // continues.
    acceptedWarningKeys: string[] = [];

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logoff
    // value = the description of the warning for the user
    warnings: {} = {};

    // A dict of warnings from a failed logoff action.
    // key = a unique key for this warning
    errors: string[] = [];

    constructor() {
        super(UserLogoutResponseTuple.tupleName); // Matches server side
    }
}
