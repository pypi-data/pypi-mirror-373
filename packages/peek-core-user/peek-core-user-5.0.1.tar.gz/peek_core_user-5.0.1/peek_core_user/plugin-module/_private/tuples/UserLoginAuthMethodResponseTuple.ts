import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

@addTupleType
export class UserLoginAuthMethodResponseTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserLoginAuthMethodResponseTuple";

    public static readonly AUTH_METHOD_NONE = -1;
    public static readonly AUTH_METHOD_ONE_TIME_PASSCODE = 0;
    public static readonly AUTH_METHOD_PASSWORD = 1;

    userName: string;
    authMethod: number = UserLoginAuthMethodResponseTuple.AUTH_METHOD_NONE;

    constructor() {
        super(UserLoginAuthMethodResponseTuple.tupleName);
    }
}
