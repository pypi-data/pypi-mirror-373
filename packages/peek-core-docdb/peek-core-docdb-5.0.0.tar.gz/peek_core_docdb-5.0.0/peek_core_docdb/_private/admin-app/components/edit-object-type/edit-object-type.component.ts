import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { docDbFilt } from "@peek/peek_core_docdb/_private";
import {
    DocDbDocumentTypeTuple,
    DocDbModelSetTuple,
} from "@peek/peek_core_docdb";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-edit-object-type",
    templateUrl: "./edit-object-type.component.html",
    styleUrls: ["./edit-object-type.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditDocumentTypeComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<DocDbDocumentTypeTuple[]>(
        [],
    );
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly modelSetById$ = new BehaviorSubject<{
        [id: number]: DocDbModelSetTuple;
    }>({});
    protected readonly documentTypeById$ = new BehaviorSubject<{
        [id: number]: DocDbDocumentTypeTuple;
    }>({});

    private readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocDbDocumentTypeTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
        private tupleObserver: TupleDataObserverService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, docDbFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <DocDbDocumentTypeTuple[]>tuples;
                this.items$.next(typedTuples);
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

    protected modelSetTitle(tuple: DocDbDocumentTypeTuple): string {
        const modelSets = this.modelSetById$.getValue();
        const modelSet = modelSets[tuple.modelSetId];
        return modelSet?.name || "";
    }
}
