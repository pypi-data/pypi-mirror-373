import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";

@addTupleType
export class ChatUserReadActionTuple extends TupleActionABC {
    static readonly tupleName = chatTuplePrefix + "ChatUserReadActionTuple";

    chatUserId: number;
    readDateTime: Date;

    constructor() {
        super(ChatUserReadActionTuple.tupleName);
    }
}
