import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import {
    debounceTime,
    distinctUntilChanged,
    filter,
    takeUntil,
} from "rxjs/operators";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    UserListItemTuple,
    UserLoginStepWizardService,
} from "@peek/peek_core_user";
import { UserLoginUiSettingTuple } from "@peek/peek_core_user/_private/tuples/UserLoginUiSettingTuple";

@Component({
    selector: "peek-core-user-field-login-step-user",
    templateUrl: "./field-login-step-user.component.html",
    styleUrls: ["./field-login-step-user.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldLoginStepUserComponent extends NgLifeCycleEvents {
    // Observable streams
    readonly recentUsers$: BehaviorSubject<UserListItemTuple[]>;
    readonly lastUsers$: BehaviorSubject<UserListItemTuple[]>;
    readonly filteredUsers$ = new BehaviorSubject<UserListItemTuple[]>([]);
    readonly searchTerm$ = new BehaviorSubject<string>("");
    readonly isSearching$ = new BehaviorSubject<boolean>(false);
    readonly hasNoMatches$ = new BehaviorSubject<boolean>(true);
    readonly settings$: BehaviorSubject<UserLoginUiSettingTuple>;

    // Keep track of selected user
    selectedUser: UserListItemTuple | null = null;

    constructor(private userLoginWizardService: UserLoginStepWizardService) {
        super();

        this.recentUsers$ = this.userLoginWizardService.recentUsers$;
        this.lastUsers$ = this.userLoginWizardService.lastUsers$;
        this.settings$ = this.userLoginWizardService.setting$;

        // Initialize user filtering
        this.userLoginWizardService.allUsers$
            .pipe(
                takeUntil(this.onDestroyEvent),
                filter((users) => users?.length > 0),
            )
            .subscribe(() => this.filterUsers());

        // Setup debounced search
        this.searchTerm$
            .pipe(
                takeUntil(this.onDestroyEvent),
                debounceTime(300),
                distinctUntilChanged(),
            )
            .subscribe(() => this.filterUsers());
    }

    // Getters and setters for template binding
    get searchTerm(): string {
        return this.searchTerm$.getValue();
    }

    set searchTerm(value: string) {
        this.searchTerm$.next(value);
    }

    set filteredUsers(value: UserListItemTuple[]) {
        this.filteredUsers$.next(value);
    }

    set isSearching(value: boolean) {
        this.isSearching$.next(value);
    }

    set hasNoMatches(value: boolean) {
        this.hasNoMatches$.next(value);
    }

    async selectUser(user: UserListItemTuple): Promise<void> {
        this.selectedUser = user;
        this.userLoginWizardService.selectUser(user);

        await this.userLoginWizardService.gotoNextLoginStepIndex();
    }

    clearSearch(): void {
        this.searchTerm = "";
        this.selectedUser = null;
        this.userLoginWizardService.unselectUser();
        this.filterUsers();
    }

    private filterUsers(): void {
        this.isSearching = true;
        this.hasNoMatches = false;

        const users = this.userLoginWizardService.allUsers;
        const searchTerm = this.searchTerm.trim();

        if (!searchTerm) {
            this.filteredUsers = users;
            this.isSearching = false;
            return;
        }

        const searchLower = searchTerm.toLowerCase();
        const filtered = users.filter((user) =>
            user.combinedDisplayStrForSearch.includes(searchLower),
        );

        this.hasNoMatches = filtered.length === 0;
        this.filteredUsers = filtered;
        this.isSearching = false;
    }
}
