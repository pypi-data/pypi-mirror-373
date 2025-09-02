import { ChangeDetectionStrategy, Component } from "@angular/core";
import { Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { UserService } from "@peek/peek_core_user";
import { DeviceOnlineService } from "@peek/peek_core_device/_private";
import { UserLogoutAction } from "@peek/peek_core_user/_private/tuples/UserLogoutAction";
import { NzMessageService } from "ng-zorro-antd/message";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "peek-core-user-office-logout",
    templateUrl: "./office-logout.component.html",
    styleUrls: ["./office-logout.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OfficeLogoutComponent extends NgLifeCycleEvents {
    readonly isLoggingOut$ = new BehaviorSubject<boolean>(false);

    constructor(
        private userService: UserService,
        private router: Router,
        private deviceOnlineService: DeviceOnlineService,
        private message: NzMessageService,
        headerService: HeaderService,
    ) {
        super();
        headerService.setTitle("User Logout");
    }

    get isLoggingOut(): boolean {
        return this.isLoggingOut$.getValue();
    }

    set isLoggingOut(value: boolean) {
        this.isLoggingOut$.next(value);
    }

    async doLogout(): Promise<void> {
        if (this.isLoggingOut) {
            return;
        }

        const action = new UserLogoutAction();
        action.userName = this.userService.userDetails.userId;

        this.isLoggingOut = true;

        try {
            await this.userService.logout(action);
            await this.deviceOnlineService.setDeviceOffline();
            this.message.success("Logout Successful");
            await this.router.navigate([""]);
        } catch (err) {
            const errorMessage = String(err);
            if (errorMessage.startsWith("Timed out")) {
                this.message.error("Logout Failed. The server didn't respond.");
                return;
            }
            this.message.error(errorMessage);
        } finally {
            this.isLoggingOut = false;
        }
    }

    get loggedInUserText(): string {
        const { displayName, userId } = this.userService.userDetails;
        return `${displayName} (${userId})`;
    }
}
