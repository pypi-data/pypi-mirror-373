import { Observable } from "rxjs";
import { DocumentTuple } from "@peek/peek_core_docdb";

/** Object Action Item Callback Interface
 *
 * This interface defines a callback that will be called when the action item is clicked
 * but the user.
 *
 */
export interface DocDbPopupActionCallbackI {
    (): void;
}

/** Object Action Item Interface
 *
 * This interface represents a hierarchy of a action items that will be presented to
 * a user when the popup appears for a diagram item click/tap.
 *
 * NOTE: Don't specify both children and a callback, as the click/tap event will
 * navigate to the child action options.
 *
 */
export interface DocDbPopupActionI {
    name: string;
    tooltip: string | null;
    icon: string | null;
    callback: DocDbPopupActionCallbackI | null;
    children: DocDbPopupActionI[];
    closeOnCallback?: boolean;
}

/** Object Item Detail Interface
 *
 * This interface represents some some detail that another plugin wants to appear
 * on the diagram item select popup.
 *
 */
export interface DocDbPopupDetailI {
    title: string;
    value: string; // TODO: Add support for tables, etc.
    order: number;
    showInHeader: boolean;
}

/** Object Trigger Position
 *
 * This interface describes where on the screen the popup will appear.
 *
 */
export interface ObjectTriggerPositionI {
    x: number;
    y: number;
}

/** Object Popup Type
 *
 */
export enum DocDbPopupTypeE {
    tooltipPopup,
    summaryPopup,
    detailPopup,
}

export enum DocDbPopupClosedReasonE {
    userClickedAction,
    userDismissedPopup,
    closedByApiCall,
    other,
}

/** Object Trigger Options
 *
 * This interface describes additional options for triggering a popup.
 *
 */
export interface ObjectTriggerOptionsI {
    triggeredForContext?: string;
    triggeredFromPosition?: { x: number; y: number };
    popupDelayMs?: number;
}

export interface DocDbPopupContextI {
    /** The type of the popup being displayed */
    popupType: DocDbPopupTypeE;

    /** The is the key assigned to the Object item when it was imported */
    key: string;

    /** The is the document from DocDB */
    document: DocumentTuple | null;

    /** The key of the model set that this Object belongs to */
    modelSetKey: string;

    /** The name of the plugin that triggered the popup */
    triggeredByPlugin: string;

    /** The additional options that the popup was triggered with  */
    options: ObjectTriggerOptionsI;

    /** Add Action Item
     *
     * @param action: A action item, or the root action item of a hierarchy of items to add.
     */
    addAction(action: DocDbPopupActionI): void;

    /** Add Detail Items
     *
     * @param details: A list of details object on the popup.
     */
    addDetails(details: DocDbPopupDetailI[]): void;
}

/** Object Item Popup Service
 *
 * This service provides support for other plugins to integrate with the diagram.
 *
 * When a selectable item on the diagram is clicked/tapped, an observable event will
 * be fired with a context class, allowing the other plugin to add actions and details to the popup.
 */
export abstract class DocDbPopupService {
    constructor() {}

    /** Show Object Popup
     *
     * Use this method to trigger a popup with the objects respective details
     *
     */
    abstract showPopup(
        popupClicked: boolean,
        popupType: DocDbPopupTypeE,
        triggeredByPlugin: string,
        position: ObjectTriggerPositionI,
        modelSetKey: string,
        objectKey: string,
        options?: ObjectTriggerOptionsI,
    ): void;

    abstract hideAllPopups(): void;

    /** Hide Object Popup
     *
     * Use this method to trigger a tooltip with the objects respective details
     *
     */
    abstract hidePopup(popupType: DocDbPopupTypeE): void;

    /** Hide Hover Popup
     *
     * Use this method to hide any popup opened via hover
     *
     */
    abstract hideHoverPopup(): void;

    /** Object Popup Observable
     *
     * This method returns an observable that is fired with the context when ever a
     * popup is triggered.
     */
    abstract popupObservable(
        popupType: DocDbPopupTypeE,
    ): Observable<DocDbPopupContextI>;

    /** Object Popup Closed Observable
     *
     * This method returns an observable that is fired when a popup is closed.
     */
    abstract popupClosedObservable(
        popupType: DocDbPopupTypeE,
    ): Observable<DocDbPopupClosedReasonE>;
}
