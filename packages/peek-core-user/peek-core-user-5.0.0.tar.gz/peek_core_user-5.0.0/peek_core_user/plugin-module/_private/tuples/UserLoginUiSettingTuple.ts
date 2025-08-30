import { Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

export class UserLoginUiSettingTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserLoginUiSettingTuple";
    //  Should the UI show the users as a list or a text box?
    showUsersAsList: boolean = false;
    //  Should the UI show the vehicle login box?
    showVehicleInput: boolean = false;

    constructor() {
        super(UserLoginUiSettingTuple.tupleName); // Matches server side
    }
}
