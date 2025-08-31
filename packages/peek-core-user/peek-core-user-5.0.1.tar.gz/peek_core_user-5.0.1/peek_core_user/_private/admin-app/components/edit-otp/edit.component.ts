import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { OtpSettingTuple } from "../../tuples/OtpSettingTuple";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

interface OtpConfidenceStats {
    confidence: number;
    style: {
        color: string;
    };
}

@Component({
    selector: "pl-user-edit-otp",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditOtpSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<OtpSettingTuple[]>([]);
    protected readonly itemsToDelete$ = new BehaviorSubject<OtpSettingTuple[]>(
        [],
    );
    protected readonly otpSettingConfidenceStatistics$ =
        new BehaviorSubject<OtpConfidenceStats>({
            confidence: NaN,
            style: {
                color: "#CF1322",
            },
        });

    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.OtpSetting",
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
                const typedTuples = <OtpSettingTuple[]>tuples;
                this.items$.next(typedTuples);
                this.updateConfidenceStat(typedTuples[0]);
                this.itemsToDelete$.next([]);
            });
    }

    protected save(): void {
        const otpSettingTuple = this.items$.value[0];

        if (
            otpSettingTuple.otpNumberOfWords >
            otpSettingTuple.otpNumberOfCandidates
        ) {
            this.balloonMsg.showError(
                "Number of Words must be equal or larger than Number of Candidates",
            );
            return;
        }

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

    protected updateConfidenceStat(otpSettingTuple: OtpSettingTuple): number {
        const confidence = OtpSettingTuple.getConfidence(otpSettingTuple);
        const isOtpSettingConfident = OtpSettingTuple.isConfident(confidence);
        const color = isOtpSettingConfident ? "#3F8600" : "#CF1322";

        this.otpSettingConfidenceStatistics$.next({
            confidence: confidence,
            style: {
                color: color,
            },
        });

        return confidence;
    }
}
