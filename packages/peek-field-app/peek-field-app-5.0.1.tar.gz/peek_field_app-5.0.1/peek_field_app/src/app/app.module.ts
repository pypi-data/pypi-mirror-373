import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { NgModule } from "@angular/core";
import { RouterModule } from "@angular/router";
import { BalloonMsgModule } from "@synerty/peek-plugin-base-js";
import {
    SqlFactoryService,
    TupleActionPushOfflineSingletonService,
    TupleOfflineStorageNameService,
    TupleStorageFactoryService,
    TupleStorageFactoryServiceWeb,
} from "@synerty/vortexjs";
import { staticRoutes } from "./app.routes";
import { peekRootServices } from "./app.services";
import { AppComponent } from "./core/components/app/app.component";
import { pluginRootModules } from "../@_peek/plugin-root-modules";
import { pluginRootServices } from "@_peek/plugin-root-services";
import { PluginRootComponent } from "./plugin-root.component";
import { en_US, NZ_I18N } from "ng-zorro-antd/i18n";
import { HttpClientModule } from "@angular/common/http";
import {
    en_US as mobile_en_US,
    LOCAL_PROVIDER_TOKEN,
    NgZorroAntdMobileModule,
} from "ng-zorro-antd-mobile";
import { registerLocaleData } from "@angular/common";
import en from "@angular/common/locales/en";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { ComponentsModule } from "./core/components";
import { PagesModule } from "./pages/pages.module";
import { AngularSvgIconModule } from "angular-svg-icon";
import { ServiceWorkerModule } from "@angular/service-worker";
import { environment } from "../environments/environment";

registerLocaleData(en);

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService("peek_office_service");
}

@NgModule({
    declarations: [AppComponent, PluginRootComponent],
    bootstrap: [AppComponent],
    imports: [
        RouterModule.forRoot(staticRoutes, {}),
        FormsModule,
        NzIconModule,
        BrowserModule,
        BrowserAnimationsModule,
        BalloonMsgModule,
        ...pluginRootModules,
        NgZorroAntdMobileModule,
        HttpClientModule,
        ComponentsModule,
        PagesModule,
        AngularSvgIconModule.forRoot(),
        ServiceWorkerModule.register("ngsw-worker.js", {
            enabled: environment.serviceWorkerEnabled,
            // Register the ServiceWorker as soon as the application is stable
            // or after 30 seconds (whichever comes first).
            registrationStrategy: "registerImmediately",
        }),
    ],
    providers: [
        { provide: NZ_I18N, useValue: en_US },
        { provide: LOCAL_PROVIDER_TOKEN, useValue: mobile_en_US },
        ...peekRootServices,
        SqlFactoryService,
        {
            provide: TupleStorageFactoryService,
            useClass: TupleStorageFactoryServiceWeb,
        },
        TupleActionPushOfflineSingletonService,
        ...pluginRootServices,
    ],
})
export class AppModule {}
