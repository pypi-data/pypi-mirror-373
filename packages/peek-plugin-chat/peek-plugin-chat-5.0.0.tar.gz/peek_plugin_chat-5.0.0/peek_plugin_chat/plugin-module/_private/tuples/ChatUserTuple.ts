import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";

@addTupleType
export class ChatUserTuple extends Tuple {
    public static readonly tupleName = chatTuplePrefix + "ChatUserTuple";

    //  Description of date1
    id: number;
    chatId: number;

    // User to / from
    userId: string;
    isUserExternal: boolean;

    // User to / from
    lastReadDate: Date;

    // // Message state details
    // userName: string;

    constructor() {
        super(ChatUserTuple.tupleName);
    }
}
