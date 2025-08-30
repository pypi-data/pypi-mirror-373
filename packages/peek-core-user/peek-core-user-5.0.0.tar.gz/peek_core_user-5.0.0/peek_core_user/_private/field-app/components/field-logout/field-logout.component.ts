import { ChangeDetectionStrategy, Component } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { UserService } from "@peek/peek_core_user";
import { UserLogoutAction } from "@peek/peek_core_user/_private/tuples/UserLogoutAction";
import { DeviceOnlineService } from "@peek/peek_core_device/_private";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "peek-core-user-field-logout",
    templateUrl: "./field-logout.component.html",
    styleUrls: ["./field-logout.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldLogoutComponent extends NgLifeCycleEvents {
    // BehaviorSubjects
    readonly isLoggingOut$ = new BehaviorSubject<boolean>(false);
    readonly errors$ = new BehaviorSubject<string[]>([]);
    readonly warnings$ = new BehaviorSubject<string[]>([]);
    private warningKeys: string[] = [];

    constructor(
        private userService: UserService,
        private router: Router,
        private deviceOnlineService: DeviceOnlineService,
        private balloonMsg: BalloonMsgService,
        headerService: HeaderService,
    ) {
        super();
        headerService.setTitle("User Logout");
    }

    // Getters and setters for BehaviorSubjects
    get isLoggingOut(): boolean {
        return this.isLoggingOut$.getValue();
    }

    set isLoggingOut(value: boolean) {
        this.isLoggingOut$.next(value);
    }

    get errors(): string[] {
        return this.errors$.getValue();
    }

    set errors(value: string[]) {
        this.errors$.next(value);
    }

    get warnings(): string[] {
        return this.warnings$.getValue();
    }

    set warnings(value: string[]) {
        this.warnings$.next(value);
    }

    // Current user display
    get loggedInUserText(): string {
        const details = this.userService.userDetails;
        return details
            ? `${details.displayName} (${details.userId})`
            : "Unknown User";
    }

    async doLogout(): Promise<void> {
        if (this.isLoggingOut) {
            return;
        }

        this.isLoggingOut = true;

        const logoutAction = new UserLogoutAction();
        logoutAction.userName = this.userService.userDetails.userId;
        logoutAction.acceptedWarningKeys = this.warningKeys;

        try {
            const response = await this.userService.logout(logoutAction);

            if (response.succeeded) {
                await this.handleSuccessfulLogout();
                return;
            }

            this.handleFailedLogout(response);
        } catch (err) {
            this.handleLogoutError(err);
        } finally {
            this.isLoggingOut = false;
        }
    }

    async navigateHome(): Promise<void> {
        await this.router.navigate([""]);
    }

    private async handleSuccessfulLogout(): Promise<void> {
        await this.deviceOnlineService.setDeviceOffline();
        this.balloonMsg.showSuccess("Logout Successful");
        await this.router.navigate([""]);
    }

    private handleFailedLogout(response: any): void {
        this.balloonMsg.showWarning(
            "Logout Failed, check the warnings and" + " try" + " again",
        );

        const warnings: string[] = [];
        const warningKeys: string[] = [];

        for (const key in response.warnings) {
            if (response.warnings.hasOwnProperty(key)) {
                const warningMessages = response.warnings[key].split("\n");
                warnings.push(...warningMessages);
                warningKeys.push(key);
            }
        }

        this.errors = response.errors || [];
        this.warnings = warnings;
        this.warningKeys = warningKeys;
    }

    private handleLogoutError(err: any): void {
        const errorMessage = String(err);
        if (errorMessage.startsWith("Timed out")) {
            this.balloonMsg.showError(
                "Logout Failed. The server didn't" + " respond.",
            );
            return;
        }
        this.balloonMsg.showError(errorMessage);
    }

    private clearMessages(): void {
        this.errors = [];
        this.warnings = [];
        this.warningKeys = [];
    }
}
