/** Diagram Snapshot Service
 *
 * This service allows other plugins to get a snapshot of the current canvas as an
 * image.
 *
 */
export abstract class DiagramSnapshotService {
    /** Snapshot Diagram
     *
     * Call this method to retrieve a Base64 encoded snapshot image of the
     * current canvas.
     *
     */
    abstract snapshotDiagram(): Promise<string | null>;
}
