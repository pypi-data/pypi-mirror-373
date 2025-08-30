import { BehaviorSubject } from "rxjs";
import { ChangeDetectionStrategy, Component, ElementRef } from "@angular/core";
import {
    DocDbPopupActionI,
    DocDbPopupClosedReasonE,
    DocDbPopupDetailI,
    DocDbPopupTypeE,
} from "@peek/peek_core_docdb";
import {
    PopupTriggeredParams,
    PrivateDocDbPopupService,
} from "@peek/peek_core_docdb/_private/services/PrivateDocDbPopupService";
import { DOCDB_POPUP } from "@peek/peek_core_docdb/constants";

type Popup = "tooltip" | "summary" | "detail";

// This is a root/global component
@Component({
    selector: "popup-component",
    templateUrl: "popup.component.html",
    styleUrls: ["popup.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PopupComponent {
    DOCDB_POPUP = DOCDB_POPUP;

    params$ = new BehaviorSubject<PopupTriggeredParams>(null);
    modalAction$ = new BehaviorSubject<DocDbPopupActionI>(null);
    currentPopup$ = new BehaviorSubject<Popup>(null);

    left$ = new BehaviorSubject<number>(0);
    right$ = new BehaviorSubject<number>(0);
    top$ = new BehaviorSubject<number>(0);
    bottom$ = new BehaviorSubject<number>(0);

    constructor(
        private popupService: PrivateDocDbPopupService,
        private element: ElementRef,
    ) {
        this.popupService.showTooltipPopupSubject.subscribe((val) => {
            this.openPopup(val);
            this.currentPopup = "tooltip";
            document.body.appendChild(this.element.nativeElement);
        });
        this.popupService.showSummaryPopupSubject.subscribe((val) => {
            this.openPopup(val);
            this.currentPopup = "summary";
            document.body.appendChild(this.element.nativeElement);
        });
        this.popupService.showDetailPopupSubject.subscribe((val) => {
            this.openPopup(val);
            this.currentPopup = "detail";
            document.body.appendChild(this.element.nativeElement);
        });

        this.popupService.hideTooltipPopupSubject.subscribe(() =>
            this.closePopup(),
        );
        this.popupService.hideSummaryPopupSubject.subscribe(() =>
            this.closePopup(),
        );
        this.popupService.hideDetailPopupSubject.subscribe(() =>
            this.closePopup(),
        );
    }

    get params() {
        return this.params$.getValue();
    }

    set params(value) {
        this.params$.next(value);
    }

    get modalAction() {
        return this.modalAction$.getValue();
    }

    set modalAction(value) {
        this.modalAction$.next(value);
    }

    get currentPopup() {
        return this.currentPopup$.getValue();
    }

    set currentPopup(value) {
        this.currentPopup$.next(value);
    }

    get left() {
        return this.left$.getValue();
    }

    set left(value) {
        this.left$.next(value);
    }

    get right() {
        return this.right$.getValue();
    }

    set right(value) {
        this.right$.next(value);
    }

    get top() {
        return this.top$.getValue();
    }

    set top(value) {
        this.top$.next(value);
    }

    get bottom() {
        return this.bottom$.getValue();
    }

    set bottom(value) {
        this.bottom$.next(value);
    }

    closePopup(): void {
        if (!this.params) {
            return;
        }

        this.params = null;
        this.popupService.hidePopupWithReason(
            DocDbPopupTypeE.summaryPopup,
            DocDbPopupClosedReasonE.closedByApiCall,
        );
    }

    showDetailsPopup(): void {
        const params = this.params;

        this.popupService.hidePopupWithReason(
            DocDbPopupTypeE.summaryPopup,
            DocDbPopupClosedReasonE.userDismissedPopup,
        );

        this.popupService.showPopup(
            true,
            DocDbPopupTypeE.detailPopup,
            params.triggeredByPlugin,
            this.makeMouseEvent(params),
            params.modelSetKey,
            params.objectKey,
            params.options,
        );
    }

    headerDetails(details: DocDbPopupDetailI[]): string {
        return details
            .filter((d) => d.showInHeader)
            .map((d) => d.value)
            .join(", ");
    }

    bodyDetails(details: DocDbPopupDetailI[]): DocDbPopupDetailI[] {
        return details.filter((d) => !d.showInHeader);
    }

    modalActionClicked(item: DocDbPopupActionI): void {
        this.actionClicked(item);
        this.closeModal();
    }

    actionClicked(item: DocDbPopupActionI): void {
        if (item.children?.length) {
            this.modalAction = item;
        } else {
            item.callback();
        }
        this.closePopup();
    }

    modalName(): string {
        if (this.modalAction == null) {
            return null;
        }

        return this.modalAction.name || this.modalAction.tooltip;
    }

    closeModal(): void {
        this.modalAction = null;
    }

    modalChildActions(): DocDbPopupActionI[] {
        return this.modalAction == null ? [] : this.modalAction.children;
    }

    openPopup(params: any) {
        this.params = params;

        if (params.position.changedTouches) {
            this.setHorizontal(params.position.changedTouches[0].clientX);
            this.setVertical(params.position.changedTouches[0].clientY);
        } else {
            this.setHorizontal(params.position.x);
            this.setVertical(params.position.y);
        }
    }

    setHorizontal(x: number): void {
        const width = window.innerWidth;

        if (x > width / 2) {
            this.right = Math.round(width - x);
            this.left = null;
        } else {
            this.left = Math.round(x);
            this.right = null;
        }
    }

    setVertical(y: number): void {
        const height = window.innerHeight;

        if (y > height / 2) {
            this.bottom = Math.round(height - y);
            this.top = null;
        } else {
            this.top = Math.round(y);
            this.bottom = null;
        }
    }

    private makeMouseEvent(params) {
        let x = 0;
        let y = 0;

        if (params.position.changedTouches) {
            x = params.position.changedTouches[0].clientX;
            y = params.position.changedTouches[0].clientY;
        } else {
            x = params.position.x;
            y = params.position.y;
        }

        return <any>{
            preventDefault: () => false,
            x,
            y,
        };
    }
}
