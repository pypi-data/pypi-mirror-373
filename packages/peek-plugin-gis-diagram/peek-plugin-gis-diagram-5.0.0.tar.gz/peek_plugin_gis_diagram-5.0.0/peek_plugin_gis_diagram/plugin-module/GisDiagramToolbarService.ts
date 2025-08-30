import { Injectable } from "@angular/core";
import {
    DiagramToolbarService,
    DiagramToolButtonI,
} from "@peek/peek_plugin_diagram/DiagramToolbarService";
import { gisDiagramModelSetKey } from "./_private/PluginNames";

export { DiagramToolButtonI } from "@peek/peek_plugin_diagram/DiagramToolbarService";

/** Gis Diagram Toolbar Service
 *
 * Use this service to add items to the toolbars.
 *
 * This is a helper service to simplify integrations with the diagram.
 *
 *
 */

@Injectable()
export class GisDiagramToolbarService {
    constructor(private diagramService: DiagramToolbarService) {}

    /** Add Tool Button
     *
     * Call this method to add new tool buttons to the diagrams tool bar.
     *
     * @param toolButton: A single tool button, or a hierarchy of tool buttons to add
     * to the diagrams tool bar.
     */
    addToolButton(toolButton: DiagramToolButtonI) {
        this.diagramService.addToolButton(
            gisDiagramModelSetKey,
            null,
            toolButton,
        );
    }
}
