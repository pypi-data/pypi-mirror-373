
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { NgLifeCycleEvents, TupleActionPushService } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminSendTestActivityActionTuple } from "@peek/peek_plugin_inbox/_private";
import { BehaviorSubject } from "rxjs";

interface ActivityForm {
    uniqueId: string | null;
    userId: string | null;
    title: string | null;
    iconPath: string | null;
    description: string | null;
    routePath: string | null;
    routeParamJson: string | null;
    autoDeleteDateTime: Date | null;
}

@Component({
    selector: "active-task-send-test-activity",
    templateUrl: "send-test-activity.component.html",
    styleUrls: ["send-test-activity.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class SendTestActivityComponent extends NgLifeCycleEvents {
    protected readonly activity$ = new BehaviorSubject<ActivityForm>({
        uniqueId: null,
        userId: null,
        title: null,
        iconPath: null,
        description: null,
        routePath: null,
        routeParamJson: null,
        autoDeleteDateTime: new Date(Date.now() + 24 * 60 * 60 * 1000) // Tomorrow
    });

    constructor(
        private tupleActionPush: TupleActionPushService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();
    }

    protected async handleSend(): Promise<void> {
        const activityCopy = { ...this.activity$.getValue() };
        
        const action = new AdminSendTestActivityActionTuple();
        action.formData = {
            ...activityCopy,
            autoDeleteDateTime: activityCopy.autoDeleteDateTime?.toString() || ''
        };

        try {
            await this.tupleActionPush.pushAction(action);
            this.balloonMsg.showSuccess("Activity created successfully");
        } catch (e) {
            this.balloonMsg.showError(`Failed to create activity ${e}`);
        }
    }

    protected handleFormUpdate(field: keyof ActivityForm, value: any): void {
        const current = this.activity$.getValue();
        this.activity$.next({
            ...current,
            [field]: value
        });
    }
}