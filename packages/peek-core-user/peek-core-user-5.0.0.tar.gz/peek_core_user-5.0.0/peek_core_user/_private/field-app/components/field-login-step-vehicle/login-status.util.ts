interface LoginStatusCheck {
    isUserSelected: boolean;
    password?: string;
    vehicleId?: string;
    shouldShowVehicleInput: boolean;
}

export function getLoginStatusMessage(params: LoginStatusCheck): string {
    const messages = [];

    if (!params.isUserSelected) {
        messages.push("Please select a user");
    }

    if (!params.password?.length) {
        messages.push("Please enter your password");
    }

    if (params.shouldShowVehicleInput && !params.vehicleId?.length) {
        messages.push("Please enter a vehicle ID");
    }

    return messages.join(", ");
}
