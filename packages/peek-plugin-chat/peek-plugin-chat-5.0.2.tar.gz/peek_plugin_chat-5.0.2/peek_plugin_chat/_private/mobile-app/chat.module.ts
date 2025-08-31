import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import {
    chatActionProcessorName,
    chatFilt,
    chatObservableName,
    chatTupleOfflineServiceName,
} from "@peek/peek_plugin_chat/_private";
import { MsgListComponent } from "./msg-list/msg-list.component";
import { ChatListComponent } from "./chat-list/chat-list.component";
import { pluginRoutes } from "./chat.routes";
import { NewChatComponent } from "./chat-list/new-chat/new-chat.component";

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(chatTupleOfflineServiceName);
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(chatObservableName, chatFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(chatActionProcessorName, chatFilt);
}

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        HttpClientModule,
        NzIconModule,
    ],
    exports: [],
    providers: [
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
        TupleActionPushOfflineService,
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
    ],
    declarations: [MsgListComponent, ChatListComponent, NewChatComponent],
})
export class ChatModule {}
