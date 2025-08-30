import { Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../_private/PluginNames";

export class UserDetailTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserDetailTuple";
    //  The username / userid of the user, EG C917
    userName: string;
    //  The title of the user, EG 'Chief Wiggum'
    userTitle: string;
    //  An external system user uuid, EG 715903a7ebc14fb0afb00d432676c51c
    userUuid: string | null;
    //  The mobile number, EG +61 419 123 456
    mobile: string | null;
    //  The email address, EG guy@place.com
    email: string | null;
    //  A list of group names that this user belongs to
    groupNames: number[];
    // A field for additional data
    data: { [key: string]: any } | null;

    constructor() {
        super(UserDetailTuple.tupleName); // Matches server side
    }
}
