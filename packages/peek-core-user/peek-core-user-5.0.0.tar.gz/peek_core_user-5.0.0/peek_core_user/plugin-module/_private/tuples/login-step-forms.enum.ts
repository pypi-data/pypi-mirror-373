export enum LoginStepForm {
    // Office specific forms
    OFFICE_FORM = -1,

    // Field specific forms
    FIELD_STEP_SELECT_USER = 1,
    FIELD_STEP_VERIFY_OTP = 2,
    FIELD_STEP_VERIFY_PASSWORD = 3,
    FIELD_STEP_VEHICLE = 4,
}

export interface LoginFormValidation {
    userName?: boolean;
    password?: boolean;
    vehicleId?: boolean;
}

export const VALIDATION_CONFIGS: {
    [key in LoginStepForm]: LoginFormValidation;
} = {
    [LoginStepForm.OFFICE_FORM]: {
        userName: true,
        password: true,
    },
    [LoginStepForm.FIELD_STEP_SELECT_USER]: {
        userName: true,
    },
    [LoginStepForm.FIELD_STEP_VERIFY_OTP]: {
        password: true,
    },
    [LoginStepForm.FIELD_STEP_VERIFY_PASSWORD]: {
        password: true,
    },
    [LoginStepForm.FIELD_STEP_VEHICLE]: {
        vehicleId: true,
    },
};
