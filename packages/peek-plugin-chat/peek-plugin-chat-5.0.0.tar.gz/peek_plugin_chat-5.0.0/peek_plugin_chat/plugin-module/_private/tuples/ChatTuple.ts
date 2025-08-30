import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";
import { ChatUserTuple } from "./ChatUserTuple";
import { MessageTuple } from "./MessageTuple";

@addTupleType
export class ChatTuple extends Tuple {
    public static readonly tupleName = chatTuplePrefix + "ChatTuple";

    //  Description of date1
    id: number;

    // Message details
    lastActivity: Date;

    usersKey: string;

    messages: MessageTuple[] = [];

    users: ChatUserTuple[] = [];

    constructor() {
        super(ChatTuple.tupleName);
    }
}
