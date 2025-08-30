import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject, interval, Subject } from "rxjs";
import { filter, takeUntil } from "rxjs/operators";
import { UserLoginStepWizardService, UserService } from "@peek/peek_core_user";
import {
    UserLoginAuthMethodResponseTuple,
    UserLoginOtpAction,
    UserLoginOtpResponseTuple,
} from "@peek/peek_core_user/tuples";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { LoginStep } from "@peek/peek_core_user/_private/services/login-step-wizard.service";

interface OtpOption {
    label: string;
    value: string;
    disabled: boolean;
}

@Component({
    selector: "peek-core-user-field-login-step-authenticate",
    templateUrl: "./field-login-step-authenticate.component.html",
    styleUrls: ["./field-login-step-authenticate.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldLoginStepAuthenticateComponent extends NgLifeCycleEvents {
    readonly AUTH_METHODS = {
        ONE_TIME_PASSCODE:
            UserLoginAuthMethodResponseTuple.AUTH_METHOD_ONE_TIME_PASSCODE,
        PASSWORD: UserLoginAuthMethodResponseTuple.AUTH_METHOD_PASSWORD,
    };

    readonly OTP_REQUEST_BUTTON_TEXT = "Get Passcode";
    public readonly errors$ = new BehaviorSubject<string[]>([]);
    public readonly warnings$ = new BehaviorSubject<string[]>([]);

    isPasswordVisible = false;
    readonly userSelectedTokens$ = new BehaviorSubject<string[]>([]);
    readonly otpOptions$ = new BehaviorSubject<OtpOption[]>([]);
    readonly isOtpRequestButtonDisabled$ = new BehaviorSubject<boolean>(false);
    readonly otpRequestButtonText$ = new BehaviorSubject<string>(
        this.OTP_REQUEST_BUTTON_TEXT,
    );

    readonly isAuthenticating$: BehaviorSubject<boolean>;

    // Service observables
    readonly userLoginAuthMethodResponseTuple$: BehaviorSubject<UserLoginAuthMethodResponseTuple>;

    // Add authMethod property
    authMethod: UserLoginAuthMethodResponseTuple;

    private unsubTimeoutSubject = new Subject<void>();

    constructor(
        private userLoginWizardService: UserLoginStepWizardService,
        private balloonMsg: BalloonMsgService,
        private userService: UserService,
    ) {
        super();

        // Service observables
        this.userLoginAuthMethodResponseTuple$ =
            this.userLoginWizardService.userLoginAuthMethodResponseTuple$;

        this.isAuthenticating$ = this.userLoginWizardService.isAuthenticating$;

        // Subscribe to auth method changes
        this.userLoginAuthMethodResponseTuple$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((method) => {
                this.authMethod = method;
            });

        // Subscribe to wizard service changes
        this.userLoginWizardService.errors$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((errors) => this.errors$.next(errors));

        this.userLoginWizardService.warnings$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((warnings) => this.warnings$.next(warnings));

        this.userLoginWizardService.loginStepIndex$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((index) => index === LoginStep.STEP_AUTHENTICATE))
            .subscribe(async () => {
                await this.requestOtp();
            });
    }

    set userSelectedTokens(otp: string[]) {
        this.userSelectedTokens$.next(otp);
    }

    get userSelectedTokens(): string[] {
        return this.userSelectedTokens$.getValue();
    }

    set otpOptions(options: OtpOption[]) {
        this.otpOptions$.next(options);
    }

    get otpOptions(): OtpOption[] {
        return this.otpOptions$.getValue();
    }

    set isOtpRequestButtonDisabled(disabled: boolean) {
        this.isOtpRequestButtonDisabled$.next(disabled);
    }

    set otpRequestButtonText(text: string) {
        this.otpRequestButtonText$.next(text);
    }

    async requestOtp(): Promise<void> {
        const tupleAction = new UserLoginOtpAction();

        if (
            this.authMethod.authMethod ===
            UserLoginAuthMethodResponseTuple.AUTH_METHOD_NONE
        ) {
            return;
        }

        tupleAction.userName = this.authMethod.userName;

        try {
            const response = await this.userService.requestOtp(tupleAction);

            if (
                response.otpRequestStatus !==
                UserLoginOtpResponseTuple.STATUS_OTP_REQUEST_ACCEPTED
            ) {
                return;
            }

            this.otpOptions = response.otpOptions.map((opt) => ({
                label: opt,
                value: opt,
                disabled: this.userSelectedTokens.includes(opt),
            }));

            const allUsers = this.userLoginWizardService.allUsers;
            const user = allUsers.find(
                (u) => u.userName === tupleAction.userName,
            );

            if (user?.mobile) {
                const maskedMobile = this.maskPhoneNumber(user.mobile);
                this.showOtpSentMessage(maskedMobile);
                this.startOtpCooldown(response.otpValidTo);
            }
        } catch (err) {
            const errorMessage = String(err);
            if (errorMessage.startsWith("Timed out")) {
                this.balloonMsg.showError(
                    "Cannot determine verification method for login. " +
                        "The server didn't respond.",
                );
                return;
            }
            if (errorMessage.length === 0) {
                this.balloonMsg.showError(
                    "An error occurred when determining your " +
                        "verification method for login.",
                );
                return;
            }
            this.balloonMsg.showError(errorMessage);
        }
    }

    resetSelection(): void {
        this.userSelectedTokens = [];
        this.userLoginWizardService.updateUserLoginFormPassword("");

        // Reset all options to enabled
        this.otpOptions = this.otpOptions.map((opt) => ({
            ...opt,
            disabled: false,
        }));
    }

    onOtpCardClick(value: string): void {
        const currentOtp = this.userSelectedTokens;

        // Create new array and sort immediately
        const userSelectedTokens = currentOtp.includes(value)
            ? currentOtp.filter((word) => word !== value)
            : [...currentOtp, value];

        this.userSelectedTokens = userSelectedTokens;
        this.userLoginWizardService.updateUserLoginFormPassword(
            userSelectedTokens.join("_"),
        );

        // Update disabled state of options
        this.otpOptions = this.otpOptions.map((opt) => ({
            ...opt,
            disabled: userSelectedTokens.includes(opt.value),
        }));
    }

    get password(): string {
        return this.userLoginWizardService.userLoginFormTuple.password;
    }

    onPasswordModelChange(password: string): void {
        this.userLoginWizardService.updateUserLoginFormPassword(password);
    }

    private maskPhoneNumber(mobile: string): string {
        const lastFourDigits = mobile.slice(-4);
        const maskedDigits = mobile.slice(0, -4).replace(/\d/g, "*");
        return `${maskedDigits}${lastFourDigits}`;
    }

    private showOtpSentMessage(maskedMobile: string): void {
        this.balloonMsg.showSuccess(
            `One-time password sent to ${maskedMobile}`,
        );
    }

    private startOtpCooldown(otpValidTo: Date): void {
        this.isOtpRequestButtonDisabled = true;

        let remainingSeconds = Math.floor(
            Math.abs(otpValidTo.getTime() - Date.now()) / 1000,
        );
        this.updateButtonText(remainingSeconds);

        this.unsubTimeoutSubject.next();
        interval(1000)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(takeUntil(this.unsubTimeoutSubject))
            .subscribe(() => {
                remainingSeconds--;
                this.updateButtonText(remainingSeconds);

                if (remainingSeconds <= 0) {
                    this.otpRequestButtonText = this.OTP_REQUEST_BUTTON_TEXT;
                    this.isOtpRequestButtonDisabled = false;
                    this.unsubTimeoutSubject.next();
                }
            });
    }

    private updateButtonText(remainingSeconds: number): void {
        this.otpRequestButtonText = `${this.OTP_REQUEST_BUTTON_TEXT} (${remainingSeconds}s)`;
    }

    async gotoNextLoginStepIndex() {
        await this.userLoginWizardService.gotoNextLoginStepIndex();
    }
}
