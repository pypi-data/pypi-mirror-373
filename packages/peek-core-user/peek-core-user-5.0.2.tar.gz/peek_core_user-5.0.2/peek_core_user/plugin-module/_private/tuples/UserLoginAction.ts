import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private";

@addTupleType
export class UserLoginAction extends TupleActionABC {
    public static readonly tupleName = userTuplePrefix + "UserLoginAction";

    userName: string | null = null;
    password: string = "";
    deviceToken: string | null = null;
    vehicleId: string = "";
    isFieldService: boolean | null = null;
    isOfficeService: boolean | null = null;

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logon
    acceptedWarningKeys: string[] = [];

    constructor() {
        super(UserLoginAction.tupleName); // Matches server side
    }
}
