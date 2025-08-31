
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { AdminStatusTuple } from "@peek/peek_core_docdb/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly statusData$ = new BehaviorSubject<AdminStatusTuple | null>(
        null
    );

    constructor(
        private readonly balloonMsg: BalloonMsgService,
        private readonly tupleObserver: TupleDataObserverService,
    ) {
        super();

        const ts = new TupleSelector(AdminStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const adminTuples = tuples as AdminStatusTuple[];
                this.statusData$.next(adminTuples[0] || null);
            });
    }
}