import { addTupleType, Tuple } from "@synerty/vortexjs";
import { abstracDataLoaderTuplePrefix } from "../PluginNames";

@addTupleType
export class AppServerSettingsTuple extends Tuple {
    public static readonly tupleName =
        abstracDataLoaderTuplePrefix + "AppServerSettingsTuple";

    id: number;
    appHost: string;

    appSshUsername: string;
    appSshPassword: string;
    appSshSudoTo: string;

    appOracleUsername: string;
    appOraclePassword: string;

    layerProfileName: string;

    enabled: boolean = false;

    constructor() {
        super(AppServerSettingsTuple.tupleName);
    }
}
