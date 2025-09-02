import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class InternalUserTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "InternalUserTuple";

    //  Description of date1
    id: number;

    //  The unique user/login name of the user
    userName: string;

    //  The display name of the user
    userTitle: string;

    //  A unique id reference to an external system
    userUuid: string;

    //  The mobile number of the user
    mobile: string | null;

    //  The email address of the user
    email: string | null;

    //  The display name of the user
    groupIds: number[];

    // The user import source stream - arbitrary string
    importSource: string;

    // The user authentication target - value from class `UserAuthTargetEnum`
    authenticationTarget: string;

    constructor() {
        super(InternalUserTuple.tupleName);
    }
}
