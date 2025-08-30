import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../_private/PluginNames";

@addTupleType
export class UserListItemTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserListItemTuple";
    userId: string = "";
    displayName: string = "";
    mobile: string = "";
    lastLoginDate: Date;
    lastLoginDeviceToken: string;

    private _loggedInLast30Days: boolean | null = null;
    private _combinedDisplayStrForSearch: string | null = null;

    constructor() {
        super(UserListItemTuple.tupleName); // Matches server side
    }

    get userName(): string {
        return this.userId;
    }

    get userTitle(): string {
        return this.displayName;
    }

    get loggedInLast30Days(): boolean {
        if (this._loggedInLast30Days != null) {
            return this._loggedInLast30Days;
        }

        if (!this.lastLoginDate) {
            return false;
        }

        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        this._loggedInLast30Days = this.lastLoginDate >= thirtyDaysAgo;
        return this._loggedInLast30Days;
    }

    get combinedDisplayStrForSearch(): string {
        if (this._combinedDisplayStrForSearch != null) {
            return this._combinedDisplayStrForSearch;
        }

        const parts = [
            this.displayName,
            this.userId ? `(${this.userId})` : null,
            this.mobile,
        ];
        this._combinedDisplayStrForSearch = parts
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
        return this._combinedDisplayStrForSearch;
    }
}
