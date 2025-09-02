import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
} from "@synerty/vortexjs";

import {
    coreEmailActionProcessorName,
    coreEmailFilt,
    coreEmailObservableName,
} from "./PluginNames";

import { CoreEmailAdminComponent } from "./components/core-email-page/core-email-admin.component";
import { AdminSettingListComponent } from "./components/setting-list/admin-setting-list.component";

// Ant Design Imports
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzTypographyModule } from "ng-zorro-antd/typography";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzSpinModule } from "ng-zorro-antd/spin";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzCardModule } from "ng-zorro-antd/card";

export const pluginRoutes: Routes = [
    {
        path: "",
        component: CoreEmailAdminComponent,
    },
];

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        coreEmailObservableName,
        coreEmailFilt,
    );
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        coreEmailActionProcessorName,
        coreEmailFilt,
    );
}

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        RouterModule.forChild(pluginRoutes),
        // Ant Design Modules
        NzTabsModule,
        NzButtonModule,
        NzInputModule,
        NzTableModule,
        NzTypographyModule,
        NzFormModule,
        NzGridModule,
        NzSwitchModule,
        NzSpinModule,
        NzInputNumberModule,
        NzCardModule,
    ],
    exports: [],
    providers: [
        TupleDataObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
    ],
    declarations: [CoreEmailAdminComponent, AdminSettingListComponent],
})
export class CoreEmailAdminModule {}
