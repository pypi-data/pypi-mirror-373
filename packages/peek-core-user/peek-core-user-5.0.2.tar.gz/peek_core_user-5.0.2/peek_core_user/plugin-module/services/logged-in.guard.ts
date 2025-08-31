import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { UserService } from "./user.service";
import { filter } from "rxjs/operators";
import { firstValueFrom } from "rxjs";

@Injectable()
export class LoggedInGuard implements CanActivate {
    constructor(
        private user: UserService,
        private router: Router,
    ) {}

    async canActivate(): Promise<boolean> {
        await firstValueFrom(
            this.user
                .loadingFinishedObservable()
                .pipe(filter((finishedLoading) => finishedLoading)),
        );

        if (this.user.isLoggedIn()) return true;

        await this.router.navigate(["peek_core_user", "login"]);
        return false;
    }
}
