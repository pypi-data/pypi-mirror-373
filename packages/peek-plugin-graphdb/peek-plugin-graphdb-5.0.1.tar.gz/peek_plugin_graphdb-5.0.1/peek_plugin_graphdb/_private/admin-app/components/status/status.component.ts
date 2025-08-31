
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { takeUntil } from "rxjs/operators";
import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { ServerStatusTuple } from "@peek/peek_plugin_graphdb/_private";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pl-graphdb-status",
    templateUrl: "./status.component.html",
    styleUrls: ["./status.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class StatusComponent extends NgLifeCycleEvents {
    protected readonly item$ = new BehaviorSubject<ServerStatusTuple>(new ServerStatusTuple());

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService,
    ) {
        super();

        const ts = new TupleSelector(ServerStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ServerStatusTuple[]) => {
                this.item$.next(tuples[0]);
            });
    }
}