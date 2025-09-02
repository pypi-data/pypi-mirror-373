import {
    ChangeDetectionStrategy,
    Component,
    NgZone,
    TemplateRef,
} from "@angular/core";
import { NzModalService } from "ng-zorro-antd/modal";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleActionPushService,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { InternalUserTuple } from "../../tuples/InternalUserTuple";
import { InternalUserUpdatePasswordAction } from "../../tuples/InternalUserUpdatePasswordAction";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { GroupDetailTuple } from "@peek/peek_core_user/tuples/GroupDetailTuple";
import { UserAuthTargetEnum } from "../../tuples/constants/UserAuthTargetEnum";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

interface InternalUserTupleExt extends InternalUserTuple {
    showPasswordPrompt?: boolean;
    newPassword?: string;
    confirmPassword?: string;
}

@Component({
    selector: "pl-user-edit-internal-user",
    templateUrl: "./edit-internal-user.component.html",
    styleUrls: ["./edit-internal-user.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditInternalUserComponent extends NgLifeCycleEvents {
    protected showPassword = false;
    protected readonly items$ = new BehaviorSubject<InternalUserTupleExt[]>([]);
    protected readonly itemsToDelete$ = new BehaviorSubject<
        InternalUserTuple[]
    >([]);
    protected readonly groups$ = new BehaviorSubject<GroupDetailTuple[]>([]);
    protected readonly groupsById: { [key: number]: GroupDetailTuple } = {};
    protected likeTitle = "";

    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.InternalUserTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionProcessor: TupleActionPushService,
        private tupleObserver: TupleDataObserverService,
        private zone: NgZone,
        private modal: NzModalService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () => {
            return Object.assign(
                { likeTitle: this.likeTitle },
                this.filt,
                userFilt,
            );
        });

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <InternalUserTuple[]>tuples;
                this.items$.next(typedTuples);
                this.itemsToDelete$.next([]);
            });

        this.tupleObserver
            .subscribeToTupleSelector(
                new TupleSelector(GroupDetailTuple.tupleName, {}),
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <GroupDetailTuple[]>tuples;
                this.groups$.next(typedTuples);
                for (const tuple of typedTuples) {
                    this.groupsById[tuple.id] = tuple;
                }
            });
    }

    protected needFilter(): boolean {
        return this.likeTitle == null || this.likeTitle.length < 3;
    }

    protected haveItems(): boolean {
        return this.items$.value != null && this.items$.value.length !== 0;
    }

    protected load(): void {
        if (this.needFilter()) {
            this.items$.next([]);
            this.itemsToDelete$.next([]);
            return;
        }

        this.loader.load();
    }

    protected addRow(): void {
        const items = this.items$.value;
        const newItem = new InternalUserTuple();
        newItem.importSource = "PEEK_ADMIN";
        newItem.authenticationTarget = UserAuthTargetEnum.INTERNAL;
        items.push(newItem);
        this.items$.next(items);
    }

    protected removeRow(item: InternalUserTuple): void {
        if (item.id != null) {
            const itemsToDelete = this.itemsToDelete$.value;
            itemsToDelete.push(item);
            this.itemsToDelete$.next(itemsToDelete);
        }

        const items = this.items$.value;
        const index = items.indexOf(item);
        if (index !== -1) {
            this.items$.next(items.filter((_, i) => i !== index));
        }
    }

    protected selectedUser: InternalUserTupleExt;

    protected showPasswordModal(
        item: InternalUserTupleExt,
        tplContent: TemplateRef<{}>,
    ): void {
        this.selectedUser = item;
        this.modal.create({
            nzTitle: "Set Password",
            nzContent: tplContent,
            nzOkText: "Set Password",
            nzCancelText: "Cancel",
            nzOnOk: () => this.handlePasswordConfirm(this.selectedUser)
        });
    }

    protected handlePasswordConfirm(item: InternalUserTupleExt): void {
        if (!item.newPassword) {
            this.balloonMsg.showError("Password cannot be empty");
            return;
        }

        if (item.newPassword !== item.confirmPassword) {
            this.balloonMsg.showError("Passwords do not match");
            return;
        }

        const action = new InternalUserUpdatePasswordAction();
        action.userId = item.id;
        action.newPassword = item.newPassword;

        this.actionProcessor
            .pushAction(action)
            .then(() =>
                this.balloonMsg.showSuccess("Password updated successfully"),
            )
            .catch((e) => this.balloonMsg.showError(e));

        item.newPassword = "";
        item.showPasswordPrompt = false;
    }

    protected save(): void {
        const itemsToDelete = this.itemsToDelete$.value;

        this.loader
            .save(this.items$.value)
            .then(() => {
                if (itemsToDelete.length !== 0) {
                    return this.loader.del(itemsToDelete);
                }
                return null;
            })
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected groupTitleForId(id: number): string {
        return this.groupsById[id]?.groupTitle;
    }

    protected addGroupRow(user: InternalUserTuple): void {
        user.groupIds.push(null);
        this.items$.next([...this.items$.value]);
    }

    protected removeGroupRow(user: InternalUserTuple, index: number): void {
        user.groupIds.splice(index, 1);
        this.items$.next([...this.items$.value]);
    }

    protected updateGroup(
        user: InternalUserTuple,
        index: number,
        id: string,
    ): void {
        user.groupIds[index] = parseInt(id);
        this.items$.next([...this.items$.value]);
    }
}
