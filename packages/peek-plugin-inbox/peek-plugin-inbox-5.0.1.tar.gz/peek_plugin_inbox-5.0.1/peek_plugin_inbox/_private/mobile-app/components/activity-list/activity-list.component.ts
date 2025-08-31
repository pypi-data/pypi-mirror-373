
import { takeUntil } from "rxjs/operators";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { Router } from "@angular/router";
import { ActivityTuple, PluginInboxRootService } from "@peek/peek_plugin_inbox";
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: "plugin-inbox-activity-list",
    templateUrl: "./activity-list.component.html",
    styleUrls: ["./activity-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ActivityListComponent extends NgLifeCycleEvents {
    protected readonly activities$ = new BehaviorSubject<ActivityTuple[]>([]);

    constructor(
        headerService: HeaderService,
        private rootService: PluginInboxRootService,
        private router: Router,
        private tupleService: PrivateInboxTupleProviderService,
    ) {
        super();
        headerService.setTitle("My Activity");

        this.activities$.next(this.tupleService.activities);
        this.tupleService.activityTupleObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ActivityTuple[]) => this.activities$.next(tuples));
    }

    protected hasItems(): boolean {
        return this.activities$.getValue()?.length > 0;
    }

    protected hasRoute(activity: ActivityTuple): boolean {
        return activity.routePath != null && activity.routePath.length > 0;
    }

    protected formatDateTime(activity: ActivityTuple): string {
        return new Date(activity.dateTime).toLocaleString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: 'short'
        });
    }

    protected getTimePast(activity: ActivityTuple): string {
        const duration = new Date().getTime() - new Date(activity.dateTime).getTime();
        return this.formatDuration(duration);
    }

    protected handleActivityClick(activity: ActivityTuple): void {
        if (this.hasRoute(activity)) {
            this.router.navigate([activity.routePath]);
        }
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