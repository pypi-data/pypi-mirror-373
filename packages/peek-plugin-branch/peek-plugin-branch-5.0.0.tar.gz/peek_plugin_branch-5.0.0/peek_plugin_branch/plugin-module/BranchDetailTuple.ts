import { addTupleType, Tuple } from "@synerty/vortexjs";
import { branchTuplePrefix } from "./_private/PluginNames";

@addTupleType
export class BranchDetailTuple extends Tuple {
    public static readonly tupleName = branchTuplePrefix + "BranchDetailTuple";

    /** The database ID
     *
     * Consider this field private
     */
    id: number;

    /** Model Set Key */
    modelSetKey: string;

    /** Key
     *
     * The key of this branch
     */
    key: string;

    /** Name
     *
     * The location of this branch
     */
    name: string;

    /** Comment
     *
     * The location of this branch
     */
    comment: string;

    /** userName
     *
     * The location of this branch
     */
    userName: string;

    /** Updated Date
     *
     * The location of this branch
     */
    updatedDate: Date;

    /** Created Date
     *
     * The location of this branch
     */
    createdDate: Date;

    // Local state, not stored / serialized state
    __enabled = true;

    constructor() {
        super(BranchDetailTuple.tupleName);
    }
}
