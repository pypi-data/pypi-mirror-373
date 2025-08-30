import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

@addTupleType
export class UserLoginAuthMethodAction extends TupleActionABC {
    public static readonly tupleName =
        userTuplePrefix + "UserLoginAuthMethodAction";

    public static readonly AUTH_FOR_ADMIN = 1;
    public static readonly AUTH_FOR_OFFICE = 2;
    public static readonly AUTH_FOR_FIELD = 3;

    userName: string;
    authForService: number;

    constructor() {
        super(UserLoginAuthMethodAction.tupleName);
    }
}
