
import { takeUntil } from "rxjs/operators";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, TupleGenericAction } from "@synerty/vortexjs";
import { Router } from "@angular/router";
import { TaskActionTuple, TaskTuple } from "@peek/peek_plugin_inbox";
import { PluginInboxRootService } from "@peek/peek_plugin_inbox/_private/plugin-inbox-root.service";
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: "plugin-inbox-task-list",
    templateUrl: "./task-list.component.html",
    styleUrls: ["./task-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class TaskListComponent extends NgLifeCycleEvents {
    protected readonly tasks$ = new BehaviorSubject<TaskTuple[]>([]);

    constructor(
        headerService: HeaderService,
        private rootService: PluginInboxRootService,
        private router: Router,
        private tupleService: PrivateInboxTupleProviderService,
    ) {
        super();
        headerService.setTitle("My Tasks");

        this.tasks$.next(this.tupleService.tasks);
        this.tupleService.taskTupleObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: TaskTuple[]) => this.tasks$.next(tuples));
    }

    protected hasItems(): boolean {
        return this.tasks$.getValue()?.length > 0;
    }

    protected hasRoute(task: TaskTuple): boolean {
        return task.routePath != null && task.routePath.length > 0;
    }

    protected formatDateTime(task: TaskTuple): string {
        return new Date(task.dateTime).toLocaleString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: 'short'
        });
    }

    protected getTimePast(task: TaskTuple): string {
        const duration = new Date().getTime() - new Date(task.dateTime).getTime();
        return this.formatDuration(duration);
    }

    protected handleTaskClick(task: TaskTuple): void {
        if (this.hasRoute(task)) {
            this.router.navigate([task.routePath]);
        }
        this.rootService.taskSelected(task.id);
    }

    protected handleActionClick(task: TaskTuple, taskAction: TaskActionTuple): void {
        if (taskAction.confirmMessage && !confirm(taskAction.confirmMessage)) {
            return;
        }

        const action = new TupleGenericAction();
        action.key = TaskActionTuple.tupleName;
        action.data = { id: taskAction.id };
        
        this.tupleService.tupleOfflineAction
            .pushAction(action)
            .catch((err) => alert(err));

        this.rootService.taskActioned(task.id);
    }

    private formatDuration(ms: number): string {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''}`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''}`;
        return `${seconds} second${seconds !== 1 ? 's' : ''}`;
    }
}