import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import { filter, map } from "rxjs/operators";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { DeviceOnlineService } from "@peek/peek_core_device/_private";
import { DeviceEnrolmentService } from "@peek/peek_core_device";
import { UserTupleService } from "@peek/peek_core_user/_private/user-tuple.service";
import { UserService } from "../../services/user.service";
import { UserLoginUiSettingTuple } from "@peek/peek_core_user/_private/tuples/UserLoginUiSettingTuple";
import {
    UserLoginAuthMethodAction,
    UserLoginAuthMethodResponseTuple,
} from "@peek/peek_core_user/tuples";
import { UserLoginFormTuple } from "../../services/user-login-form.tuple";
import { UserListItemTuple } from "@peek/peek_core_user/tuples/UserListItemTuple";

export enum LoginStep {
    STEP_SELECT_USER = 0,
    STEP_ENTER_VEHICLE = 1,
    STEP_AUTHENTICATE = 2,
}

interface ErrorState {
    errors: string[];
    warnings: string[];
    warningKeys: string[];
}

@Injectable()
export class UserLoginStepWizardService extends NgLifeCycleEvents {
    // Private BehaviorSubjects
    readonly userLoginFormTuple$ = new BehaviorSubject<UserLoginFormTuple>(
        new UserLoginFormTuple(),
    );
    private readonly errorState$ = new BehaviorSubject<ErrorState>({
        errors: [],
        warnings: [],
        warningKeys: [],
    });
    private readonly selectedUser$ =
        new BehaviorSubject<UserListItemTuple | null>(null);
    readonly userLoginAuthMethodResponseTuple$ =
        new BehaviorSubject<UserLoginAuthMethodResponseTuple>(
            new UserLoginAuthMethodResponseTuple(),
        );

    readonly loginStepIndex$ = new BehaviorSubject<LoginStep>(
        LoginStep.STEP_SELECT_USER,
    );
    readonly isAuthenticating$ = new BehaviorSubject<boolean>(false);
    readonly allUsers$ = new BehaviorSubject<UserListItemTuple[]>([]);
    readonly recentUsers$ = new BehaviorSubject<UserListItemTuple[]>([]);
    readonly lastUsers$ = new BehaviorSubject<UserListItemTuple[]>([]);
    readonly setting$ = new BehaviorSubject<UserLoginUiSettingTuple>(
        new UserLoginUiSettingTuple(),
    );

    // Observable getters
    readonly errors$ = this.errorState$.pipe(map((state) => state.errors));
    readonly warnings$ = this.errorState$.pipe(map((state) => state.warnings));

    constructor(
        private tupleService: UserTupleService,
        private userService: UserService,
        private balloonMsg: BalloonMsgService,
        private deviceOnlineService: DeviceOnlineService,
        private deviceEnrolmentService: DeviceEnrolmentService,
        private router: Router,
    ) {
        super();
        this.initializeUserSettings();
    }

    // Getters
    get userLoginFormTuple(): UserLoginFormTuple {
        return this.userLoginFormTuple$.getValue();
    }

    get errorState(): ErrorState {
        return this.errorState$.getValue();
    }

    get loginStepIndex(): LoginStep {
        return this.loginStepIndex$.getValue();
    }

    get allUsers(): UserListItemTuple[] {
        return this.allUsers$.getValue();
    }

    get setting(): UserLoginUiSettingTuple {
        return this.setting$.getValue();
    }

    get userLoginAuthMethodResponseTuple(): UserLoginAuthMethodResponseTuple {
        return this.userLoginAuthMethodResponseTuple$.getValue();
    }

    // Setters
    set userLoginFormTuple(value: UserLoginFormTuple) {
        this.userLoginFormTuple$.next(value);
    }

    set errorState(value: ErrorState) {
        this.errorState$.next(value);
    }

    set loginStepIndex(value: LoginStep) {
        this.loginStepIndex$.next(value);
    }

    set selectedUser(value: UserListItemTuple | null) {
        this.selectedUser$.next(value);
    }

    set allUsers(value: UserListItemTuple[]) {
        this.allUsers$.next(value);
    }

    set recentUsers(value: UserListItemTuple[]) {
        this.recentUsers$.next(value);
    }

    set lastUsers(value: UserListItemTuple[]) {
        this.lastUsers$.next(value);
    }

    set isAuthenticating(value: boolean) {
        this.isAuthenticating$.next(value);
    }

    set setting(value: UserLoginUiSettingTuple) {
        this.setting$.next(value);
    }

    set userLoginAuthMethodResponseTuple(
        value: UserLoginAuthMethodResponseTuple,
    ) {
        this.userLoginAuthMethodResponseTuple$.next(value);
    }

    // Public methods refactored to use getters/setters
    selectUser(user: UserListItemTuple): void {
        this.selectedUser = user;
        const currentForm = this.userLoginFormTuple;
        currentForm.userName = user.userName;
        this.userLoginFormTuple = currentForm;
    }

    unselectUser(): void {
        this.selectedUser = null;
        const currentForm = this.userLoginFormTuple;
        currentForm.userName = "";
        this.userLoginFormTuple = currentForm;
    }

    updateUserLoginFormPassword(password: string): void {
        const currentForm = this.userLoginFormTuple;
        currentForm.password = password;
        this.userLoginFormTuple = currentForm;
    }

    // Form Validation Methods
    validateFieldSelectUserForm(): boolean {
        return this.userLoginFormTuple.validate(LoginStep.STEP_SELECT_USER);
    }

    validateFieldOtpOrPasswordForm(): boolean {
        const step =
            this.userLoginAuthMethodResponseTuple.authMethod ===
            UserLoginAuthMethodResponseTuple.AUTH_METHOD_ONE_TIME_PASSCODE
                ? LoginStep.STEP_AUTHENTICATE
                : LoginStep.STEP_ENTER_VEHICLE;
        return this.userLoginFormTuple.validate(step);
    }

    validateFieldVehicleForm(): boolean {
        return this.userLoginFormTuple.validate(LoginStep.STEP_ENTER_VEHICLE);
    }

    validateOfficeForm(): boolean {
        return this.userLoginFormTuple.validate(-1);
    }

    async queryUserLoginAuthMethod(): Promise<void> {
        const action = new UserLoginAuthMethodAction();
        action.userName = this.userLoginFormTuple.userName;
        action.authForService = UserLoginAuthMethodAction.AUTH_FOR_FIELD;

        try {
            this.userLoginAuthMethodResponseTuple =
                await this.userService.queryUserLoginAuthMethod(action);
            this.loginStepIndex = LoginStep.STEP_AUTHENTICATE;
        } catch (err) {
            this.handleAuthMethodError(err);
        }
    }

    async login(): Promise<void> {
        this.isAuthenticating = true;

        const loginAction = await this.userLoginFormTuple.toUserLoginAction(
            this.deviceEnrolmentService.enrolmentToken(),
            this.errorState.warningKeys,
        );

        try {
            const response = await this.userService.login(loginAction);

            if (response.succeeded) {
                await this.handleSuccessfulLogin();
                return;
            }

            this.handleFailedLogin(response);
        } catch (err) {
            this.handleLoginError(err);
        } finally {
            this.isAuthenticating = false;
        }
    }

    reset(): void {
        this.unselectUser();
        this.userLoginFormTuple = new UserLoginFormTuple();
        this.errorState = {
            errors: [],
            warnings: [],
            warningKeys: [],
        };
        this.loginStepIndex = LoginStep.STEP_SELECT_USER;
    }

    gotoPreviousLoginStepIndex(): void {
        if (this.loginStepIndex <= LoginStep.STEP_SELECT_USER) {
            return;
        }

        this.loginStepIndex = this.loginStepIndex - 1;
    }

    async gotoNextLoginStepIndex(): Promise<void> {
        try {
            this.isAuthenticating = true;

            switch (this.loginStepIndex) {
                case LoginStep.STEP_SELECT_USER: {
                    if (!this.validateFieldSelectUserForm()) {
                        this.balloonMsg.showError(
                            "Please complete all required fields",
                        );
                        return;
                    }
                    await this.queryUserLoginAuthMethod();
                    if (this.setting.showVehicleInput) {
                        this.loginStepIndex = LoginStep.STEP_ENTER_VEHICLE;
                    } else {
                        this.loginStepIndex = LoginStep.STEP_AUTHENTICATE;
                    }
                    break;
                }
                case LoginStep.STEP_ENTER_VEHICLE: {
                    if (!this.validateFieldVehicleForm()) {
                        this.balloonMsg.showError(
                            "Please select a valid vehicle",
                        );
                        return;
                    }
                    this.loginStepIndex = LoginStep.STEP_AUTHENTICATE;
                    break;
                }
                case LoginStep.STEP_AUTHENTICATE: {
                    if (!this.validateFieldOtpOrPasswordForm()) {
                        this.balloonMsg.showError(
                            "Invalid authentication details",
                        );
                        return;
                    }
                    await this.login();
                    this.balloonMsg.showSuccess("Login successful");
                    break;
                }
            }
        } catch (error) {
            this.balloonMsg.showError(String(error));
            console.error("Login error:", error);
        } finally {
            this.isAuthenticating = false;
        }
    }

    private initializeUserSettings(): void {
        const settingsSelector = new TupleSelector(
            UserLoginUiSettingTuple.tupleName,
            {},
        );
        this.tupleService.observer
            .subscribeToTupleSelector(settingsSelector)
            .pipe(filter((items) => items.length > 0))
            .subscribe((settings: Tuple[]) => {
                this.setting = <UserLoginUiSettingTuple>settings[0];
                if (this.setting.showUsersAsList) {
                    this.loadUserList();
                }
            });
    }

    private loadUserList(): void {
        const userSelector = new TupleSelector(UserListItemTuple.tupleName, {});
        this.tupleService.observer
            .subscribeToTupleSelector(userSelector)
            .pipe(filter((users) => users.length > 0))
            .subscribe((tuples: Tuple[]) => {
                this.allUsers = <UserListItemTuple[]>tuples;
                this.lastUsers = (<UserListItemTuple[]>tuples) //
                    .filter(
                        (v) =>
                            v.lastLoginDeviceToken ===
                            this.deviceEnrolmentService.enrolmentToken(),
                    );
                const lastUsersSet = new Set(
                    this.lastUsers //
                        .map((v) => v.userId),
                );
                this.recentUsers = (<UserListItemTuple[]>tuples) //
                    .filter(
                        (v) =>
                            v.loggedInLast30Days && !lastUsersSet.has(v.userId),
                    );
            });
    }

    private async handleSuccessfulLogin(): Promise<void> {
        this.reset();
        await this.deviceOnlineService.setDeviceOnline();
        this.balloonMsg.showSuccess("Login Successful");
        await this.router.navigate([""]);
    }

    private handleFailedLogin(response: any): void {
        this.balloonMsg.showWarning(
            "Login Failed, check the warnings and try again",
        );

        const warnings: string[] = [];
        const warningKeys: string[] = [];

        for (const key in response.warnings) {
            if (response.warnings.hasOwnProperty(key)) {
                response.warnings[key]
                    .split("\n")
                    .forEach((warning: string) => {
                        warnings.push(warning);
                    });
                warningKeys.push(key);
            }
        }

        this.errorState = {
            errors: response.errors,
            warnings,
            warningKeys,
        };
    }

    private handleLoginError(err: any): void {
        const errorMessage = String(err);
        if (errorMessage.startsWith("Timed out")) {
            throw new Error("Login Failed. The server didn't respond.");
        }
        if (!errorMessage) {
            throw new Error("An error occurred when logging in.");
        }
        throw new Error(errorMessage);
    }

    private handleAuthMethodError(err: any): void {
        const errorMessage = String(err);
        if (errorMessage.startsWith("Timed out")) {
            throw new Error(
                "Cannot determine verification method for login. The server didn't respond.",
            );
        }
        if (!errorMessage) {
            throw new Error(
                "An error occurred when determining your verification method for login.",
            );
        }
        throw new Error(errorMessage);
    }
}
