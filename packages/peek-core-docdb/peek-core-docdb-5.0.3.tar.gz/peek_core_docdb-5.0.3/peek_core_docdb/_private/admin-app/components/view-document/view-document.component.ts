
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { docDbFilt } from "@peek/peek_core_docdb/_private";
import { DocumentTuple } from "@peek/peek_core_docdb";
import { BehaviorSubject } from "rxjs";
import { debounceTime, distinctUntilChanged, takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-view-document",
    templateUrl: "./view-document.component.html",
    styleUrls: ["./view-document.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ViewDocumentComponent extends NgLifeCycleEvents {
    protected readonly docKey$ = new BehaviorSubject<string>("");
    protected readonly modelSetKey$ = new BehaviorSubject<string>("");
    protected readonly doc$ = new BehaviorSubject<any>({});
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly jsonDoc$ = new BehaviorSubject<string>("");

    private readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocumentTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign(
                {
                    docKey: this.docKey$.getValue(),
                    modelSetKey: this.modelSetKey$.getValue(),
                },
                this.filt,
                docDbFilt,
            ),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((genericTuples: Tuple[]) => {
                const tuples = <DocumentTuple[]>genericTuples;
                if (tuples.length === 0) {
                    this.doc$.next({});
                    this.jsonDoc$.next("");
                } else {
                    this.doc$.next(tuples[0]);
                    this.updateJsonDoc(tuples[0]);
                }
            });

        // Auto-fetch when docKey changes with debounce
        this.docKey$
            .pipe(
                takeUntil(this.onDestroyEvent),
                debounceTime(500),
                distinctUntilChanged(),
            )
            .subscribe(() => {
                this.handleFetch();
            });
    }

    protected setDocKey(value: string): void {
        this.docKey$.next(value);
    }

    protected handleFetch(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .then(() => {
                if (this.doc$.getValue().key != null) {
                    this.balloonMsg.showSuccess("Fetch Successful");
                } else {
                    this.balloonMsg.showInfo("No matching document");
                }
            })
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }

    private updateJsonDoc(doc: any): void {
        try {
            const jsonData = JSON.parse(doc.documentJson || "{}");
            // Remove keys starting with underscore
            Object.keys(jsonData).forEach((key) => {
                if (key.startsWith("_")) {
                    delete jsonData[key];
                }
            });
            this.jsonDoc$.next(JSON.stringify(jsonData, null, 2));
        } catch (e) {
            this.jsonDoc$.next("");
            console.error("Error parsing document JSON:", e);
        }
    }
}