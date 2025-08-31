
import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule, Routes } from "@angular/router";
import { NzIconModule } from "ng-zorro-antd/icon";
import { LoggedInGuard } from "@peek/peek_core_user";
import { PluginInboxRootComponent } from "./components/plugin-inbox-root/plugin-inbox-root.component";
import { ActivityListComponent } from "./components/activity-list/activity-list.component";
import { TaskListComponent } from "./components/task-list/task-list.component";

export const pluginRoutes: Routes = [
    {
        path: "",
        component: PluginInboxRootComponent,
        canActivate: [LoggedInGuard],
    },
    {
        path: "**",
        component: PluginInboxRootComponent,
        canActivate: [LoggedInGuard],
    },
];

@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzIconModule,
    ],
    declarations: [
        PluginInboxRootComponent,
        TaskListComponent,
        ActivityListComponent,
    ],
})
export class PluginInboxClientModule {}