import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService,
} from "@synerty/vortexjs";
import { DocDbModelSetTuple, DocDbPropertyTuple } from "@peek/peek_core_docdb";
import { docDbFilt } from "@peek/peek_core_docdb/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-edit-property",
    templateUrl: "./edit-property.component.html",
    styleUrls: ["./edit-property.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditPropertyComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<DocDbPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly modelSetById$ = new BehaviorSubject<{
        [key: number]: DocDbModelSetTuple;
    }>({});

    private readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocDbPropertyTuple",
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
                const typedTuples = <DocDbPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
            });

        const ts = new TupleSelector(DocDbModelSetTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <DocDbModelSetTuple[]>tuples;
                const modelSetById: { [id: string]: DocDbModelSetTuple } = {};
                for (const tuple of typedTuples) {
                    modelSetById[tuple.id] = tuple;
                }
                this.modelSetById$.next(modelSetById);
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

    protected modelSetTitle(tuple: DocDbPropertyTuple): string {
        const modelSets = this.modelSetById$.getValue();
        const modelSet = modelSets[tuple.modelSetId];
        return modelSet?.name || "";
    }
}
