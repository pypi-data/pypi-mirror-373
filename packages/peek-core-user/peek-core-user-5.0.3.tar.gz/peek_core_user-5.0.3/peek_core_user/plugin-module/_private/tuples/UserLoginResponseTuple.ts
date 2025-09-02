import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";
import { UserDetailTuple } from "../../tuples/UserDetailTuple";

@addTupleType
export class UserLoginResponseTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserLoginResponseTuple";
    userName: string;
    userToken: string;
    deviceToken: string;
    deviceDescription: string;
    vehicleId: string = "";
    userDetail: UserDetailTuple;
    succeeded: boolean = true;
    // continues.
    acceptedWarningKeys: string[] = [];

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logon
    // value = the description of the warning for the user
    warnings: {} = {};

    // A dict of warnings from a failed logon action.
    // key = a unique key for this warning
    errors: string[] = [];

    constructor() {
        super(UserLoginResponseTuple.tupleName); // Matches server side
    }
}
