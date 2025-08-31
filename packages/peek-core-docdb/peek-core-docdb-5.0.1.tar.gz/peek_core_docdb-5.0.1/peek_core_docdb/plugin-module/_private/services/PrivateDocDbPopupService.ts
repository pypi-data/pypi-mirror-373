import { Injectable, NgZone } from "@angular/core";
import {
    DocDbPopupActionI,
    DocDbPopupClosedReasonE,
    DocDbPopupContextI,
    DocDbPopupDetailI,
    DocDbPopupService,
    DocDbPopupTypeE,
    ObjectTriggerOptionsI,
    ObjectTriggerPositionI,
} from "../../DocDbPopupService";
import { BehaviorSubject, fromEvent, Observable, Subject } from "rxjs";
import {
    DocDbPropertyTuple,
    DocDbPropertyTypeFilterI,
    DocDbService,
    DocumentResultI,
} from "@peek/peek_core_docdb";
import { assert, sortText } from "@synerty/vortexjs";
import { DOCDB_POPUP } from "@peek/peek_core_docdb/constants";
import { first } from "rxjs/operators";

export class PopupTriggeredParams {
    actions$ = new BehaviorSubject<DocDbPopupActionI[]>([]);
    details$ = new BehaviorSubject<DocDbPopupDetailI[]>([]);

    constructor(
        public triggeredByPlugin: string,
        public position: ObjectTriggerPositionI,
        public modelSetKey: string,
        public objectKey: string,
        public options: ObjectTriggerOptionsI,
    ) {}

    get actions() {
        return this.actions$.getValue();
    }

    set actions(value) {
        this.actions$.next(value);
    }

    get details() {
        return this.details$.getValue();
    }

    set details(value) {
        this.details$.next(value);
    }
}

@Injectable()
export class PrivateDocDbPopupService extends DocDbPopupService {
    showTooltipPopupSubject = new Subject<PopupTriggeredParams>();
    hideTooltipPopupSubject = new Subject<void>();
    showSummaryPopupSubject = new Subject<PopupTriggeredParams>();
    hideSummaryPopupSubject = new Subject<void>();
    showDetailPopupSubject = new Subject<PopupTriggeredParams>();
    hideDetailPopupSubject = new Subject<void>();

    private tooltipPopupSubject = new Subject<DocDbPopupContextI>();
    private tooltipPopupClosedSubject = new Subject<DocDbPopupClosedReasonE>();
    private summaryPopupSubject = new Subject<DocDbPopupContextI>();
    private summaryPopupClosedSubject = new Subject<DocDbPopupClosedReasonE>();
    private detailPopupSubject = new Subject<DocDbPopupContextI>();
    private detailPopupClosedSubject = new Subject<DocDbPopupClosedReasonE>();

    private readonly DATA_LOAD_LEAD_TIME_MS = 200;
    private readonly TOOLTIP_POPUP_DELAY_TIME_MS = 700;

    private shownPopup: DocDbPopupTypeE | null = null;
    private popupClicked: boolean = false;

    constructor(
        private docDbService: DocDbService,
        protected zone: NgZone,
    ) {
        super();
        this.handleHidePopups();
    }

    handleHidePopups(): void {
        fromEvent(document, "touchstart").subscribe((event: any) =>
            this.handleCloseEvents(event),
        );

        fromEvent(document, "mousedown").subscribe((event: any) =>
            this.handleCloseEvents(event),
        );
    }

    handleCloseEvents(event): void {
        if (!this.popupClicked) {
            return;
        }
        for (const el of event.path || event.composedPath()) {
            if (el.id === DOCDB_POPUP) {
                return;
            }
        }
        this.hideAllPopups();
    }

    showPopup(
        popupClicked: boolean,
        popupType: DocDbPopupTypeE,
        triggeredByPlugin: string,
        position: ObjectTriggerPositionI,
        modelSetKey: string,
        objectKey: string,
        options: ObjectTriggerOptionsI = {},
    ): void {
        if (this.popupClicked && !popupClicked) {
            return;
        }

        this.hidePopup(DocDbPopupTypeE.tooltipPopup);

        this.shownPopup = popupType;
        this.popupClicked = popupClicked;

        const params = new PopupTriggeredParams(
            triggeredByPlugin,
            position,
            modelSetKey,
            objectKey,
            Object.assign({ popupDelayMs: 0 }, options),
        );

        if (popupType == DocDbPopupTypeE.tooltipPopup) {
            params.options.popupDelayMs =
                params.options.popupDelayMs || this.TOOLTIP_POPUP_DELAY_TIME_MS;

            this.triggerPopup(
                popupType,
                params,
                this.showTooltipPopupSubject,
                this.hideTooltipPopupSubject,
                this.tooltipPopupSubject,
                (prop: DocDbPropertyTuple) => prop.showOnTooltip,
            );
        } else if (popupType == DocDbPopupTypeE.summaryPopup) {
            this.triggerPopup(
                popupType,
                params,
                this.showSummaryPopupSubject,
                this.hideSummaryPopupSubject,
                this.summaryPopupSubject,
                (prop: DocDbPropertyTuple) => prop.showOnSummary,
            );
        } else if (popupType == DocDbPopupTypeE.detailPopup) {
            this.triggerPopup(
                popupType,
                params,
                this.showDetailPopupSubject,
                this.hideDetailPopupSubject,
                this.detailPopupSubject,
                (prop: DocDbPropertyTuple) => prop.showOnDetail,
            );
        } else {
            throw new Error(`showPopup:Unhandled popup type ${popupType}`);
        }
    }

    hidePopupWithReason(
        popupType: DocDbPopupTypeE,
        reason: DocDbPopupClosedReasonE,
    ): void {
        this.shownPopup = null;
        this.hideTooltipPopupSubject.next();
        this.tooltipPopupClosedSubject.next(reason);
        this.hideSummaryPopupSubject.next();
        this.summaryPopupClosedSubject.next(reason);
        this.hideDetailPopupSubject.next();
        this.detailPopupClosedSubject.next(reason);
    }

    hidePopup(popupType: DocDbPopupTypeE): void {
        this.hidePopupWithReason(
            popupType,
            DocDbPopupClosedReasonE.closedByApiCall,
        );
    }

    hideHoverPopup(): void {
        if (this.popupClicked) {
            return;
        }

        this.hidePopup(DocDbPopupTypeE.tooltipPopup);
    }

    hideAllPopups(): void {
        this.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.hidePopup(DocDbPopupTypeE.summaryPopup);
        this.hidePopup(DocDbPopupTypeE.detailPopup);
        this.popupClicked = false;
    }

    popupObservable(
        popupType: DocDbPopupTypeE,
    ): Observable<DocDbPopupContextI> {
        if (popupType == DocDbPopupTypeE.tooltipPopup) {
            return this.tooltipPopupSubject.asObservable();
        } else if (popupType == DocDbPopupTypeE.summaryPopup) {
            return this.summaryPopupSubject.asObservable();
        } else if (popupType == DocDbPopupTypeE.detailPopup) {
            return this.detailPopupSubject.asObservable();
        } else {
            throw new Error(
                `popupObservable:Unhandled popup type ${popupType}`,
            );
        }
    }

    popupClosedObservable(
        popupType: DocDbPopupTypeE,
    ): Observable<DocDbPopupClosedReasonE> {
        if (popupType == DocDbPopupTypeE.tooltipPopup) {
            return this.tooltipPopupClosedSubject.asObservable();
        } else if (popupType == DocDbPopupTypeE.summaryPopup) {
            return this.summaryPopupClosedSubject.asObservable();
        } else if (popupType == DocDbPopupTypeE.detailPopup) {
            return this.detailPopupClosedSubject.asObservable();
        } else {
            throw new Error(
                `popupObservable:Unhandled popup type ${popupType}`,
            );
        }
    }

    private triggerPopup(
        popupType: DocDbPopupTypeE,
        params: PopupTriggeredParams,
        showTriggerSubject: Subject<PopupTriggeredParams>,
        hideTriggerSubject: Subject<void>,
        subject: Subject<DocDbPopupContextI>,
        propFilter: DocDbPropertyTypeFilterI,
    ) {
        assert(params.objectKey != null, "objectKey is null");

        // Load the data XXXms before showing the popup, if we can.
        const loadDelay =
            params.options.popupDelayMs < this.DATA_LOAD_LEAD_TIME_MS
                ? params.options.popupDelayMs
                : params.options.popupDelayMs - this.DATA_LOAD_LEAD_TIME_MS;

        let loadCancelled = false;

        const loadTimeoutHandle = setTimeout(() => {
            // FIXME: This doesn't work because all the data is under pofDiagram
            // this.docDbService.getObjects(params.modelSetKey, [params.objectKey])
            this.docDbService
                .getObjects("pofDiagram", [params.objectKey])
                .then((docs: DocumentResultI) => {
                    if (loadCancelled) return;

                    const apiHook: DocDbPopupContextI = {
                        popupType: popupType,
                        key: params.objectKey,
                        document: null,
                        modelSetKey: params.modelSetKey,
                        triggeredByPlugin: params.triggeredByPlugin,
                        options: params.options,
                        addAction: (item: DocDbPopupActionI) => {
                            params.actions = this.sortActions([
                                ...params.actions,
                                item,
                            ]);
                        },
                        addDetails: (items: DocDbPopupDetailI[]) => {
                            params.details = this.sortDetails([
                                ...params.details,
                                ...items,
                            ]);
                        },
                    };

                    const doc = docs[params.objectKey];
                    if (doc != null) {
                        apiHook.document = doc;
                        const docProps =
                            this.docDbService.getNiceOrderedProperties(
                                doc,
                                propFilter,
                            );
                        params.details = [...params.details, ...docProps];
                    }

                    // Tell any observers that we're popping up
                    // Give them a chance to add their items
                    subject.next(apiHook);
                });
        }, loadDelay);

        const popupTimeoutHandle = setTimeout(
            () => showTriggerSubject.next(params),
            params.options.popupDelayMs,
        );

        hideTriggerSubject.pipe(first()).subscribe(() => {
            loadCancelled = true;
            clearTimeout(popupTimeoutHandle);
            clearTimeout(loadTimeoutHandle);
        });
    }

    private sortActions(actions: DocDbPopupActionI[]): DocDbPopupActionI[] {
        actions = sortText(actions, (action) => {
            return action.name != null
                ? action.name
                : action.tooltip != null
                ? action.tooltip
                : "";
        });
        for (const action of actions) {
            action.children = this.sortActions(action.children || []);
        }
        return actions;
    }

    private sortDetails(details: DocDbPopupDetailI[]): DocDbPopupDetailI[] {
        return details.sort((a, b) => {
            const ao = a.order || 0;
            const bo = b.order || 0;
            if (ao != bo) return ao < bo ? -1 : 1;

            const an = a.title || "";
            const bn = b.title || "";

            if (an != bn) return an < bn ? -1 : 1;

            const av = a.value || "";
            const bv = b.value || "";

            if (av != bv) return av < bv ? -1 : 1;

            return 0;
        });
    }
}
