import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { inboxFilt } from "@peek/peek_plugin_inbox/plugin-inbox-names";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

class SettingProperty extends Tuple {
    id: number;
    settingId: number;
    key: string;
    type: string;
    int_value: number;
    char_value: string;
    boolean_value: boolean;

    constructor() {
        super("c.s.p.setting.property");
    }
}

@Component({
    selector: "pl-inbox-setting-list",
    templateUrl: "./admin-setting-list.component.html",
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminSettingListComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingProperty[]>([]);
    protected readonly loader: TupleLoader;

    private readonly filt = {
        key: "server.setting.data",
        ...inboxFilt,
    };

    constructor(
        vortexService: VortexService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, this.filt);

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingProperty[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected handleSave(): void {
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected handleReset(): void {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}
