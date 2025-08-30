import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import {
    en_US as mobile_en_US,
    LOCAL_PROVIDER_TOKEN,
} from "ng-zorro-antd-mobile";
import {
    BalloonMsgModule,
    BalloonMsgService,
} from "@synerty/peek-plugin-base-js";
import {
    SqlFactoryService,
    TupleActionPushOfflineSingletonService,
    TupleStorageFactoryService,
    TupleStorageFactoryServiceWeb,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { AppRoutingModule } from "./app/app-routing.module";
import { AppComponent } from "./app/components/app-component/app.component";
import { PluginRootComponent } from "./app/plugin-root.component";
import { en_US, NZ_I18N } from "ng-zorro-antd/i18n";

import { ACE_CONFIG, AceConfigInterface, AceModule } from "ngx-ace-wrapper";
/** config angular i18n **/
import { registerLocaleData } from "@angular/common";
import en from "@angular/common/locales/en";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";
import { DashboardComponent } from "./app/components/dashboard/dashboard.component";
import { NavbarComponent } from "./app/components/navbar/navbar.component";
import { NzModalModule } from "ng-zorro-antd/modal";

const DEFAULT_ACE_CONFIG: AceConfigInterface = {};

registerLocaleData(en);

@NgModule({
    declarations: [AppComponent, PluginRootComponent],
    imports: [
        AceModule,
        BrowserModule,
        BrowserAnimationsModule,
        FormsModule,
        NzIconModule,
        HttpClientModule,
        AppRoutingModule,
        BalloonMsgModule,
        DashboardComponent,
        NavbarComponent,
        NzModalModule,
    ],
    providers: [
        { provide: NZ_I18N, useValue: en_US },
        { provide: LOCAL_PROVIDER_TOKEN, useValue: mobile_en_US },
        {
            provide: ACE_CONFIG,
            useValue: DEFAULT_ACE_CONFIG,
        },
        {
            provide: TupleStorageFactoryService,
            useClass: TupleStorageFactoryServiceWeb,
        },
        SqlFactoryService,
        TupleActionPushOfflineSingletonService,
        VortexService,
        VortexStatusService,
        BalloonMsgService,
    ],
    bootstrap: [AppComponent],
})
export class AppModule {
    constructor(private vortexStatusService: VortexStatusService) {
        this.vortexStatusService.httpSessionLoggedOut.subscribe(() => {
            setTimeout(() => location.reload(), 100);
        });
    }
}
