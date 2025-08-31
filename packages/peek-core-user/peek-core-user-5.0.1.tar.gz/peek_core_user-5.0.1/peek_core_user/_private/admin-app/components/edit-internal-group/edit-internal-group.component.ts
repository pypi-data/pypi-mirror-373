import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { InternalGroupTuple } from "../../tuples/InternalGroupTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-user-edit-internal-group",
    templateUrl: "./edit-internal-group.component.html",
    styleUrls: ["./edit-internal-group.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditInternalGroupComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<InternalGroupTuple[]>([]);
    protected readonly itemsToDelete$ = new BehaviorSubject<
        InternalGroupTuple[]
    >([]);
    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.InternalGroupTuple",
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
                const typedTuples = <InternalGroupTuple[]>tuples;
                this.items$.next(typedTuples);
                this.itemsToDelete$.next([]);
            });
    }

    protected addRow(): void {
        const items = this.items$.value;
        const newItem = new InternalGroupTuple();
        this.items$.next([...items, newItem]);
    }

    protected removeRow(item: InternalGroupTuple): void {
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
