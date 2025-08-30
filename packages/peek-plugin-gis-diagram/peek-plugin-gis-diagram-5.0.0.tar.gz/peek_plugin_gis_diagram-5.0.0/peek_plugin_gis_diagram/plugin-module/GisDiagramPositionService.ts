/** Diagram Position Service
 *
 * This service allows other plugins embedding the diagram to position the diagram.
 *
 */

export abstract class GisDiagramPositionService {
    constructor() {}

    /** Position By Key
     *
     * @param dispKey: The key equipment to position on.
     *
     */
    abstract positionByKey(dispKey: string): void;

    /** Can Position By Key
     *
     * @param dispKey: The key equipment to position on.
     * @returns A promise that fires wth true or false.
     *
     */
    abstract canPositionByKey(dispKey: string): Promise<boolean>;
}
