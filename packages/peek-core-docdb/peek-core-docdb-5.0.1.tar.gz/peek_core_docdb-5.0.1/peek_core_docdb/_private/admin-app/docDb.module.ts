import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { ViewDocumentComponent } from "./components/view-document/view-document.component";
import { EditSettingComponent } from "./components/edit-setting/edit-setting.component";
import { StatusComponent } from "./components/status/status.component";
import { DocdbPageComponent } from "./components/docdb-page/docdb-page.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";

import {
    docDbActionProcessorName,
    docDbFilt,
    docDbObservableName,
    docDbTupleOfflineServiceName,
} from "@peek/peek_core_docdb/_private";
import { EditPropertyComponent } from "./components/edit-property/edit-property.component";
import { EditDocumentTypeComponent } from "./components/edit-object-type/edit-object-type.component";

// ng-zorro-antd imports
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzSpaceModule } from "ng-zorro-antd/space";
import { NzTypographyModule } from "ng-zorro-antd/typography";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(docDbActionProcessorName, docDbFilt);
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(docDbObservableName, docDbFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(docDbTupleOfflineServiceName);
}

export const pluginRoutes: Routes = [
    {
        path: "",
        component: DocdbPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        // ng-zorro-antd modules
        NzButtonModule,
        NzTableModule,
        NzTabsModule,
        NzInputModule,
        NzSwitchModule,
        NzCardModule,
        NzEmptyModule,
        NzGridModule,
        NzFormModule,
        NzSpaceModule,
        NzTypographyModule,
        NzDividerModule,
        NzInputNumberModule,
        NzTagModule,
        NzDescriptionsModule,
    ],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [
        DocdbPageComponent,
        ViewDocumentComponent,
        EditSettingComponent,
        StatusComponent,
        EditPropertyComponent,
        EditDocumentTypeComponent,
    ],
})
export class DocDbModule {}
