import { addTupleType, Tuple } from "@synerty/vortexjs";
import { gisDiagramTuplePrefix } from "../PluginNames";

@addTupleType
export class GisDiagramTuple extends Tuple {
    public static readonly tupleName =
        gisDiagramTuplePrefix + "GisDiagramTuple";

    //  Description of date1
    dict1: {};

    //  Description of array1
    array1: any[];

    //  Description of date1
    date1: Date;

    constructor() {
        super(GisDiagramTuple.tupleName);
    }
}
