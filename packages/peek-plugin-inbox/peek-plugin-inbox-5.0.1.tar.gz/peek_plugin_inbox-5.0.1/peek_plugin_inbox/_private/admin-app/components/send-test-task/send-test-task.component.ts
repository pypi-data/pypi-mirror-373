
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { NgLifeCycleEvents, TupleActionPushService } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminSendTestTaskActionTuple } from "@peek/peek_plugin_inbox/_private";
import { BehaviorSubject } from "rxjs";

interface TaskAction {
    title?: string;
    confirmMessage?: string;
}

interface TaskForm {
    uniqueId: string | null;
    userId: string | null;
    title: string | null;
    iconPath: string | null;
    description: string | null;
    routePath: string | null;
    routeParamJson: string | null;
    notificationRequiredFlags: number;
    notifyByPopup: boolean;
    notifyBySound: boolean;
    notifyBySms: boolean;
    notifyByEmail: boolean;
    notifyByDialog: boolean;
    displayAs: number;
    displayPriority: number;
    autoComplete: number;
    autoDelete: number;
    actions: TaskAction[];
    autoDeleteDateTime: Date;
}

enum DisplayAs {
    TASK = 0,
    MESSAGE = 1
}

enum Priority {
    SUCCESS = 1,
    INFO = 2,
    WARNING = 3,
    DANGER = 4
}

enum AutoComplete {
    OFF = 0,
    ON_DELIVER = 1,
    ON_SELECT = 2,
    ON_ACTION = 4,
    ON_DIALOG = 16
}

enum AutoDelete {
    OFF = 0,
    ON_DELIVER = 1,
    ON_SELECT = 2,
    ON_ACTION = 4,
    ON_COMPLETE = 8,
    ON_DIALOG = 16
}

@Component({
    selector: "active-task-send-test-task",
    templateUrl: "send-test-task.component.html",
    styleUrls: ["send-test-task.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class SendTestTaskComponent extends NgLifeCycleEvents {
    protected readonly DisplayAs = DisplayAs;
    protected readonly Priority = Priority;
    protected readonly AutoComplete = AutoComplete;
    protected readonly AutoDelete = AutoDelete;

    protected readonly task$ = new BehaviorSubject<TaskForm>({
        uniqueId: null,
        userId: null,
        title: null,
        iconPath: null,
        description: null,
        routePath: null,
        routeParamJson: null,
        notificationRequiredFlags: 0,
        notifyByPopup: false,
        notifyBySound: false,
        notifyBySms: false,
        notifyByEmail: false,
        notifyByDialog: false,
        displayAs: DisplayAs.TASK,
        displayPriority: Priority.SUCCESS,
        autoComplete: AutoComplete.OFF,
        autoDelete: AutoDelete.OFF,
        actions: [],
        autoDeleteDateTime: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
    });

    constructor(
        private tupleActionPush: TupleActionPushService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();
    }

    protected handleAddAction(): void {
        const current = this.task$.getValue();
        current.actions.push({});
        this.task$.next(current);
    }

    protected async handleSend(): Promise<void> {
        const taskData = this.task$.getValue();
        let flags = 0;

        if (taskData.notifyByPopup) flags |= 1;
        if (taskData.notifyBySound) flags |= 2;
        if (taskData.notifyBySms) flags |= 4;
        if (taskData.notifyByEmail) flags |= 8;
        if (taskData.notifyByDialog) flags |= 16;

        const taskCopy = {
            ...taskData,
            notificationRequiredFlags: flags
        };

        // Remove UI-specific properties
        delete taskCopy.notifyByPopup;
        delete taskCopy.notifyBySound;
        delete taskCopy.notifyBySms;
        delete taskCopy.notifyByEmail;
        delete taskCopy.notifyByDialog;

        const action = new AdminSendTestTaskActionTuple();
        action.formData = taskCopy;

        try {
            await this.tupleActionPush.pushAction(action);
            this.balloonMsg.showSuccess("Task created successfully");
        } catch (e) {
            this.balloonMsg.showError(`Failed to create task ${e}`);
        }
    }

    protected handleFormUpdate(field: keyof TaskForm, value: any): void {
        const current = this.task$.getValue();
        this.task$.next({
            ...current,
            [field]: value
        });
    }

    protected handleActionUpdate(index: number, field: keyof TaskAction, value: string): void {
        const current = this.task$.getValue();
        current.actions[index] = {
            ...current.actions[index],
            [field]: value
        };
        this.task$.next(current);
    }
}