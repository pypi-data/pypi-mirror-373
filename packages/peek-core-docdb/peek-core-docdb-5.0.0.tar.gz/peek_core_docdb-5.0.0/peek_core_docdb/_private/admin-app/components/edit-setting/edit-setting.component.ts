
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    docDbFilt,
    SettingPropertyTuple,
} from "@peek/peek_core_docdb/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-edit-setting",
    templateUrl: "./edit-setting.component.html",
    styleUrls: ["./edit-setting.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);

    private readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, docDbFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: SettingPropertyTuple[]) => {
                this.items$.next(tuples);
            });
    }

    protected handleSave(): void {
        this.loading$.next(true);
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }

    protected handleReset(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }
}