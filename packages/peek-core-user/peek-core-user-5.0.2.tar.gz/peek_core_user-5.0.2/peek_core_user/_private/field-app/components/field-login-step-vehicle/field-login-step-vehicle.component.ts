import { ChangeDetectionStrategy, Component } from "@angular/core";
import { UserLoginStepWizardService } from "@peek/peek_core_user";
import { UserLoginFormTuple } from "@peek/peek_core_user/services/user-login-form.tuple";
import { BehaviorSubject } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

@Component({
    selector: "peek-core-user-field-login-step-vehicle",
    templateUrl: "./field-login-step-vehicle.component.html",
    styleUrls: ["./field-login-step-vehicle.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldLoginStepVehicleComponent extends NgLifeCycleEvents {
    readonly userLoginFormTuple: UserLoginFormTuple;

    // BehaviorSubjects
    public readonly vehicleId$ = new BehaviorSubject<string>("");

    constructor(
        private userLoginWizardService: UserLoginStepWizardService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();
        this.userLoginFormTuple = userLoginWizardService.userLoginFormTuple;
    }

    override ngOnInit() {
        // Subscribe to form tuple changes
        this.vehicleId$.next(this.userLoginFormTuple.vehicleId || "");
    }

    // Setters and getters
    set vehicleId(value: string) {
        value = value.trim();
        this.vehicleId$.next(value);
        this.userLoginFormTuple.vehicleId = value;
    }

    get vehicleId(): string {
        return this.vehicleId$.getValue();
    }

    async handleOk(): Promise<void> {
        // Validate that vehicle ID is required when the input should be shown
        if (!this.vehicleId) {
            this.balloonMsg.showWarning("Please enter a valid vehicle ID");
            return;
        }

        await this.userLoginWizardService.gotoNextLoginStepIndex();
    }
}
