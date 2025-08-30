import { Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "plugin-gis-diagram",
    templateUrl: "gisDiagram.component.web.html",
})
export class GisDiagramComponent extends NgLifeCycleEvents {
    constructor(private headerService: HeaderService) {
        super();

        this.headerService.setTitle("GIS Diagram");
    }
}
