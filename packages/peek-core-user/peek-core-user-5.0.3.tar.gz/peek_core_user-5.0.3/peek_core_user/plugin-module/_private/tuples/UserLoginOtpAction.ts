import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

@addTupleType
export class UserLoginOtpAction extends TupleActionABC {
    public static readonly tupleName = userTuplePrefix + "UserLoginOtpAction";

    userName: string;

    constructor() {
        super(UserLoginOtpAction.tupleName); // Matches server side
    }
}
