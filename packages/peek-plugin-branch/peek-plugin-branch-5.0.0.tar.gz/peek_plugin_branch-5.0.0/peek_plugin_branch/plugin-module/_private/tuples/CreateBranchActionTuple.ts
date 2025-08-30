import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { branchTuplePrefix } from "../PluginNames";
import { BranchDetailTuple } from "../../BranchDetailTuple";

@addTupleType
export class CreateBranchActionTuple extends TupleActionABC {
    static readonly tupleName = branchTuplePrefix + "CreateBranchActionTuple";

    branchDetail: BranchDetailTuple;
    offset: number;

    constructor() {
        super(CreateBranchActionTuple.tupleName);
    }
}
