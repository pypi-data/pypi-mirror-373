
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
    Tuple
} from "@synerty/vortexjs";
import {
    diagramTraceFilt,
    SettingPropertyTuple
} from "@peek/peek_plugin_diagram_trace/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-diagram-trace-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    
    private readonly loader: TupleLoader;
    private readonly filt = {
        key: "admin.Edit.SettingProperty"
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, diagramTraceFilt)
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected handleSave(): void {
        this.loading$.next(true);
        this.loader
            .save()
            .then(() => {
                this.balloonMsg.showSuccess("Save Successful");
                this.loading$.next(false);
            })
            .catch((e) => {
                this.balloonMsg.showError(e);
                this.loading$.next(false);
            });
    }

    protected handleReset(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .then(() => {
                this.balloonMsg.showSuccess("Reset Successful");
                this.loading$.next(false);
            })
            .catch((e) => {
                this.balloonMsg.showError(e);
                this.loading$.next(false);
            });
    }

    protected handleBooleanToggle(item: SettingPropertyTuple): void {
        item.boolean_value = !item.boolean_value;
    }
}