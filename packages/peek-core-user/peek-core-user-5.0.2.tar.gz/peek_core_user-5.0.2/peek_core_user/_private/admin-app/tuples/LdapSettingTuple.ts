import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class LdapSettingTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "LdapSettingTuple";

    //  Description of date1
    id: number;

    ldapTitle: string;
    ldapDomain: string;
    ldapUri: string;
    ldapCNFolders: string;
    ldapOUFolders: string;
    ldapGroups: string;

    adminEnabled: boolean;
    desktopEnabled: boolean;
    mobileEnabled: boolean;

    agentHost: string;

    constructor() {
        super(LdapSettingTuple.tupleName);
    }
}
