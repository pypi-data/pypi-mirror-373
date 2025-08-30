import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "./PluginNames";
import { UserListItemTuple } from "../tuples/UserListItemTuple";

@addTupleType
export class UserServiceStateTuple extends Tuple {
    public static readonly tupleName =
        userTuplePrefix + "UserServiceStateTuple";

    userDetails: UserListItemTuple | null = null;
    userGroups: string[] = [];
    authToken: string | null = null;

    constructor() {
        super(UserServiceStateTuple.tupleName);
    }
}

export interface UserServiceState {
    userDisplayNameById: { [id: string]: string };
    users: UserListItemTuple[];
    serviceState: UserServiceStateTuple;
}

export const INITIAL_STATE: UserServiceState = {
    userDisplayNameById: {},
    users: [],
    serviceState: new UserServiceStateTuple(),
};
