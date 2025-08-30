import { Component, ChangeDetectionStrategy } from "@angular/core";
import { takeUntil } from "rxjs/operators";
import { BehaviorSubject } from "rxjs";
import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminStatusTuple } from "../../tuples/AdminStatusTuple";

@Component({
    selector: "pl-eventdb-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly item$ = new BehaviorSubject<AdminStatusTuple>(
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
            .subscribe((tuples: AdminStatusTuple[]) =>
                this.item$.next(tuples[0]),
            );
    }
}
