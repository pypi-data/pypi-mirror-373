import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditInternalUserComponent } from "./components/edit-internal-user/edit-internal-user.component";
import { EditInternalGroupComponent } from "./components/edit-internal-group/edit-internal-group.component";
import { EditSettingComponent } from "./components/edit-setting/edit-setting.component";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzSelectModule } from "ng-zorro-antd/select";
import { NzPopconfirmModule } from "ng-zorro-antd/popconfirm";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzSpaceModule } from "ng-zorro-antd/space";
import { NzTagModule } from "ng-zorro-antd/tag";
import { HttpClientModule } from "@angular/common/http";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
import { CoreUserPageComponent } from "./components/core-user-page/core-user-page.component";
import {
    userActionProcessorName,
    userFilt,
    userObservableName,
    userTupleOfflineServiceName,
} from "@peek/peek_core_user/_private";

import { ManageLoggedInUserComponent } from "./components/logged-in-user/logged-in-user.component";
import { NzStatisticModule } from "ng-zorro-antd/statistic";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { EditLdapSettingComponent } from "./components/edit-ldap-setting/edit-ldap-setting.component";
import { EditOtpSettingComponent } from "./components/edit-otp/edit.component";
import { NzModalModule, NzModalService } from "ng-zorro-antd/modal";

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(userObservableName, userFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(userActionProcessorName, userFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(userTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: CoreUserPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        // Ng-Zorro-Antd Modules
        NzInputNumberModule,
        NzTabsModule,
        NzStatisticModule,
        NzSwitchModule,
        NzButtonModule,
        NzIconModule,
        NzInputModule,
        NzFormModule,
        NzTableModule,
        NzSelectModule,
        NzPopconfirmModule,
        NzCardModule,
        NzDividerModule,
        NzSpaceModule,
        NzTagModule,
        NzModalModule,
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
        CoreUserPageComponent,
        ManageLoggedInUserComponent,
        EditInternalUserComponent,
        EditInternalGroupComponent,
        EditSettingComponent,
        EditLdapSettingComponent,
        EditOtpSettingComponent,
    ],
})
export class UserModule {}
