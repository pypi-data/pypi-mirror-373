import { inboxTuplePrefix } from "../plugin-inbox-names";
import { addTupleType, Tuple } from "@synerty/vortexjs";
import { TaskActionTuple } from "./TaskActionTuple";

@addTupleType
export class TaskTuple extends Tuple {
    static readonly tupleName = inboxTuplePrefix + "Task";
    static readonly AUTO_COMPLETE_OFF = 0;
    static readonly AUTO_COMPLETE_ON_DELIVER = 1;
    static readonly AUTO_COMPLETE_ON_SELECT = 2;
    static readonly AUTO_COMPLETE_ON_ACTION = 4;
    static readonly AUTO_COMPLETE_ON_DIALOG = 16;
    static readonly AUTO_DELETE_OFF = 0;
    static readonly AUTO_DELETE_ON_DELIVER = 1;
    static readonly AUTO_DELETE_ON_SELECT = 2;
    static readonly AUTO_DELETE_ON_ACTION = 4;
    static readonly AUTO_DELETE_ON_COMPLETE = 8;
    static readonly AUTO_DELETE_ON_DIALOG = 16;
    // The state of this action
    static readonly STATE_DELIVERED = 1;
    static readonly STATE_SELECTED = 2;
    static readonly STATE_ACTIONED = 4;
    static readonly STATE_COMPLETED = 8;
    static readonly STATE_DIALOG_CONFIRMED = 16;
    static readonly NOTIFY_BY_DEVICE_POPUP = 1;
    static readonly NOTIFY_BY_DEVICE_SOUND = 2;
    static readonly NOTIFY_BY_SMS = 4;
    static readonly NOTIFY_BY_EMAIL = 8;
    static readonly NOTIFY_BY_DEVICE_DIALOG = 16;
    static readonly DISPLAY_AS_TASK = 0;
    static readonly DISPLAY_AS_MESSAGE = 1;
    static readonly PRIORITY_SUCCESS = 1;
    static readonly PRIORITY_INFO = 2;
    static readonly PRIORITY_WARNING = 3;
    static readonly PRIORITY_DANGER = 4;
    id: number;
    pluginName: string;
    uniqueId: string;
    userId: string;
    dateTime: Date;
    // The display properties of the task
    title: string;
    description: string;
    iconPath: string;
    // The mobile-app route to open when this task is selected
    routePath: string;
    routeParamJson: {};
    autoComplete: number;
    autoDelete: number;
    stateFlags: number;
    notificationRequiredFlags: number;
    notificationSentFlags: number;
    displayAs: number;
    displayPriority: number;

    // The actions for this TaskTuple.
    actions: TaskActionTuple[];

    constructor() {
        super(TaskTuple.tupleName);
    }

    // ------------------------------
    // State properties
    isCompleted(): boolean {
        return !!(this.stateFlags & TaskTuple.STATE_COMPLETED);
    }

    isActioned(): boolean {
        return !!(this.stateFlags & TaskTuple.STATE_ACTIONED);
    }

    isDelivered(): boolean {
        return !!(this.stateFlags & TaskTuple.STATE_DELIVERED);
    }

    isSelected(): boolean {
        return !!(this.stateFlags & TaskTuple.STATE_SELECTED);
    }

    // ------------------------------
    // Notifications Required properties
    isNotifyBySound(): boolean {
        return !!(
            this.notificationRequiredFlags & TaskTuple.NOTIFY_BY_DEVICE_SOUND
        );
    }

    isNotifyByPopup(): boolean {
        return !!(
            this.notificationRequiredFlags & TaskTuple.NOTIFY_BY_DEVICE_POPUP
        );
    }

    isNotifyByDialog(): boolean {
        return !!(
            this.notificationRequiredFlags & TaskTuple.NOTIFY_BY_DEVICE_DIALOG
        );
    }

    // ------------------------------
    // Notifications Sent properties
    isNotifiedBySound(): boolean {
        return !!(
            this.notificationSentFlags & TaskTuple.NOTIFY_BY_DEVICE_SOUND
        );
    }

    isNotifiedByPopup(): boolean {
        return !!(
            this.notificationSentFlags & TaskTuple.NOTIFY_BY_DEVICE_POPUP
        );
    }

    isNotifiedByDialog(): boolean {
        return !!(
            this.notificationSentFlags & TaskTuple.NOTIFY_BY_DEVICE_DIALOG
        );
    }

    // ------------------------------
    // Notification properties
    isTask(): boolean {
        return this.displayAs == TaskTuple.DISPLAY_AS_TASK;
    }

    isMessage(): boolean {
        return this.displayAs == TaskTuple.DISPLAY_AS_MESSAGE;
    }

    displayAsText(): string {
        switch (this.displayAs) {
            case TaskTuple.DISPLAY_AS_TASK: {
                return "Task";
            }

            case TaskTuple.DISPLAY_AS_MESSAGE: {
                return "Message";
            }

            default: {
                throw new Error(`Unknown displayAs type ${this.displayAs}`);
            }
        }
    }

    // ------------------------------
    // Priority properties

    isPrioritySuccess(): boolean {
        return this.displayPriority === TaskTuple.PRIORITY_SUCCESS;
    }

    isPriorityInfo(): boolean {
        return this.displayPriority === TaskTuple.PRIORITY_INFO;
    }

    isPriorityWarning(): boolean {
        return this.displayPriority === TaskTuple.PRIORITY_WARNING;
    }

    isPriorityDanger(): boolean {
        return this.displayPriority === TaskTuple.PRIORITY_DANGER;
    }
}
