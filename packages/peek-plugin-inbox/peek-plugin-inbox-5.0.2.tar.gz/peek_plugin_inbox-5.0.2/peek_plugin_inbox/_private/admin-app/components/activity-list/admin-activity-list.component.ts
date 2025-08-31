import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { ActivityTuple } from "@peek/peek_plugin_inbox/tuples/ActivityTuple";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

interface ActivityTableData {
    dateTime: Date;
    title: string;
    description: string;
}

@Component({
    selector: "admin-inbox-activity-list",
    templateUrl: "./admin-activity-list.component.html",
    styleUrls: ["./admin-activity-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminActivityListComponent extends NgLifeCycleEvents {
    protected readonly activities$ = new BehaviorSubject<ActivityTableData[]>(
        [],
    );
    protected readonly userId$ = new BehaviorSubject<string>("");
    protected readonly columns = [
        { title: "Date", key: "dateTime" },
        { title: "Title", key: "title" },
        { title: "Description", key: "description" },
    ];

    private subscription: any = null;

    constructor(private observerService: TupleDataObserverService) {
        super();
    }

    protected handleUpdate(): void {
        if (this.subscription != null) {
            this.subscription.unsubscribe();
        }

        const tupleSelector = new TupleSelector(ActivityTuple.tupleName, {
            userId: this.userId$.getValue(),
        });

        this.subscription = this.observerService
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <ActivityTuple[]>tuples;
                const sortedActivities = typedTuples
                    .sort(
                        (o1, o2) =>
                            o2.dateTime.getTime() - o1.dateTime.getTime(),
                    )
                    .map((activity) => ({
                        dateTime: activity.dateTime,
                        title: activity.title,
                        description: activity.description,
                    }));
                this.activities$.next(sortedActivities);
            });
    }
}
