import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzTypographyModule } from "ng-zorro-antd/typography";
import { NzEmptyModule } from "ng-zorro-antd/empty";

// Import our components
import { ChatPageComponent } from "./components/chat-page/chat-page.component";
import { NzCardModule } from "ng-zorro-antd/card";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: ChatPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzTypographyModule,
        NzEmptyModule,
        NzCardModule,
    ],
    exports: [],
    providers: [],
    declarations: [ChatPageComponent],
})
export class ChatModule {}
