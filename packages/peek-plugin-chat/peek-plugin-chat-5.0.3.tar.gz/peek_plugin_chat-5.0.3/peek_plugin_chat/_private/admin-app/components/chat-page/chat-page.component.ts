
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "chat-admin",
    templateUrl: "chat-page.component.html",
    styleUrls: ["chat-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}