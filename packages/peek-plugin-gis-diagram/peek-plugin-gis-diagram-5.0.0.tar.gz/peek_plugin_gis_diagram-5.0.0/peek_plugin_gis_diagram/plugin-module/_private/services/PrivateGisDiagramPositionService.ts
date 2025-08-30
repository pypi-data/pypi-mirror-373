import { filter, first } from "rxjs/operators";
import { GisDiagramPositionService } from "../../GisDiagramPositionService";
import { Injectable } from "@angular/core";
import { DiagramPositionService } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { gisDiagramBaseUrl, gisDiagramModelSetKey } from "../PluginNames";
import { Router } from "@angular/router";

/** Gis Diagram Position Service
 *
 * This service allows other plugins to integrate with the Gis Diagram.
 *
 * This service is a root, persistently provided services, so an plugin need only call
 * "position", this service then loads the diagram and then positions it.
 *
 */
@Injectable()
export class PrivateGisDiagramPositionService extends GisDiagramPositionService {
    constructor(
        private router: Router,
        private pos: DiagramPositionService,
    ) {
        super();
    }

    positionByKey(dispKey: string): void {
        this.pos
            .isReadyObservable()
            .pipe(filter((ready) => ready))
            .pipe(first())
            .subscribe(() => {
                this.pos.positionByKey(gisDiagramModelSetKey, null, {
                    highlightKey: dispKey,
                });
            });

        this.router.navigate([gisDiagramBaseUrl]);
    }

    canPositionByKey(dispKey: string): Promise<boolean> {
        return this.pos.canPositionByKey(gisDiagramModelSetKey, dispKey);
    }
}
