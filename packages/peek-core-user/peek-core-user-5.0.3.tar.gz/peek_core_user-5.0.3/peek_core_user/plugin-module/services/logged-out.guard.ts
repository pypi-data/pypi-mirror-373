import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { UserService } from "./user.service";

@Injectable()
export class LoggedOutGuard implements CanActivate {
    constructor(
        private user: UserService,
        private router: Router,
    ) {}

    async canActivate() {
        if (!this.user.isLoggedIn()) return true;

        await this.router.navigate(["peek_core_user", "logout"]);
        return false;
    }
}
