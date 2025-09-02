
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PluginInboxRootService } from "@peek/peek_plugin_inbox";
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: "plugin-inbox",
    templateUrl: "./plugin-inbox-root.component.html",
    styleUrls: ["./plugin-inbox-root.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class PluginInboxRootComponent extends NgLifeCycleEvents {
    protected readonly barIndex$ = new BehaviorSubject<number>(0);

    constructor(
        rootService: PluginInboxRootService,
        private tupleService: PrivateInboxTupleProviderService,
    ) {
        super();
    }

    protected handleTabChange(index: number): void {
        this.barIndex$.next(index);
    }
}