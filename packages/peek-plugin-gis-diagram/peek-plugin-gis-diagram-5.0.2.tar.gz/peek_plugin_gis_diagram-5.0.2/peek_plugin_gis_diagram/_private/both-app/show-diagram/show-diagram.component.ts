import { interval } from "rxjs";
import { debounce, filter, first, map, takeUntil } from "rxjs/operators";
import { Location } from "@angular/common";
import { AfterViewInit, Component } from "@angular/core";
import { ActivatedRoute, Params, Router } from "@angular/router";
import {
    DiagramCoordSetService,
    DiagramCoordSetTuple,
    DiagramPositionService,
    PositionUpdatedI,
} from "@peek/peek_plugin_diagram";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { modelSetKey } from "@peek/peek_plugin_gis_diagram/_private/PluginNames";

@Component({
    selector: "plugin-gis-diagram-show-diagram",
    templateUrl: "show-diagram.component.web.html",
})
export class ShowDiagramComponent
    extends NgLifeCycleEvents
    implements AfterViewInit
{
    private landingCoordSetKey = null;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private diagramCoordSetService: DiagramCoordSetService,
        private diagramPosService: DiagramPositionService,
        private loc: Location,
    ) {
        super();
    }

    override ngAfterViewInit(): void {
        // Use the default coord set
        this.diagramCoordSetService
            .diagramCoordSetTuples(modelSetKey)
            .pipe(filter((cs: DiagramCoordSetTuple[]) => cs.length != 0))
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(first())
            .pipe(
                map((cs: DiagramCoordSetTuple[]) =>
                    cs.filter((c) => c.enabled),
                ),
            )
            .subscribe((tuples: DiagramCoordSetTuple[]) => {
                this.landingCoordSetKey = tuples[0].key;
                this._applyRouteParams(this.route.snapshot.params);
            });

        this.diagramPosService
            .isReadyObservable()
            .pipe(filter((ready) => ready))
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(first())
            .subscribe(() => {
                this.route.params
                    .pipe(takeUntil(this.onDestroyEvent))
                    .subscribe((params: Params) =>
                        this._applyRouteParams(params),
                    );
            });

        this.diagramPosService
            .positionUpdatedObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(debounce(() => interval(1000)))
            .subscribe((pos: PositionUpdatedI) => {
                let url = this.router.url.split(";")[0];

                // Sometimes it can try to position after we've navigated away
                if (url.indexOf("peek_plugin_gis_diagram") == -1) return;

                this.router.navigate([
                    url,
                    {
                        x: pos.x,
                        y: pos.y,
                        zoom: pos.zoom,
                    },
                ]);
            });
    }

    private _applyRouteParams(params): void {
        let vars = {};

        if (typeof window !== "undefined") {
            window.location.href.replace(
                /[?&]+([^=&]+)=([^&]*)/gi,
                (m, key, value) => (vars[key] = value),
            );
        }

        let x = params["x"] || vars["x"];
        let y = params["y"] || vars["y"];
        let zoom = params["zoom"] || vars["zoom"] || "1.0";

        let coordSetKey =
            params["coordSetKey"] ||
            vars["coordSetKey"] ||
            this.landingCoordSetKey;

        let dispKey = params["key"] || vars["key"];

        if (coordSetKey == null) {
            console.log("Skipping this param updated, coordSet is null");
            return;
        }

        if (dispKey != null) {
            this.diagramPosService.positionByKey(modelSetKey, coordSetKey, {
                highlightKey: dispKey,
            });
        } else if (x != null && y != null) {
            this.diagramPosService.position(
                coordSetKey,
                parseFloat(x),
                parseFloat(y),
                parseFloat(zoom),
                {},
            );
        } else {
            this.diagramPosService.positionByCoordSet(modelSetKey, coordSetKey);
        }
    }
}
