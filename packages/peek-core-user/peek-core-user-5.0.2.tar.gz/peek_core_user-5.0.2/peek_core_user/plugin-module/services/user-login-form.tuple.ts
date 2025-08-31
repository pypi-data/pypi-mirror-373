import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private";
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from "@angular/forms";
import { UserLoginStepFormEnum } from "@peek/peek_core_user/_private/tuples/UserLoginStepFormEnum";
import { CryptoUtil, UserLoginAction } from "@peek/peek_core_user";

export type UserLoginFormT = FormGroup<{
    userName: FormControl<string>;
    password: FormControl<string>;
    vehicleId: FormControl<string>;
}>;

@addTupleType
export class UserLoginFormTuple extends Tuple {
    static readonly tupleName = userTuplePrefix + "UserLoginFormTuple";

    userName: string;
    password: string;
    vehicleId: string | null = null;

    constructor() {
        super();
        this.createFormGroup();
    }

    async toUserLoginAction(
        deviceToken: string,
        acceptedWarningKeys: string[],
    ): Promise<UserLoginAction> {
        const tupleAction = new UserLoginAction();

        tupleAction.userName = this.userName;
        tupleAction.vehicleId = this.vehicleId;
        tupleAction.deviceToken = deviceToken;

        tupleAction.password = await CryptoUtil.encryptAES256GCM(
            this.password,
            tupleAction.uuid,
        );

        tupleAction.acceptedWarningKeys = acceptedWarningKeys;

        return tupleAction;
    }

    validate(userLoginStepFormEnum: number): boolean {
        const formGroup = this.createFormGroup();
        this.updateFormValidatorsForStep(userLoginStepFormEnum, formGroup);
        return this.doValidateForm(formGroup);
    }

    private createFormGroup(): UserLoginFormT {
        const fb = new FormBuilder();

        return fb.group({
            // controlName: [defaultValue, optional validators in array]
            userName: [this.userName],
            password: [this.password],
            vehicleId: [this.vehicleId],
        }) as UserLoginFormT;
    }

    private updateFormValidatorsForStep(
        userLoginStepFormEnum: number,
        formGroup: UserLoginFormT,
    ) {
        // change validators for the step passed in
        const controls = formGroup.controls;

        formGroup.clearValidators();
        formGroup.clearAsyncValidators();

        // office login
        if (userLoginStepFormEnum === UserLoginStepFormEnum.OFFICE_FORM) {
            controls.userName.setValidators([Validators.required]);
            controls.password.setValidators([Validators.required]);
            return;
        }

        // field login - step select user
        if (
            userLoginStepFormEnum >=
            UserLoginStepFormEnum.FIELD_STEP_SELECT_USER_FORM
        ) {
            controls.userName.setValidators([Validators.required]);
        }

        // field login - step verify (otp or password)
        if (
            userLoginStepFormEnum >=
                UserLoginStepFormEnum.FIELD_STEP_VERIFY_OTP_FORM ||
            userLoginStepFormEnum >=
                UserLoginStepFormEnum.FIELD_STEP_VERIFY_PASSWORD_FORM
        ) {
            controls.password.setValidators([Validators.required]);
        }

        // field login - step vehicle
        if (
            userLoginStepFormEnum >=
            UserLoginStepFormEnum.FIELD_STEP_VEHICLE_FORM
        ) {
            controls.vehicleId.setValidators([Validators.required]);
        }
    }

    private doValidateForm(formGroup: UserLoginFormT): boolean {
        if (formGroup == null) {
            return false;
        }

        if (formGroup.valid) {
            return true;
        }

        Object.values(formGroup.controls).forEach((control) => {
            if (control.invalid) {
                control.markAsDirty();
                control.updateValueAndValidity({
                    onlySelf: true,
                });
            }
        });
        return false;
    }
}
