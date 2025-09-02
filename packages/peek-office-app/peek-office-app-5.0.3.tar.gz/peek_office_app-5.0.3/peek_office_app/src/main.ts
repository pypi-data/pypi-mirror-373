import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";
import { enableProdMode } from "@angular/core";
import { environment } from "./environments/environment";
import { VortexService } from "@synerty/vortexjs";
import { AppModule } from "./app/app.module";
import { Payload, PayloadDelegateWeb } from "@synerty/vortexjs";

const protocol = location.protocol.toLowerCase() === "https:" ? "wss" : "ws";
VortexService.setVortexUrl(
  `${protocol}://${location.hostname}:${location.port}/vortexws`,
);
VortexService.setVortexClientName("peek-office-app");

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
