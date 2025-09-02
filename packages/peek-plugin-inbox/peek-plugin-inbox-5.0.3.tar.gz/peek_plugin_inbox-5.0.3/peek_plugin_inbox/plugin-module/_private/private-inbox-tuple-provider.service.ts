import { Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Injectable, NgZone } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushOfflineSingletonService,
    TupleDataObservableNameService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { UserService } from "@peek/peek_core_user";
import { TaskTuple } from "../tuples/TaskTuple";
import { ActivityTuple } from "../tuples/ActivityTuple";
import {
    inboxActionProcessorName,
    inboxFilt,
    inboxObservableName,
    inboxTupleOfflineServiceName,
} from "../plugin-inbox-names";

@Injectable()
export class PrivateInboxTupleProviderService extends NgLifeCycleEvents {
    public tupleOfflineAction: TupleActionPushOfflineService;
    public tupleDataOfflineObserver: TupleDataOfflineObserverService;

    private tasksSubject = new Subject<TaskTuple[]>();
    private activitiesSubject = new Subject<ActivityTuple[]>();
    private taskSubscription: any | null;
    private activitiesSubscription: any | null;

    constructor(
        private userService: UserService,
        tupleActionSingletonService: TupleActionPushOfflineSingletonService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
        zone: NgZone,
    ) {
        super();

        let tupleDataObservableName = new TupleDataObservableNameService(
            inboxObservableName,
            inboxFilt,
        );
        let storageName = new TupleOfflineStorageNameService(
            inboxTupleOfflineServiceName,
        );
        let tupleActionName = new TupleActionPushNameService(
            inboxActionProcessorName,
            inboxFilt,
        );

        let tupleOfflineStorageService = new TupleOfflineStorageService(
            storageFactory,
            storageName,
        );

        this.tupleDataOfflineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            tupleDataObservableName,
            tupleOfflineStorageService,
        );

        this.tupleOfflineAction = new TupleActionPushOfflineService(
            tupleActionName,
            vortexService,
            vortexStatusService,
            tupleActionSingletonService,
        );

        this.userService.loggedInStatus
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((status) => {
                if (status) this.subscribe();
                else this.unsubscribe();
            });

        if (this.userService.loggedIn) this.subscribe();

        this.onDestroyEvent.subscribe(() => this.unsubscribe());
    }

    private _tasks: TaskTuple[] = [];

    get tasks(): TaskTuple[] {
        return this._tasks;
    }

    // -------------------------
    // Setup subscriptions when the user changes

    private _activities: ActivityTuple[] = [];

    get activities(): ActivityTuple[] {
        return this._activities;
    }

    // -------------------------
    // Properties for the UI components to use

    get taskTupleSelector(): TupleSelector {
        return new TupleSelector(TaskTuple.tupleName, {
            userId: this.userService.loggedInUserDetails.userId,
        });
    }

    get activityTupleSelector(): TupleSelector {
        return new TupleSelector(ActivityTuple.tupleName, {
            userId: this.userService.loggedInUserDetails.userId,
        });
    }

    taskTupleObservable(): Observable<TaskTuple[]> {
        return this.tasksSubject;
    }

    activityTupleObservable(): Observable<ActivityTuple[]> {
        return this.activitiesSubject;
    }

    private subscribe() {
        this.unsubscribe();

        // Load Tasks ------------------

        this.taskSubscription = this.tupleDataOfflineObserver
            .subscribeToTupleSelector(this.taskTupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: TaskTuple[]) => {
                this._tasks = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime(),
                );
                this.tasksSubject.next(this._tasks);
            });

        // Load Activities ------------------

        // We don't do anything with the activities, we just want to store
        // them offline.
        this.activitiesSubscription = this.tupleDataOfflineObserver
            .subscribeToTupleSelector(this.activityTupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ActivityTuple[]) => {
                this._activities = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime(),
                );
                this.activitiesSubject.next(this._activities);
            });
    }

    private unsubscribe() {
        if (this.activitiesSubscription != null) {
            this.activitiesSubscription.unsubscribe();
            this.activitiesSubscription = null;
        }

        if (this.taskSubscription != null) {
            this.taskSubscription.unsubscribe();
            this.taskSubscription = null;
        }
    }
}
