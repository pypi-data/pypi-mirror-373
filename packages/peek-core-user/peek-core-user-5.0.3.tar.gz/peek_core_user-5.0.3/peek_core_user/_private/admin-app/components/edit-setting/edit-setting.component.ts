import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { SettingPropertyTuple } from "../../tuples/SettingPropertyTuple";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-user-edit-setting",
    templateUrl: "./edit-setting.component.html",
    styleUrls: ["./edit-setting.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected settingsType = "Global";
    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign(
                { settingType: this.settingsType },
                this.filt,
                userFilt,
            ),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected save(): void {
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected reset(): void {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected settingTypeChanged(): void {
        this.loader.load().catch((e) => this.balloonMsg.showError(e));
    }

    protected filterSettingsByKeyword(
        keyword: string,
        items: SettingPropertyTuple[],
    ): SettingPropertyTuple[] {
        if (!items) return [];

        const filtered = items.filter((t) =>
            t.key.toLowerCase().includes(keyword.toLowerCase()),
        );
        return filtered.sort((a, b) => (a.key < b.key ? -1 : 0));
    }
}
