import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";

@addTupleType
export class CreateChatActionTuple extends TupleActionABC {
    static readonly tupleName = chatTuplePrefix + "CreateChatActionTuple";

    userIds: string[];
    fromUserId: string;

    constructor() {
        super(CreateChatActionTuple.tupleName);
    }
}
