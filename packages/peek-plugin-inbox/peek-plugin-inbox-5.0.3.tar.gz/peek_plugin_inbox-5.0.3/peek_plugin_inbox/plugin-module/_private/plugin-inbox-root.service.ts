import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleGenericAction } from "@synerty/vortexjs";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
    BalloonMsgClickType,
    HeaderService,
} from "@synerty/peek-plugin-base-js";
import { TaskTuple } from "../tuples/TaskTuple";
import { inboxPluginName } from "../plugin-inbox-names";
import { PrivateInboxTupleProviderService } from "./private-inbox-tuple-provider.service";
import { Capacitor } from "@capacitor/core";
import { DeviceEnrolmentService } from "@peek/peek_core_device";
import { NativeNotifier } from "./notifiers/native-notifier";
import { WebNotifier } from "./notifiers/web-notifier";

/**  Root Service
 *
 * This service will be loaded by peek-field-app when the app loads.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */
@Injectable()
export class PluginInboxRootService extends NgLifeCycleEvents {
    private tasks: TaskTuple[] = [];
    private nativeNotifier = new NativeNotifier();
    private webNotifier = new WebNotifier();
    private alarmBasePath: string = "assets/peek_plugin_inbox/alert.mp3";

    get alarmWebFullPath(): string {
        return `/${this.alarmBasePath}`;
    }

    get alarmNativeRelativePath(): string {
        // relative path to <App>/public folder
        return this.alarmBasePath;
    }

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: PrivateInboxTupleProviderService,
        private deviceService: DeviceEnrolmentService,
    ) {
        super();

        if (Capacitor.isNativePlatform()) {
            this.nativeNotifier.loadSound(this.alarmNativeRelativePath);
        } else {
            this.webNotifier.loadSound(this.alarmWebFullPath);
        }

        // Check notification permissions when deviceInfo is available
        if (Capacitor.isNativePlatform()) {
            this.nativeNotifier.checkNotificationSettings();
        }

        // Subscribe to the tuple events.
        this.tupleService
            .taskTupleObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: TaskTuple[]) => {
                // Make sure we have the latest flags, to avoid notifying the user again.
                const existingTasksById = {};

                for (const task of this.tasks) {
                    existingTasksById[task.id] = task;
                }

                for (let task of tuples) {
                    const existingTask = existingTasksById[task.id];
                    if (existingTask == null) continue;

                    task.stateFlags = task.stateFlags | existingTask.stateFlags;

                    task.notificationSentFlags =
                        task.notificationSentFlags |
                        existingTask.notificationSentFlags;
                }

                // Now we can set the tasks
                this.tasks = tuples;

                let notCompletedCount = 0;
                for (let task of this.tasks) {
                    notCompletedCount +=
                        task.isCompleted() || task.isSelected() ? 0 : 1;
                }

                this.headerService.updateBadgeCount(
                    inboxPluginName,
                    notCompletedCount,
                );

                const updateApplied =
                    this.processNotifications() ||
                    this.processDeletesAndCompletes();

                if (updateApplied) {
                    // Update the cached data
                    this.tupleService.tupleDataOfflineObserver.updateOfflineState(
                        this.tupleService.taskTupleSelector,
                        this.tasks,
                    );
                }
            });
    }

    public taskSelected(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_SELECTED);
    }

    public taskActioned(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_ACTIONED);
    }

    private addTaskStateFlag(taskId: number, stateFlag: number) {
        const filtered = this.tasks.filter((t) => t.id === taskId);
        if (filtered.length === 0) {
            // This should never happen
            return;
        }

        const thisTask = filtered[0];
        this.sendStateUpdate(thisTask, stateFlag, null);
        this.processDeletesAndCompletes();

        // Update the cached data
        this.tupleService.tupleDataOfflineObserver.updateOfflineState(
            this.tupleService.taskTupleSelector,
            this.tasks,
        );
    }

    /** Process Delegates and Complete
     *
     * This method updates the local data only.
     * Server side will apply these updates when it gets state flag updates.
     */
    private processDeletesAndCompletes(): boolean {
        let updateApplied = false;

        const tasksSnapshot = this.tasks.slice();
        for (let task of tasksSnapshot) {
            const autoComplete = task.autoComplete & task.stateFlags;
            const isAlreadyCompleted =
                TaskTuple.STATE_COMPLETED & task.stateFlags;
            if (autoComplete && !isAlreadyCompleted) {
                task.stateFlags = TaskTuple.STATE_COMPLETED | task.stateFlags;
                updateApplied = true;
            }

            // If we're in the state where we should delete, then remove it
            // from our tasks.
            if (task.autoDelete & task.stateFlags) {
                const index = this.tasks.indexOf(task);
                if (index > -1) {
                    this.tasks.splice(index, 1);
                }
                updateApplied = true;
            }
        }

        return updateApplied;
    }

    private processNotifications(): boolean {
        let updateApplied = false;

        for (const task of this.tasks) {
            let notificationSentFlags = 0;
            let newStateMask = 0;

            if (task.isNotifyBySound() && !task.isNotifiedBySound()) {
                notificationSentFlags =
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_SOUND;

                if (Capacitor.isNativePlatform()) {
                    this.nativeNotifier.playSound();
                } else {
                    this.webNotifier.playSound();
                }
            }

            if (task.isNotifyByPopup() && !task.isNotifiedByPopup()) {
                this.showMessage(BalloonMsgType.Fleeting, task)
                    .then((balloonMsgClickType: BalloonMsgClickType) => {
                        this.sendStateUpdate(task, TaskTuple.STATE_SELECTED, 0);
                    })
                    .catch((err) => {
                        const e = `Inbox Dialog Error\n${err}`;
                        console.log(e);
                        this.balloonMsg.showError(e);
                    });
                notificationSentFlags =
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_POPUP;
            }

            if (task.isNotifyByDialog() && !task.isNotifiedByDialog()) {
                this.showMessage(BalloonMsgType.Confirm, task)
                    .then((balloonMsgClickType: BalloonMsgClickType) => {
                        this.sendStateUpdate(
                            task,
                            TaskTuple.STATE_DIALOG_CONFIRMED,
                            0,
                        );
                    })
                    .catch((err) => {
                        const e = `Inbox Dialog Error\n${err}`;
                        console.log(e);
                        this.balloonMsg.showError(e);
                    });

                notificationSentFlags =
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_DIALOG;
            }

            if (!task.isDelivered()) {
                newStateMask = newStateMask | TaskTuple.STATE_DELIVERED;
            }

            if (notificationSentFlags || newStateMask) {
                updateApplied = true;

                this.sendStateUpdate(task, newStateMask, notificationSentFlags);
            }
        }

        return updateApplied;
    }

    private showMessage(
        type_: BalloonMsgType,
        task: TaskTuple,
    ): Promise<BalloonMsgClickType> {
        let level: BalloonMsgLevel | null = null;

        switch (task.displayPriority) {
            case TaskTuple.PRIORITY_SUCCESS:
                level = BalloonMsgLevel.Success;
                break;

            case TaskTuple.PRIORITY_INFO:
                level = BalloonMsgLevel.Info;
                break;

            case TaskTuple.PRIORITY_WARNING:
                level = BalloonMsgLevel.Warning;
                break;

            case TaskTuple.PRIORITY_DANGER:
                level = BalloonMsgLevel.Error;
                break;

            default:
                throw new Error(`Unknown priority ${task.displayPriority}`);
        }

        const dialogTitle = `New ${task.displayAsText()}`;
        const desc = task.description ? task.description : "";
        const msg = `${task.title}\n\n${desc}`;

        // Send local notification
        if (
            Capacitor.isNativePlatform() &&
            this.deviceService.deviceInfo.isBackgrounded
        ) {
            this.nativeNotifier.sendLocalNotification(dialogTitle, desc);
        }

        return this.balloonMsg.showMessage(msg, level, type_, {
            confirmText: "Ok",
            dialogTitle,
            routePath: task.routePath,
        });
    }

    private sendStateUpdate(
        task: TaskTuple,
        stateFlags: number | null,
        notificationSentFlags: number | null,
    ) {
        const action = new TupleGenericAction();
        action.key = TaskTuple.tupleName;
        action.data = {
            id: task.id,
            stateFlags: stateFlags,
            notificationSentFlags: notificationSentFlags,
        };
        this.tupleService.tupleOfflineAction
            .pushAction(action)
            .catch((err) => alert(err));

        if (stateFlags != null) {
            task.stateFlags = task.stateFlags | stateFlags;
        }

        if (notificationSentFlags != null) {
            task.notificationSentFlags =
                task.notificationSentFlags | notificationSentFlags;
        }
    }
}
