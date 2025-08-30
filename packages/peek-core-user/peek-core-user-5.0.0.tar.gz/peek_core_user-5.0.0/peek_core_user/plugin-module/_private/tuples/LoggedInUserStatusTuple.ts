import { Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../PluginNames";

export class LoggedInUserStatusTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "LoggedInUserStatusTuple";
    //  The username / userid of the user, EG C917
    userName: string;
    //  The title of the user, EG 'Chief Wiggum'
    userTitle: string;
    //  The vehicle the user is logged in with
    vehicle: string;
    //  The date that the user logged in
    loginDate: Date;
    //  The token of the device
    deviceToken: string | null;
    //  Is the device online now
    deviceIsOnline: boolean | null;
    //  The last time the device was online
    deviceLastOnline: Date | null;
    //  The device type
    deviceType: string | null;
    //  The device description
    deviceDescription: string | null;

    constructor() {
        super(LoggedInUserStatusTuple.tupleName); // Matches server side
    }
}
