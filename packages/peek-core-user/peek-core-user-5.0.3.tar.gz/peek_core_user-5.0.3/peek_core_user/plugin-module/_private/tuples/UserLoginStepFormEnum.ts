import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private";

@addTupleType
export class UserLoginStepFormEnum extends Tuple {
    static readonly tupleName = userTuplePrefix + "UserLoginStepFormEnum";

    static readonly OFFICE_FORM = -1;

    static readonly FIELD_STEP_SELECT_USER_FORM: number = 1;
    static readonly FIELD_STEP_VERIFY_OTP_FORM: number = 2;
    static readonly FIELD_STEP_VERIFY_PASSWORD_FORM: number = 3;
    static readonly FIELD_STEP_VEHICLE_FORM: number = 4;
}
