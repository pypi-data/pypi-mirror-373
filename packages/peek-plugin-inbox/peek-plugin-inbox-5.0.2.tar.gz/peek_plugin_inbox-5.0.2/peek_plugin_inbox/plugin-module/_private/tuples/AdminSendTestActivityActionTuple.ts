import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { inboxTuplePrefix } from "../../plugin-inbox-names";

@addTupleType
export class AdminSendTestActivityActionTuple extends TupleActionABC {
    static readonly tupleName =
        inboxTuplePrefix + "AdminSendTestActivityActionTuple";

    formData: object;

    constructor() {
        super(AdminSendTestActivityActionTuple.tupleName);
    }
}
