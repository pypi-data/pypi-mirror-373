import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { Injectable } from "@angular/core";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";

@Injectable()
export class CanvasService extends NgLifeCycleEvents {
    private config: PeekCanvasConfig;

    constructor() {
        super();
    }

    setConfig(config: PeekCanvasConfig): void {
        this.config = config;
    }

    invalidate(): void {
        this.config.invalidate();
    }

    setModelNeedsCompiling(): void {
        this.config.setModelNeedsCompiling();
    }
}
