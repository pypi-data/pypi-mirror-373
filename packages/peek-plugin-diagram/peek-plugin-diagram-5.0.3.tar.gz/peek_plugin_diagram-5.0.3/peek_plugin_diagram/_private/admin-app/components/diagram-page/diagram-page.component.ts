import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "diagram-admin",
    templateUrl: "diagram-page.component.html",
    styleUrls: ["diagram-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DiagramPageComponent {
    protected readonly featuresList$ = new BehaviorSubject<string[]>([
        "Zoom and Pan",
        "Multiple Model Sets",
        "Multiple within a model set",
        "Integrations with other plugins for user click actions and menus",
        "A loader API, allowing other plugins to load and kind of diagram",
        "Integration with Peek Plugin LiveDB to dynamically update the views",
        "Integration with Peek Plugin Node Graph (TODO)",
    ]);
}
