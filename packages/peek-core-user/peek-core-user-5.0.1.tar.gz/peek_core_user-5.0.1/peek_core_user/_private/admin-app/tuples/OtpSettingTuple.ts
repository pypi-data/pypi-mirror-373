import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "@peek/peek_core_user/_private/PluginNames";

@addTupleType
export class OtpSettingTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "OtpSettingTuple";

    //  Description of date1
    id: number;
    otpNumberOfWords: number;
    otpNumberOfCandidates: number;
    otpValidSeconds: number;
    constructor() {
        super(OtpSettingTuple.tupleName);
    }

    private static permutations(n: number, r: number): number {
        if (n === 0 || r === 0) {
            return 1;
        } else {
            let result: number = 1;
            for (let i: number = n; i > n - r; i--) {
                result *= i;
            }
            return result;
        }
    }

    static getConfidence(otpSettingTuple: OtpSettingTuple): number {
        return (
            100 -
            otpSettingTuple.otpValidSeconds /
                OtpSettingTuple.permutations(
                    otpSettingTuple.otpNumberOfCandidates,
                    otpSettingTuple.otpNumberOfWords,
                )
        );
    }

    static isConfident(confidence: number): boolean {
        return confidence > 99.99;
    }
}
