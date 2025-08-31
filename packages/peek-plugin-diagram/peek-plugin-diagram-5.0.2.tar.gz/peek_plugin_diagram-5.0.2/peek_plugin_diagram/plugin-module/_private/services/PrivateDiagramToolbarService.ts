import { BehaviorSubject } from "rxjs";
import { Injectable } from "@angular/core";
import {
    DiagramToolbarBuiltinButtonEnum,
    DiagramToolbarService,
    DiagramToolButtonI,
    ToolbarTypeE,
} from "../../DiagramToolbarService";

@Injectable()
export class PrivateDiagramToolbarService extends DiagramToolbarService {
    readonly toolButtons$ = new BehaviorSubject<DiagramToolButtonI[]>([]);
    readonly options$ = new BehaviorSubject<DiagramToolButtonI[]>([]);
    readonly editToolButtons$ = new BehaviorSubject<DiagramToolButtonI[]>([]);

    readonly buttonBitMask$ = new BehaviorSubject<number>(
        DiagramToolbarBuiltinButtonEnum.ALL_BUTTONS,
    );

    constructor() {
        super();

        /*
         this.addToolButton(null,
         null,
         {
         name: "Mockup",
         tooltip: null,
         icon: 'pencil',
         callback: () => alert("Mockup feature is coming soon."),
         children: []
         }
         );
         
         this.addToolButton(null,
         null,
         {
         name: "Search",
         tooltip: null,
         icon: 'search',
         callback: () => alert("Search feature is coming soon."),
         children: []
         }
         );
         
         
         this.addToolButton(null,
         null,
         {
         name: "WP Home",
         tooltip: null,
         icon: 'home',
         callback: () => alert("This is an example web link"),
         children: []
         }
         );
         */
    }

    get toolButtons(): DiagramToolButtonI[] {
        return this.toolButtons$.getValue();
    }

    private setToolButtons(value: DiagramToolButtonI[]) {
        this.toolButtons$.next([...value]);
    }

    get options(): DiagramToolButtonI[] {
        return this.options$.getValue();
    }

    private setOptions(value: DiagramToolButtonI[]) {
        this.options$.next([...value]);
    }

    get editToolButtons(): DiagramToolButtonI[] {
        return this.editToolButtons$.getValue();
    }

    private setEditToolButtons(value: DiagramToolButtonI[]) {
        this.editToolButtons$.next([...value]);
    }

    get buttonBitMask(): number {
        return this.buttonBitMask$.getValue();
    }

    setButtonBitMask(value: number) {
        this.buttonBitMask$.next(value);
    }

    toolbarBuiltinButtonsMask(): number {
        return this.buttonBitMask;
    }

    setToolbarBuiltinButtonsMask(value: number) {
        this.setButtonBitMask(value);
    }

    addToolButton(
        modelSetKey: string | null,
        coordSetKey: string | null,
        toolButton: DiagramToolButtonI,
        toolbarType: ToolbarTypeE = ToolbarTypeE.ViewToolbar,
    ) {
        if (toolbarType === ToolbarTypeE.ViewToolbar) {
            if (toolButton.isActive == null) {
                this.setToolButtons([...this.toolButtons, toolButton]);
            } else {
                this.setOptions([...this.options, toolButton]);
            }
        } else {
            this.setEditToolButtons([...this.editToolButtons, toolButton]);
        }
    }

    removeToolButton(
        buttonKey: string,
        toolbarType: ToolbarTypeE = ToolbarTypeE.ViewToolbar,
    ) {
        function condition(item: DiagramToolButtonI): boolean {
            return item.key != buttonKey;
        }

        if (toolbarType === ToolbarTypeE.ViewToolbar) {
            this.setToolButtons(this.toolButtons.filter(condition));
            this.setOptions(this.options.filter(condition));
        } else {
            this.setEditToolButtons(this.editToolButtons.filter(condition));
        }
    }
}
