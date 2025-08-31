import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
} from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { UserLoginStepWizardService } from "@peek/peek_core_user";
import { BehaviorSubject } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { LoginStep } from "@peek/peek_core_user/_private/services/login-step-wizard.service";

@Component({
    selector: "peek-core-user-field-login",
    templateUrl: "./field-login.component.html",
    styleUrls: ["./field-login.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldLoginComponent
    extends NgLifeCycleEvents
    implements OnInit, OnDestroy
{
    readonly LoginStep = LoginStep;

    // Public observables
    readonly loginStepIndex$: BehaviorSubject<number>;

    constructor(
        headerService: HeaderService,
        protected userLoginWizardService: UserLoginStepWizardService,
    ) {
        super();
        headerService.setTitle("User Login");

        this.loginStepIndex$ = this.userLoginWizardService.loginStepIndex$;
    }

    async gotoPreviousLoginStepIndex() {
        this.userLoginWizardService.gotoPreviousLoginStepIndex();
    }
}
