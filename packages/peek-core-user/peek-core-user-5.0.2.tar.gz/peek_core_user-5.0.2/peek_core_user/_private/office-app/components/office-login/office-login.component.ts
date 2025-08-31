import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { UserLoginStepWizardService } from "@peek/peek_core_user";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "peek-core-user-office-login",
    templateUrl: "./office-login.component.html",
    styleUrls: ["./office-login.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OfficeLoginComponent extends NgLifeCycleEvents {
    readonly username$ = new BehaviorSubject<string>("");
    readonly password$ = new BehaviorSubject<string>("");

    constructor(
        headerService: HeaderService,
        private userLoginWizardService: UserLoginStepWizardService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();
        headerService.setTitle("User Login");
    }

    override ngOnInit(): void {
        // Subscribe to form updates
        this.userLoginWizardService.userLoginFormTuple$
            ?.pipe(takeUntil(this.onDestroyEvent))
            .subscribe((form) => {
                if (form) {
                    this.username = form.userName || "";
                    this.password = form.password || "";
                }
            });
    }

    get isAuthenticating$() {
        return this.userLoginWizardService.isAuthenticating$;
    }

    onUsernameInput(event: Event): void {
        const input = event.target as HTMLInputElement;
        const lowercaseValue = input.value.toLowerCase();
        input.value = lowercaseValue;
        this.username = lowercaseValue;
    }

    // Username getter/setter
    set username(value: string) {
        const lowercaseValue = value.toLowerCase();
        this.username$.next(lowercaseValue);
        if (this.userLoginWizardService.userLoginFormTuple) {
            this.userLoginWizardService.userLoginFormTuple.userName =
                lowercaseValue;
        }
    }

    // Password getter/setter
    set password(value: string) {
        this.password$.next(value);
        if (this.userLoginWizardService.userLoginFormTuple) {
            this.userLoginWizardService.userLoginFormTuple.password = value;
        }
    }

    async login(): Promise<void> {
        if (!this.userLoginWizardService.validateOfficeForm()) {
            this.balloonMsg.showWarning("Please enter a username and password");
            return;
        }
        try {
            await this.userLoginWizardService.login();
        } catch (err) {
            this.balloonMsg.showError(String(err));
        }
    }
}
