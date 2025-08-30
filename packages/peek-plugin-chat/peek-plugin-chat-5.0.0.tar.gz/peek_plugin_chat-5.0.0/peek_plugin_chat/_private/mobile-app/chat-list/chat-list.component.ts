import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import {
    chatBaseUrl,
    ChatTuple,
    ChatUserTuple,
    CreateChatActionTuple,
} from "@peek/peek_plugin_chat/_private";
import { UserService } from "@peek/peek_core_user";
import { NewChatDialogData } from "./new-chat/new-chat.component";

@Component({
    selector: "plugin-chat-chat-list",
    templateUrl: "chat-list.component.mweb.html",
})
export class ChatListComponent extends NgLifeCycleEvents {
    chats: Array<ChatTuple> = [];

    newChatDialogData: NewChatDialogData = null;
    private userId: string;

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionService: TupleActionPushService,
        private tupleDataObserver: TupleDataObserverService,
        private router: Router,
        private userService: UserService,
        headerService: HeaderService,
    ) {
        super();
        headerService.setTitle("Chats");

        this.userId = userService.userDetails.userId;

        // Create the TupleSelector to tell the observable what data we want
        let tupleSelector = new TupleSelector(ChatTuple.tupleName, {
            userId: this.userId,
        });

        // Setup a subscription for the data
        let sup = tupleDataObserver
            .subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: ChatTuple[]) => {
                // We've got new data, assign it to our class variable
                this.chats = tuples;
            });

        // unsubscribe when this component is destroyed
        // This is a feature of NgLifeCycleEvents
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());
    }

    // ---- Data manipulation methods

    // ---- User Input methods
    mainClicked() {
        this.router.navigate([chatBaseUrl]);
    }

    newChatClicked() {
        this.newChatDialogData = new NewChatDialogData();
    }

    chatClicked(chat) {
        this.router.navigate([chatBaseUrl, "messages", chat.id]);
    }

    userDisplayName(chatUser: ChatUserTuple): string {
        return this.userService.userDisplayName(chatUser.userId);
    }

    // ---- Display methods

    isNewChatDialogShown(): boolean {
        return this.newChatDialogData != null;
    }

    otherChatUsers(chat: ChatTuple): ChatUserTuple[] {
        return chat.users.filter((cu) => cu.userId != this.userId);
    }

    isChatRead(chat: ChatTuple): boolean {
        let chatUser = chat.users.filter((cu) => cu.userId == this.userId)[0];
        return chat.lastActivity <= chatUser.lastReadDate;
    }

    dialogConfirmed(data: NewChatDialogData) {
        // Safeguard against angular calling this twice
        if (this.newChatDialogData == null) return;

        // Check if this is a unique chat.
        this.createChat(data);

        this.newChatDialogData = null;
    }

    dialogCanceled() {
        this.newChatDialogData = null;
    }

    private createChat(data: NewChatDialogData) {
        let action = new CreateChatActionTuple();
        action.userIds = data.users.map((u) => u.userId);
        action.fromUserId = this.userService.loggedInUserDetails.userId;
        this.actionService
            .pushAction(action)
            .then(() => {
                this.balloonMsg.showSuccess("Chat Created");
            })
            .catch((err) => alert(err));
    }
}
