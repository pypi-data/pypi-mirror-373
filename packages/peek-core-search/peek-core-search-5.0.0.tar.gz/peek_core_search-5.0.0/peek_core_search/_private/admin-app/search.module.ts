import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { EditPropertyComponent } from "./components/edit-property-table/edit.component";
import { EditObjectTypeComponent } from "./components/edit-object-type-table/edit.component";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { StatusComponent } from "./components/status-component/status.component";
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
    searchActionProcessorName,
    searchFilt,
    searchObservableName,
    searchTupleOfflineServiceName,
} from "@peek/peek_core_search/_private";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { EditExcludeSearchTermComponent } from "./components/edit-exclude-search-term-table/edit.component";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzCheckboxModule } from "ng-zorro-antd/checkbox";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { SearchPageComponent } from "./components/search-page/search-page.component";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { NzEmptyModule } from "ng-zorro-antd/empty";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        searchActionProcessorName,
        searchFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(searchObservableName, searchFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(searchTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: SearchPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzSwitchModule,
        NzTableModule,
        NzButtonModule,
        NzCardModule,
        NzTabsModule,
        NzFormModule,
        NzInputModule,
        NzCheckboxModule,
        NzIconModule,
        NzTagModule,
        NzDividerModule,
        NzInputNumberModule,
        NzDescriptionsModule,
        NzEmptyModule,
    ],
    exports: [],
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
        SearchPageComponent,
        EditPropertyComponent,
        EditSettingComponent,
        EditObjectTypeComponent,
        StatusComponent,
        EditExcludeSearchTermComponent,
    ],
})
export class SearchModule {}
