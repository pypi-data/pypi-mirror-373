import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject, Observable, Subject } from "rxjs";
import { first, takeUntil } from "rxjs/operators";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
} from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import {
    DeviceEnrolmentService,
    DeviceInfoTuple,
} from "@peek/peek_core_device";
import { DeviceOnlineService } from "@peek/peek_core_device/_private";
import { UserTupleService } from "../_private/user-tuple.service";
import { UserLoggedInTuple } from "../_private";
import { UserListItemTuple } from "../tuples/UserListItemTuple";
import {
    UserLoginAction,
    UserLoginAuthMethodAction,
    UserLoginAuthMethodResponseTuple,
    UserLoginOtpAction,
    UserLoginOtpResponseTuple,
    UserLoginResponseTuple,
    UserLogoutAction,
    UserLogoutResponseTuple,
} from "../tuples";
import {
    INITIAL_STATE,
    UserServiceState,
    UserServiceStateTuple,
} from "../_private/user-service-state.model";

@Injectable()
export class UserService extends NgLifeCycleEvents {
    private readonly state$ = new BehaviorSubject<UserServiceState>(
        INITIAL_STATE,
    );
    readonly loggedInStatus$ = new BehaviorSubject<boolean>(false);
    readonly loggedInStatus = new Subject<boolean>();
    private readonly loadingFinished$ = new BehaviorSubject<boolean>(false);
    private readonly stateSelector = new TupleSelector(
        UserServiceStateTuple.tupleName,
        {},
    );

    constructor(
        private router: Router,
        private balloonMsg: BalloonMsgService,
        private deviceEnrolmentService: DeviceEnrolmentService,
        private deviceOnlineService: DeviceOnlineService,
        private tupleService: UserTupleService,
    ) {
        super();
        this.initializeService();
    }

    // Public API Methods
    get users(): UserListItemTuple[] {
        return this.state$.getValue().users;
    }

    get userDetails(): UserListItemTuple | null {
        return this.state$.getValue().serviceState.userDetails;
    }

    get loggedInUserDetails(): UserListItemTuple {
        if (!this.userDetails) {
            throw new Error("loggedInUserDetails called when null");
        }
        return this.userDetails;
    }

    get userGroups(): string[] {
        return this.state$.getValue().serviceState.userGroups;
    }

    get loggedIn(): boolean {
        return this.state$.getValue().serviceState.authToken !== null;
    }

    isLoggedIn(): boolean {
        return this.loggedIn;
    }

    hasLoaded(): boolean {
        return this.loadingFinished$.getValue();
    }

    loadingFinishedObservable(): Observable<boolean> {
        return this.loadingFinished$.asObservable();
    }

    async requestOtp(
        action: UserLoginOtpAction,
    ): Promise<UserLoginOtpResponseTuple> {
        const tuples = await this.tupleService.action.pushAction(action);
        return this.validateOtpResponse(tuples);
    }

    async queryUserLoginAuthMethod(
        action: UserLoginAuthMethodAction,
    ): Promise<UserLoginAuthMethodResponseTuple> {
        const tuples = await this.tupleService.action.pushAction(action);
        return this.validateAuthMethodResponse(tuples);
    }

    async login(action: UserLoginAction): Promise<UserLoginResponseTuple> {
        this.setDeviceTokens(action);
        const tuples = await this.tupleService.action.pushAction(action);
        return this.validateLoginResponse(tuples);
    }

    async logout(action: UserLogoutAction): Promise<UserLogoutResponseTuple> {
        if (!this.loggedIn) {
            throw new Error("Cannot logout when not logged in");
        }

        this.setDeviceTokens(action);

        try {
            const tuples = await this.tupleService.action.pushAction(action);
            const response = this.validateLogoutResponse(tuples);

            if (response.succeeded) {
                this.setLogout();
            }

            return response;
        } catch (err) {
            if (String(err).includes("not logged in")) {
                this.setLogout();
            }
            throw err;
        }
    }

    userDisplayName(userName: string): string | null {
        return this.state$.getValue().userDisplayNameById[userName] || null;
    }

    // Private Methods
    private initializeService(): void {
        this.initializeUserList();
        this.initializeDeviceSubscription();
        this.setupOnDestroy();
        this.loadState().catch((e) =>
            console.error(`UserService: Error loading state ${e}`),
        );
    }

    private initializeUserList(): void {
        const tupleSelector = new TupleSelector(
            UserListItemTuple.tupleName,
            {},
        );
        this.tupleService.observer
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples) => {
                this.updateUserList(tuples as UserListItemTuple[]);
            });
    }

    private initializeDeviceSubscription(): void {
        this.deviceEnrolmentService
            .deviceInfoObservable()
            .pipe(first())
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((deviceInfo: DeviceInfoTuple) => {
                this.setupUserLoggedInSubscription(deviceInfo);
            });
    }

    private setupUserLoggedInSubscription(deviceInfo: DeviceInfoTuple): void {
        const selector = new TupleSelector(UserLoggedInTuple.tupleName, {
            deviceToken: deviceInfo.deviceToken,
        });

        this.tupleService.observer
            .subscribeToTupleSelector(selector, true)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples) =>
                this.handleUserLoggedInUpdate(tuples as UserLoggedInTuple[]),
            );
    }

    private setupOnDestroy(): void {
        this.onDestroyEvent.subscribe(() => {
            const observers = (this.loggedInStatus as any)["observers"];
            if (observers) {
                observers.forEach((observer: any) => observer.unsubscribe());
            }
        });
    }

    private async loadState(): Promise<void> {
        const tuples = await this.tupleService.offlineStorage.loadTuples(
            this.stateSelector,
        );

        if (tuples.length > 0) {
            const serviceState = tuples[0] as UserServiceStateTuple;
            this.updateState({ serviceState });

            if (serviceState.userDetails) {
                this.setLogin(
                    serviceState.userDetails,
                    serviceState.userGroups,
                );
                this.deviceOnlineService.setDeviceOnline();
            } else {
                this.deviceOnlineService.setDeviceOffline();
            }
        }

        if (!this.hasLoaded()) {
            this.loadingFinished$.next(true);
        }
    }

    private setDeviceTokens(action: UserLoginAction | UserLogoutAction): void {
        action.deviceToken = this.deviceEnrolmentService.enrolmentToken();
        action.isOfficeService = this.deviceEnrolmentService.isOfficeService();
        action.isFieldService = this.deviceEnrolmentService.isFieldService();
    }

    private validateOtpResponse(tuples: Tuple[]): UserLoginOtpResponseTuple {
        if (!tuples?.length) {
            throw new Error("OTP request received no response from server");
        }

        const response = tuples[0] as UserLoginOtpResponseTuple;
        if (response._tupleType !== UserLoginOtpResponseTuple.tupleName) {
            throw new Error(`Unknown OTP response tuple: ${response}`);
        }

        return response;
    }

    private validateAuthMethodResponse(
        tuples: Tuple[],
    ): UserLoginAuthMethodResponseTuple {
        if (!tuples?.length) {
            throw new Error(
                "Auth method request received no response from server",
            );
        }

        const response = tuples[0] as UserLoginAuthMethodResponseTuple;
        if (
            response._tupleType !== UserLoginAuthMethodResponseTuple.tupleName
        ) {
            throw new Error(`Unknown auth method response tuple: ${response}`);
        }

        return response;
    }

    private validateLoginResponse(tuples: Tuple[]): UserLoginResponseTuple {
        if (!tuples?.length) {
            throw new Error("Login received no response from server");
        }

        const response = tuples[0] as UserLoginResponseTuple;
        if (response._tupleType !== UserLoginResponseTuple.tupleName) {
            throw new Error(`Unknown login response tuple: ${response}`);
        }

        return response;
    }

    private validateLogoutResponse(tuples: Tuple[]): UserLogoutResponseTuple {
        if (!tuples?.length) {
            throw new Error("Logout received no response from server");
        }

        const response = tuples[0] as UserLogoutResponseTuple;
        if (response._tupleType !== UserLogoutResponseTuple.tupleName) {
            throw new Error(`Unknown logout response tuple: ${response}`);
        }

        return response;
    }

    private updateUserList(users: UserListItemTuple[]): void {
        const userDisplayNameById: { [id: string]: string } = {};
        users.forEach((user) => {
            userDisplayNameById[user.userId] = user.displayName;
        });

        this.updateState({
            users,
            userDisplayNameById,
        });
    }

    private async handleUserLoggedInUpdate(
        tuples: UserLoggedInTuple[],
    ): Promise<void> {
        if (tuples.length !== 1) return;

        const userLoggedIn = tuples[0];
        const serverSaidLoggedIn = userLoggedIn.userDetails != null;

        if (serverSaidLoggedIn) {
            if (!this.loggedIn) {
                this.setLogin(
                    userLoggedIn.userDetails,
                    userLoggedIn.userGroups,
                );
                await this.router.navigate([""]);
            }
            return;
        }

        if (!this.loggedIn) return;

        await this.setLogout();
        await this.handleForcedLogout();
    }

    private async handleForcedLogout(): Promise<void> {
        await this.balloonMsg.showMessage(
            "This user has been logged out due to a login/logout on another device, " +
                "or an administrative logout",
            BalloonMsgLevel.Error,
            BalloonMsgType.Confirm,
        );
        await this.router.navigate(["peek_core_user", "login"]);
    }

    private async setLogin(
        userDetails: UserListItemTuple,
        userGroups: string[] = [],
    ): Promise<void> {
        const serviceState = this.state$.getValue().serviceState;
        serviceState.authToken = "TODO, but not null";
        serviceState.userDetails = userDetails;
        serviceState.userGroups = userGroups;

        this.updateState({ serviceState });
        this.updateLoggedInStatus(true);
        await this.storeState();
    }

    private async setLogout(): Promise<void> {
        const serviceState = this.state$.getValue().serviceState;
        serviceState.userDetails = null;
        serviceState.userGroups = [];
        serviceState.authToken = null;

        this.updateState({ serviceState });
        this.updateLoggedInStatus(false);
        await this.storeState();
    }

    private updateState(partial: Partial<UserServiceState>): void {
        this.state$.next({
            ...this.state$.getValue(),
            ...partial,
        });
    }

    private updateLoggedInStatus(status: boolean): void {
        this.loggedInStatus$.next(status);
        this.loggedInStatus.next(status);
    }

    private async storeState(): Promise<void> {
        try {
            await this.tupleService.offlineStorage.saveTuples(
                this.stateSelector,
                [this.state$.getValue().serviceState],
            );
        } catch (e) {
            console.error(`UserService: Error storing state ${e}`);
        }
    }
}
