import { takeUntil } from "rxjs/operators";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminStatusTuple } from "../../tuples/AdminStatusTuple";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pl-livedb-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly statusData$ =
        new BehaviorSubject<AdminStatusTuple | null>(null);

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService,
    ) {
        super();

        const ts = new TupleSelector(AdminStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typeTuple = <AdminStatusTuple[]>tuples;
                this.statusData$.next(typeTuple[0] || null);
            });
    }
}
