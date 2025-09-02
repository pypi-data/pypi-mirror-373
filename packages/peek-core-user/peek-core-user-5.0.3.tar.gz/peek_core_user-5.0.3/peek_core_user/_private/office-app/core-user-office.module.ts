import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { pluginRoutes } from "./core-user-office.routes";
import { HttpClientModule } from "@angular/common/http";
import { OfficeLoginComponent } from "./components/office-login/office-login.component";
import { OfficeLogoutComponent } from "./components/office-logout/office-logout.component";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzLayoutModule } from "ng-zorro-antd/layout";
import { NzAvatarModule } from "ng-zorro-antd/avatar";
import { NzTypographyModule } from "ng-zorro-antd/typography";
import { UserLoginStepWizardService } from "@peek/peek_core_user";

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        HttpClientModule,
        FormsModule,
        NzIconModule,
        NzAlertModule,
        NzCardModule,
        NzButtonModule,
        NzFormModule,
        NzInputModule,
        NzLayoutModule,
        NzAvatarModule,
        NzTypographyModule,
    ],
    declarations: [OfficeLoginComponent, OfficeLogoutComponent],
    providers: [UserLoginStepWizardService],
})
export class CoreUserOfficeModule {}
