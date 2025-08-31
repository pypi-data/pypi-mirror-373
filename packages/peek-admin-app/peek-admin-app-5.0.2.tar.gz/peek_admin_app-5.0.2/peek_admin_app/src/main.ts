import { enableProdMode } from "@angular/core";
import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";

import { AppModule } from "./app.module";
import { environment } from "./environments/environment";
import { Payload, PayloadDelegateWeb, VortexService } from "@synerty/vortexjs";

const protocol = location.protocol.toLowerCase() == "https:" ? "wss" : "ws";
VortexService.setVortexClientName("peek-admin-app");
VortexService.setVortexUrl(
  `${protocol}://${location.hostname}:${location.port}/vortexws`,
);

if (typeof Worker !== "undefined") {
  // Create a new
  const encodePayloadWorkerCreator = () =>
    new Worker(
      new URL(
        "../node_modules/@synerty/vortexjs/workers/PayloadDelegateWebEncodeWorker",
        import.meta.url,
      ),
      { type: "module" },
    );

  const decodePayloadWorkerCreator = () =>
    new Worker(
      new URL(
        "../node_modules/@synerty/vortexjs/workers/PayloadDelegateWebDecodeWorker",
        import.meta.url,
      ),
      { type: "module" },
    );

  const encodePayloadEnvelopeWorkerCreator = () =>
    new Worker(
      new URL(
        "../node_modules/@synerty/vortexjs/workers/PayloadEnvelopeDelegateWebDecodeWorker",
        import.meta.url,
      ),
      { type: "module" },
    );

  const decodePayloadEnvelopeWorkerCreator = () =>
    new Worker(
      new URL(
        "../node_modules/@synerty/vortexjs/workers/PayloadEnvelopeDelegateWebEncodeWorker",
        import.meta.url,
      ),
      { type: "module" },
    );

  Payload.setWorkerDelegate(
    new PayloadDelegateWeb(
      encodePayloadWorkerCreator,
      decodePayloadWorkerCreator,
      encodePayloadEnvelopeWorkerCreator,
      decodePayloadEnvelopeWorkerCreator,
    ),
  );
}

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule);
