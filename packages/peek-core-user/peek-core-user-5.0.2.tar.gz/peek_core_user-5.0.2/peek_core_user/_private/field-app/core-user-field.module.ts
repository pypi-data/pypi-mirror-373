import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { RouterModule } from "@angular/router";
import { pluginRoutes } from "./core-user-field.routes";
import { HttpClientModule } from "@angular/common/http";
import { FieldLoginComponent } from "./components/field-login/field-login.component";
import { FieldLoginStepUserComponent } from "./components/field-login-step-user/field-login-step-user.component";
import { FieldLoginStepVehicleComponent } from "./components/field-login-step-vehicle/field-login-step-vehicle.component";
import { FieldLogoutComponent } from "./components/field-logout/field-logout.component";
import { FieldLoginStepAuthenticateComponent } from "./components/field-login-step-authenticate/field-login-step-authenticate.component";
import { NzStepsModule } from "ng-zorro-antd/steps";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzSelectModule } from "ng-zorro-antd/select";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzListModule } from "ng-zorro-antd/list";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzAvatarModule } from "ng-zorro-antd/avatar";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { UserLoginStepWizardService } from "@peek/peek_core_user";
import { FieldLoginSimpleComponent } from "./components/field-login-simple/field-login-simple.component";
import { NzTypographyModule } from "ng-zorro-antd/typography";

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        HttpClientModule,
        NzIconModule,
        NzStepsModule,
        NzButtonModule,
        NzSelectModule,
        NzInputModule,
        NzListModule,
        NzEmptyModule,
        NzAlertModule,
        NzFormModule,
        NzCardModule,
        NzAvatarModule,
        NzDividerModule,
        NzTypographyModule,
    ],
    declarations: [
        FieldLoginComponent,
        FieldLoginStepVehicleComponent,
        FieldLoginStepAuthenticateComponent,
        FieldLoginStepUserComponent,
        FieldLogoutComponent,
        FieldLoginSimpleComponent,
    ],
    providers: [UserLoginStepWizardService],
})
export class CoreUserFieldModule {}
