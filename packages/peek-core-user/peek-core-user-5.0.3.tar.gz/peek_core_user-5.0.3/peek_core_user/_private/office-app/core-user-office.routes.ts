import { LoggedInGuard, LoggedOutGuard } from "@peek/peek_core_user";
import { Route } from "@angular/router";
import { OfficeLogoutComponent } from "./components/office-logout/office-logout.component";
import { OfficeLoginComponent } from "./components/office-login/office-login.component";

export const pluginRoutes: Route[] = [
    {
        path: "",
        pathMatch: "full",
        component: OfficeLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "login",
        component: OfficeLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "logout",
        component: OfficeLogoutComponent,
        canActivate: [LoggedInGuard],
    },
    // Fall through to peel-client-fe UnknownRoute
];
