import { Component, ChangeDetectionStrategy } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminStatusTuple } from "@peek/peek_core_search/_private";

@Component({
    selector: "pl-search-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly statusData$ = new BehaviorSubject<AdminStatusTuple>(
        new AdminStatusTuple(),
    );

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
                this.statusData$.next(typeTuple[0]);
            });
    }
}
