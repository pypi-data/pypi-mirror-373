import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzMenuModule } from "ng-zorro-antd/menu";
import { NzDropDownModule } from "ng-zorro-antd/dropdown";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzButtonModule } from 'ng-zorro-antd/button';
import {
    NgLifeCycleEvents,
    Payload,
    Tuple,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { dashboardRoute } from "../../app-routing.module";
import { homeLinks } from "@_peek/plugin-home-links";
import { peekAppEnvironment } from "../../../environments/peek-app-environment";

interface HomeLink {
    name: string;
    title: string;
    resourcePath: string;
}

class UserTuple extends Tuple {
    supportExceeded: boolean = false;
    demoExceeded: boolean = true;
    countsExceeded: boolean = true;
    username: string = "None";

    constructor() {
        super("peek_logic_service.PeekAdmNavbarUserTuple");
    }
}

@Component({
    selector: "app-navbar",
    templateUrl: "./navbar.component.html",
    styleUrls: ["./navbar.component.scss"],
    standalone: true,
    imports: [
        CommonModule,
        RouterModule,
        HttpClientModule,
        NzIconModule,
        NzMenuModule,
        NzDropDownModule,
        NzAlertModule,
        NzButtonModule
    ],
})
export class NavbarComponent extends NgLifeCycleEvents implements OnInit {
    readonly appVersion: string = peekAppEnvironment.version;

    dashboardPath: string | undefined = dashboardRoute.path;
    user: UserTuple = new UserTuple();
    platformMenuData: HomeLink[] = [];
    pluginsMenuData: HomeLink[] = [];
    vortexIsOnline: boolean = false;

    private readonly userDataFilt = {
        plugin: "peek_logic_service",
        key: "nav.adm.user.data",
    };

    constructor(
        private vortexStatusService: VortexStatusService,
        private vortexService: VortexService,
    ) {
        super();

        // Sort home links into platform and plugins
        for (let homeLink of homeLinks) {
            if (homeLink.name.startsWith("peek_core")) {
                this.platformMenuData.push(homeLink);
            } else {
                this.pluginsMenuData.push(homeLink);
            }
        }

        // Sort menu items alphabetically
        this.platformMenuData.sort((a, b) => a.title.localeCompare(b.title));
        this.pluginsMenuData.sort((a, b) => a.title.localeCompare(b.title));

        this.vortexStatusService.isOnline
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v) => (this.vortexIsOnline = v));
    }

    override ngOnInit() {
        this.vortexService
            .createTupleLoader(this, this.userDataFilt)
            .observable.subscribe(
                (tuples) => (this.user = tuples[0] as UserTuple),
            );
    }

    logoutClicked(): void {
        this.vortexService.sendPayload(
            new Payload(Object.assign({ logout: true }, this.userDataFilt)),
        );
        setTimeout(() => location.reload(), 100);
    }
}
