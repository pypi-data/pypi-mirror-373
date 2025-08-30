import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chatTuplePrefix } from "../PluginNames";

@addTupleType
export class MessageTuple extends Tuple {
    public static readonly tupleName = chatTuplePrefix + "MessageTuple";
    // Emergency priority for message
    public static readonly PRIORITY_EMERGENCY = 1;
    // Normal priority for a message, the alert will be fleeting
    public static readonly PRIORITY_NORMAL_FLEETING = 2;
    // Normal priority for message, the alert will be sticky
    public static readonly PRIORITY_NORMAL_STICKY = 3;
    //  Description of date1
    id: number;
    chatId: number;
    // Message details
    message: string;
    priority: number;
    // User to / from
    fromUserId: string;

    // Message state details
    dateTime: Date;

    // onReadPayload = Column(PeekVarBinary)

    constructor() {
        super(MessageTuple.tupleName);
    }
}
