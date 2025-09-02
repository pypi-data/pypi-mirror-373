import { UserListItemTuple } from "@peek/peek_core_user";

export function webDisplayText(item: UserListItemTuple): string {
    if (item.userId == null || item?.userId === "") return item.displayName;

    return `${item.displayName} (${item.userId})`;
}
