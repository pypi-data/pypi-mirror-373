import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { TaskTuple } from "@peek/peek_plugin_inbox/tuples/TaskTuple";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

interface TaskTableData {
    dateTime: Date;
    title: string;
    description: string;
}

@Component({
    selector: "admin-inbox-task-list",
    templateUrl: "./admin-task-list.component.html",
    styleUrls: ["./admin-task-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminTaskListComponent extends NgLifeCycleEvents {
    protected readonly tasks$ = new BehaviorSubject<TaskTableData[]>([]);
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

        const tupleSelector = new TupleSelector(TaskTuple.tupleName, {
            userId: this.userId$.getValue(),
        });

        this.subscription = this.observerService
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <TaskTuple[]>tuples;
                const sortedTasks = typedTuples
                    .sort(
                        (o1, o2) =>
                            o2.dateTime.getTime() - o1.dateTime.getTime(),
                    )
                    .map((task) => ({
                        dateTime: task.dateTime,
                        title: task.title,
                        description: task.description,
                    }));
                this.tasks$.next(sortedTasks);
            });
    }
}
