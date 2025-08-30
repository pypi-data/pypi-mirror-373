import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { LdapSettingTuple } from "../../tuples/LdapSettingTuple";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-user-edit-ldap-setting",
    templateUrl: "./edit-ldap-setting.component.html",
    styleUrls: ["./edit-ldap-setting.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditLdapSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<LdapSettingTuple[]>([]);
    protected readonly itemsToDelete$ = new BehaviorSubject<LdapSettingTuple[]>(
        [],
    );
    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.LdapSetting",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(
            this,
            Object.assign({}, this.filt, userFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <LdapSettingTuple[]>tuples;
                this.items$.next(typedTuples);
                this.itemsToDelete$.next([]);
            });
    }

    protected addRow(): void {
        const items = this.items$.value;
        const newItem = new LdapSettingTuple();
        items.push(newItem);
        this.items$.next(items);
    }

    protected removeRow(item: LdapSettingTuple): void {
        if (item.id != null) {
            const itemsToDelete = this.itemsToDelete$.value;
            itemsToDelete.push(item);
            this.itemsToDelete$.next(itemsToDelete);
        }

        const items = this.items$.value;
        const index = items.indexOf(item);
        if (index !== -1) {
            items.splice(index, 1);
            this.items$.next(items);
        }
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
}
