import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { inboxTuplePrefix } from "../../plugin-inbox-names";

@addTupleType
export class AdminSendTestTaskActionTuple extends TupleActionABC {
    static readonly tupleName =
        inboxTuplePrefix + "AdminSendTestTaskActionTuple";

    formData: object;

    constructor() {
        super(AdminSendTestTaskActionTuple.tupleName);
    }
}
