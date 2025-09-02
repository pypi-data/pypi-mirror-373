import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import {
    DocumentResultI,
    PrivateDocumentLoaderService,
} from "./_private/document-loader";
import { DocumentTuple } from "./DocumentTuple";
import { DocDbTupleService } from "./_private";
import { DocDbPropertyTuple } from "./DocDbPropertyTuple";

export interface DocPropT {
    title: string;
    value: string;
    order: number;
    showInHeader: boolean;
}

export interface DocDbPropertyTypeFilterI {
    (propType: DocDbPropertyTuple): boolean;
}

// ----------------------------------------------------------------------------
/** LocationIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey locations based on the index.
 *
 */
@Injectable()
export class DocDbService extends NgLifeCycleEvents {
    propertiesByName: { [key: string]: DocDbPropertyTuple } = {};

    constructor(
        private documentLoader: PrivateDocumentLoaderService,
        private tupleService: DocDbTupleService,
    ) {
        super();

        let propTs = new TupleSelector(DocDbPropertyTuple.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(propTs)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: DocDbPropertyTuple[]) => {
                this.propertiesByName = {};

                for (let item of tuples) {
                    let propKey = this._makePropKey(item.modelSetId, item.name);
                    this.propertiesByName[propKey] = item;
                }
            });
    }

    /** Get Locations
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getObjects(modelSetKey: string, keys: string[]): Promise<DocumentResultI> {
        return this.documentLoader.getDocuments(modelSetKey, keys);
    }

    getNiceOrderedProperties(
        doc: DocumentTuple,
        filter: DocDbPropertyTypeFilterI | null = null,
    ): DocPropT[] {
        let props: DocPropT[] = [];

        for (let name of Object.keys(doc.document)) {
            let propKey = this._makePropKey(doc.modelSet.id, name);
            let prop =
                this.propertiesByName[propKey] || new DocDbPropertyTuple();
            if (filter != null && !filter(prop)) continue;
            props.push({
                title: prop.title,
                value: doc.document[name],
                order: prop.order,
                showInHeader: prop.showInHeader,
            });
        }
        props.sort((a, b) => a.order - b.order);

        return props;
    }

    private _makePropKey(modelSetId: number, name: string): string {
        return `${modelSetId}.${name.toLowerCase()}`;
    }
}
