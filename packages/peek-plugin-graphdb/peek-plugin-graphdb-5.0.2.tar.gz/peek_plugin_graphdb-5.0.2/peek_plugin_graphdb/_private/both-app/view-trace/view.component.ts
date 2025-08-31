import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Params } from "@angular/router";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, VortexStatusService } from "@synerty/vortexjs";
import {
    GraphDbService,
    GraphDbTraceResultTuple,
} from "@peek/peek_plugin_graphdb";

@Component({
    selector: "plugin-graphdb-view-trace",
    templateUrl: "view.component.web.html",
})
export class ViewTraceComponent extends NgLifeCycleEvents implements OnInit {
    modelSetKey: string = "pofDiagram";
    traceConfigKey: string = "";
    startVertexKey: string = "";
    traceResult: GraphDbTraceResultTuple = null;
    error: string = "";

    constructor(
        private balloonMsg: BalloonMsgService,
        private route: ActivatedRoute,
        private graphDbService: GraphDbService,
        private vortexStatus: VortexStatusService,
        private headerService: HeaderService,
    ) {
        super();

        headerService.setTitle("DEV test trace ...");
    }

    override ngOnInit() {
        this.route.params
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((params: Params) => {
                let vars = {};

                if (typeof window !== "undefined") {
                    window.location.href.replace(
                        /[?&]+([^=&]+)=([^&]*)/gi,
                        (m, key, value) =>
                            (vars[key] = decodeURIComponent(value)),
                    );
                }

                this.modelSetKey = params["modelSetKey"] || vars["modelSetKey"];
                this.traceConfigKey =
                    params["traceConfigKey"] || vars["traceConfigKey"];
                this.startVertexKey =
                    params["startVertexKey"] || vars["startVertexKey"];

                if (!(this.modelSetKey && this.modelSetKey.length)) return;
                if (!(this.traceConfigKey && this.traceConfigKey.length))
                    return;
                if (!(this.startVertexKey && this.startVertexKey.length))
                    return;

                this.runTrace();
            });
    }

    // private loadDoc(doc: SegmentTuple, key: string) {
    //     this.itemKey = itemKey;
    //     this.itemKeyTypeName = '';
    //
    //     if (this.itemKey == null || this.itemKey.key == null) {
    //         this.balloonMsg.showWarning(`Failed to find ${key}`);
    //         this.headerService.setTitle(`ItemKey ${key} Not Found`);
    //         return;
    //     }
    //     this.balloonMsg.showSuccess(`We've found ${key}`);
    //
    //     this.headerService.setTitle(`ItemKey ${key}`);
    //
    //     this.itemKeyTypeName = this.itemKey.itemKeyType.name;
    // }

    runTrace() {
        this.traceResult = null;
        this.error = "";

        this.graphDbService
            .getTraceResult(
                this.modelSetKey,
                this.traceConfigKey,
                this.startVertexKey,
            )
            .then(
                (result: GraphDbTraceResultTuple) =>
                    (this.traceResult = result),
            )
            .catch((e) => {
                this.balloonMsg.showError(e);
                this.error = e;
            });
    }
}
