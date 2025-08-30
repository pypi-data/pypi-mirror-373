import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

@addTupleType
export class UserLoginOtpResponseTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserLoginOtpResponseTuple";

    public static readonly STATUS_OTP_REQUEST_ACCEPTED = 0;
    public static readonly STATUS_OTP_REQUEST_REJECTED = 1;

    otpRequestStatus: number;
    userName: string;
    otpOptions: string[];
    otpValidFrom: Date;
    otpValidTo: Date;

    constructor() {
        super(UserLoginOtpResponseTuple.tupleName); // Matches server side
    }
}
