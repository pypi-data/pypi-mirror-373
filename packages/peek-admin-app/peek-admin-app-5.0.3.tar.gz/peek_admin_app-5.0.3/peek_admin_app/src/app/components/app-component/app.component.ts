
import { Component, OnInit } from "@angular/core";
import {
  NgLifeCycleEvents,
  VortexService,
  VortexStatusService,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { takeUntil } from "rxjs/operators";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent extends NgLifeCycleEvents implements OnInit {
  isCollapsed = false;

  constructor(
    private vortexService: VortexService,
    private vortexStatusService: VortexStatusService,
    private balloonMsg: BalloonMsgService,
  ) {
    super();

    vortexStatusService.errors
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((msg: string) => balloonMsg.showError(msg));

    vortexStatusService.warning
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((msg: string) => balloonMsg.showWarning(msg));
  }

  override ngOnInit() {
    // This causes two reconnections when the app starts
    // this.vortexService.reconnect();
  }
}