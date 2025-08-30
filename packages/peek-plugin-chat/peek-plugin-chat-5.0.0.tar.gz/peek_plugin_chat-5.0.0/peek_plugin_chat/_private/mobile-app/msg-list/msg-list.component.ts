import { takeUntil } from "rxjs/operators";
import { Component, ElementRef, OnInit, ViewChild } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { ActivatedRoute, Params, Router } from "@angular/router";
import {
    chatBaseUrl,
    ChatTuple,
    ChatUserReadActionTuple,
    ChatUserTuple,
    MessageTuple,
    SendMessageActionTuple,
} from "@peek/peek_plugin_chat/_private";
import { UserService } from "@peek/peek_core_user";
import * as moment from "moment";

declare let NSIndexPath: any;
declare let UITableViewScrollPosition: any;

@Component({
    selector: "plugin-chat-msg-list",
    templateUrl: "msg-list.component.mweb.html",
})
export class MsgListComponent extends NgLifeCycleEvents implements OnInit {
    chat: ChatTuple = new ChatTuple();
    chatUser: ChatUserTuple | null = null;
    newMessageText: string = "";

    @ViewChild("messageListRef", { static: true })
    messageListRef: ElementRef;

    private userId: string;

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionService: TupleActionPushService,
        private tupleDataObserver: TupleDataObserverService,
        private tupleDataOfflineObserver: TupleDataOfflineObserverService,
        private tupleOfflineAction: TupleActionPushOfflineService,
        private route: ActivatedRoute,
        private router: Router,
        private userService: UserService,
        headerService: HeaderService,
    ) {
        super();
        headerService.setTitle("Chat");

        this.userId = userService.userDetails.userId;
    }

    // ---- Data manipulation methods
    override ngOnInit() {
        this.route.params
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((params: Params) => {
                let chatId = parseInt(params["chatId"]);
                this.loadChat(chatId);
            });
    }

    // ---- Display methods
    messages(): MessageTuple[] {
        if (this.chat != null) return this.chat.messages;
        return [];
    }

    // ---- Action Methods

    haveMessages(): boolean {
        return this.chat != null && this.chat.messages.length !== 0;
    }

    sendEnabled(): boolean {
        return this.newMessageText.length != 0;
    }

    isMessageFromThisUser(msg: MessageTuple): boolean {
        return msg.fromUserId == this.userService.userDetails.userId;
    }

    userDisplayName(msg: MessageTuple): string {
        return this.userService.userDisplayName(msg.fromUserId);
    }

    isNormalPriority(msg: MessageTuple): boolean {
        return (
            msg.priority === MessageTuple.PRIORITY_NORMAL_STICKY ||
            msg.priority === MessageTuple.PRIORITY_NORMAL_FLEETING
        );
    }

    isEmergencyPriority(msg: MessageTuple): boolean {
        return msg.priority === MessageTuple.PRIORITY_EMERGENCY;
    }

    isFirstUnreadMesage(msgIndex: number): boolean {
        if (this.chat == null) return false;

        // If there are no messages, then false
        // though this method won't be called if this is the case
        if (this.chat.messages.length === 0) return false;

        let msg = this.chat.messages[msgIndex];

        if (msg == null) return false;

        // If we've read this message, then it's false.
        if (msg.dateTime <= this.chatUser.lastReadDate) return false;

        // From here on, msg is unread, we just need to work out if it's the first

        // If this is the first message...
        if (msgIndex === 0) return true;

        let lastMsg = this.chat.messages[msgIndex - 1];
        let lastIsRead = lastMsg.dateTime <= this.chatUser.lastReadDate;

        // Now, if the last message is read, and this is unread (which it is),
        // then true, this is our first unread message
        if (lastIsRead) return true;

        return false;
    }

    dateTime(msg: MessageTuple) {
        return moment(msg.dateTime).format("HH:mm DD-MMM");
    }

    timePast(msg: MessageTuple) {
        return moment
            .duration(new Date().getTime() - msg.dateTime.getTime())
            .humanize();
    }

    // ---- User Input methods
    navToChatsClicked() {
        this.router.navigate([chatBaseUrl, "chats"]);
    }

    sendMsgClicked() {
        this.sendMessage(MessageTuple.PRIORITY_NORMAL_FLEETING);
    }

    sendSosClicked() {
        let confirmResult = confirm("SEND SOS, Are you sure?");

        // On NativeScript, it returns a promise
        if (confirmResult["then"] != null) {
            confirmResult["then"]((result) => {
                if (result) this.sendSos();
            });
        } else if (confirmResult) {
            this.sendSos();
        }
    }

    private loadChat(chatId: number) {
        let tupleSelector = new TupleSelector(ChatTuple.tupleName, {
            chatId: chatId,
        });

        this.tupleDataOfflineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ChatTuple[]) => {
                if (tuples.length === 0) return;

                this.chat = tuples[0];
                this.chatUser = this.chat.users.filter(
                    (cu) => cu.userId === this.userId,
                )[0];
                setTimeout(() => this.scrollBottom(), 10);

                this.sendRead();
            });
    }

    /** Tell the server that we've read this chat up to here.
     */
    private sendRead() {
        let action = new ChatUserReadActionTuple();
        action.chatUserId = this.chatUser.id;
        action.readDateTime = new Date();

        this.actionService
            .pushAction(action)
            .then(() => {})
            .catch((err) => {
                alert(err);
            });
    }

    private sendMessage(priority) {
        let action = new SendMessageActionTuple();
        action.chatId = this.chat.id;
        action.fromUserId = this.userService.userDetails.userId;
        action.message = this.newMessageText;
        action.priority = priority;

        this.actionService
            .pushAction(action)
            .then(() => {
                this.newMessageText = "";
                this.balloonMsg.showSuccess("Message Sent");
            })
            .catch((err) => {
                alert(err);
            });
    }

    // ---- scroll update
    private scrollBottom() {
        /*
         let position = this.messages().length - 1;
         
         if (this.messageListRef == null || this.messageListRef.nativeElement == null) {
         console.log("Can not get a reference to messageListRef, scrolling failed");
         return;
         }
         
         let element = this.messageListRef.nativeElement;
         if (element["ios"] != null || element["android"] != null) {
         element.scrollToIndex(position);
         
         } else if (element["scrollTop"] != null) {
         element.scrollTop = element.scrollHeight;
         
         }
         */
    }

    private sendSos() {
        if (this.newMessageText.length === 0) this.newMessageText = "SOS";

        this.sendMessage(MessageTuple.PRIORITY_EMERGENCY);
    }
}
