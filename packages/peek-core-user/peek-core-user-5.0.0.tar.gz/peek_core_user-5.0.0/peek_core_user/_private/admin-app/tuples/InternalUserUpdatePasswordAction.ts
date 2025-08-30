import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class InternalUserUpdatePasswordAction extends TupleActionABC {
    public static readonly tupleName =
        userTuplePrefix + "InternalUserUpdatePasswordAction";

    //  Description of date1
    userId: number;

    //  The unique user/login name of the user
    newPassword: string;

    constructor() {
        super(InternalUserUpdatePasswordAction.tupleName);
    }
}
