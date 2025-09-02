import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

@addTupleType
export class UserLogoutAction extends TupleActionABC {
    public static readonly tupleName = userTuplePrefix + "UserLogoutAction";
    userName: string;
    deviceToken: string | null = null;
    isFieldService: boolean = null;
    isOfficeService: boolean = null;

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logoff
    acceptedWarningKeys: string[] = [];

    constructor() {
        super(UserLogoutAction.tupleName); // Matches server side
    }
}
