import { inboxTuplePrefix } from "../plugin-inbox-names";
import { addTupleType, Tuple } from "@synerty/vortexjs";

@addTupleType
export class TaskActionTuple extends Tuple {
    static readonly tupleName = inboxTuplePrefix + "TaskAction";

    id: number;
    taskId: number;
    title: string;
    confirmMessage: string;

    constructor() {
        super(TaskActionTuple.tupleName);
    }
}
