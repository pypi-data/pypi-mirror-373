import { addTupleType, Tuple } from "@synerty/vortexjs";
import { abstracDataLoaderTuplePrefix } from "../PluginNames";

@addTupleType
export class LoaderStatusTuple extends Tuple {
    public static readonly tupleName =
        abstracDataLoaderTuplePrefix + "LoaderStatusTuple";

    total: number;
    queued: number;
    processing: number;
    update: Date;

    constructor() {
        super(LoaderStatusTuple.tupleName);
    }
}
