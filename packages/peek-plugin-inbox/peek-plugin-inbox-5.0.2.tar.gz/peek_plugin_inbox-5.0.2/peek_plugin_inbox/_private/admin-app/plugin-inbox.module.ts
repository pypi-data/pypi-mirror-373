import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzCheckboxModule } from "ng-zorro-antd/checkbox";
import { NzSelectModule } from "ng-zorro-antd/select";
import { NzDatePickerModule } from "ng-zorro-antd/date-picker";

import { PluginInboxPageComponent } from "./components/plugin-inbox-page/plugin-inbox-page.component";
import { SendTestTaskComponent } from "./components/send-test-task/send-test-task.component";
import { SendTestActivityComponent } from "./components/send-test-activity/send-test-activity.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";

import {
    inboxActionProcessorName,
    inboxFilt,
    inboxObservableName,
    inboxTupleOfflineServiceName,
} from "@peek/peek_plugin_inbox/plugin-inbox-names";
import { AdminSettingListComponent } from "./components/setting-list/admin-setting-list.component";
import { AdminTaskListComponent } from "./components/task-list/admin-task-list.component";
import { AdminActivityListComponent } from "./components/activity-list/admin-activity-list.component";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";

export const pluginRoutes: Routes = [
    {
        path: "",
        component: PluginInboxPageComponent,
    },
];

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(inboxObservableName, inboxFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(inboxActionProcessorName, inboxFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(inboxTupleOfflineServiceName);
}

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        RouterModule.forChild(pluginRoutes),
        NzTabsModule,
        NzGridModule,
        NzFormModule,
        NzInputModule,
        NzButtonModule,
        NzTableModule,
        NzCardModule,
        NzCheckboxModule,
        NzSelectModule,
        NzDatePickerModule,
        NzEmptyModule,
        NzTagModule,
        NzDividerModule,
        NzButtonModule,
    ],
    exports: [],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
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
    ],
    declarations: [
        PluginInboxPageComponent,
        SendTestTaskComponent,
        SendTestActivityComponent,
        AdminSettingListComponent,
        AdminTaskListComponent,
        AdminActivityListComponent,
    ],
})
export class PluginInboxAdminModule {}
