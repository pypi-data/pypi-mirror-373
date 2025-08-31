import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";

@addTupleType
export class SendMessageActionTuple extends TupleActionABC {
    static readonly tupleName = chatTuplePrefix + "SendMessageActionTuple";

    chatId: number;
    fromUserId: string;
    message: string;
    priority: number;

    constructor() {
        super(SendMessageActionTuple.tupleName);
    }
}
