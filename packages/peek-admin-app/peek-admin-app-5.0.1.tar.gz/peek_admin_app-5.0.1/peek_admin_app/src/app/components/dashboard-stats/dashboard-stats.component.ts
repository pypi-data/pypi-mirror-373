
import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import {
  NgLifeCycleEvents,
  VortexService,
  VortexStatusService,
  TupleLoader,
} from "@synerty/vortexjs";
import { filter, first } from "rxjs/operators";

interface Stat {
  desc: string;
  value: string;
}

@Component({
  selector: "app-dashboard-stats",
  templateUrl: "./dashboard-stats.component.html",
  styleUrls: ["./dashboard-stats.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    NzTableModule,
    NzButtonModule,
    NzIconModule,
    NzEmptyModule
  ]
})
export class DashboardStatsComponent extends NgLifeCycleEvents {
  private readonly statsFilt = {
    plugin: "peek_logic_service",
    key: "peakadm.dashboard.list.data",
  };

  stats: Stat[] = [];
  loader?: TupleLoader;

  constructor(vortexService: VortexService, vortexStatus: VortexStatusService) {
    super();

    this.loader = vortexService.createTupleLoader(this, this.statsFilt);

    vortexStatus.isOnline
      .pipe(
        filter(online => online),
        first()
      )
      .subscribe(() => {
        this.loader?.observable.subscribe(
          tuples => {
            this.stats = <Stat[]>tuples;
            this.stats.sort((a, b) => {
              return a.desc.localeCompare(b.desc);
            });
          });
      });
  }
}