import { LoggedInGuard, LoggedOutGuard } from "@peek/peek_core_user";
import { Route } from "@angular/router";
import { FieldLoginComponent } from "./components/field-login/field-login.component";
import { FieldLogoutComponent } from "./components/field-logout/field-logout.component";

export const pluginRoutes: Route[] = [
    {
        path: "",
        pathMatch: "full",
        component: FieldLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "login",
        component: FieldLoginComponent,
        canActivate: [LoggedOutGuard],
    },
    {
        path: "logout",
        component: FieldLogoutComponent,
        canActivate: [LoggedInGuard],
    },
    // Fall through to peel-client-fe UnknownRoute
];
