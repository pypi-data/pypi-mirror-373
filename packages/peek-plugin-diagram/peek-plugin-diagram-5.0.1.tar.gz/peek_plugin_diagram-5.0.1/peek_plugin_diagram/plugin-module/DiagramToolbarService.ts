/** Diagram Tool Button Callback Interface
 *
 * This interface represents a function that is called when the user selects a
 * toolbar menu option.
 *
 */
export interface DiagramToolButtonCallbackI {
    (): void;
}

/** Diagram Tool Button Active Interface
 *
 * This interface represents a function that is called by Angular to determine
 * if a toolbar button is active..
 *
 */
export interface DiagramToolButtonActiveI {
    (): boolean;
}

/** Diagram Tool Button Interface
 *
 * This interface represents a hierarchy of toolbar buttons that are shown on the left
 * hand side of the diagram in the mobile view.
 *
 * NOTE: Don't assign a callback if children are set.
 *
 * @param key: This is a unique key for this button. Prefix it with the plugins name.
 * @param name: The name of the toolbar button
 * @param offName: The name to display to turn off the option.
 *
 */
export interface DiagramToolButtonI {
    key?: string;
    name: string;
    offName?: string;
    tooltip: string | null;
    icon: string | null;
    callback: DiagramToolButtonCallbackI | null;
    children: DiagramToolButtonI[];
    isActive?: DiagramToolButtonActiveI | null;
}

export enum ToolbarTypeE {
    ViewToolbar = 1,
    EditToolbar = 2,
}

/** Diagram Toolbar Service
 *
 * This service allows other plugins to provide tool buttons that are displayed
 * on the diagrams window.
 */
export abstract class DiagramToolbarService {
    protected constructor() {}

    /** Add Tool Button
     *
     * Call this method to add new tool buttons to the diagrams toolbar.
     * @param modelSetKey The model set to show the button on the toolbar for.
     * null means all of them.
     *
     * @param coordSetKey The coord set to show the button on the toolbar for.
     * null means all of them.
     *
     * @param toolButton A single tool button, or a hierarchy of tool buttons to add
     * to the diagrams' toolbar.
     *
     * @param toolbarType The type of the toolbar to add the button to.
     */
    abstract addToolButton(
        modelSetKey: string | null,
        coordSetKey: string | null,
        toolButton: DiagramToolButtonI,
        toolbarType?: ToolbarTypeE,
    ): void;

    /** Remove Tool Button
     *
     * @param buttonKey The key of the button to remove.
     *
     * @param toolbarType The type of the toolbar to add the button to.
     */
    abstract removeToolButton(
        buttonKey: string,
        toolbarType?: ToolbarTypeE,
    ): void;

    abstract toolbarBuiltinButtonsMask(): number;

    abstract setToolbarBuiltinButtonsMask(buttonBitMask: number): void;
}

export enum DiagramToolbarBuiltinButtonEnum {
    BUTTON_NULL = 0,
    BUTTON_CHANGE_CANVAS_MENU = 1 << 0,
    BUTTON_PRINT_DIAGRAM = 1 << 1,
    BUTTON_EDIT_DIAGRAM = 1 << 2,
    BUTTON_SELECT_BRANCHES = 1 << 3,
    BUTTON_SELECT_LAYERS = 1 << 4,
    BUTTON_COLOR_MODES = 1 << 5,
    ALL_BUTTONS = 0x7fffffff,
}
