// ---------------------------------------------------------------------------
// PeekCanvasBounds
// ---------------------------------------------------------------------------
export class PeekCanvasBounds {
    x: number;
    y: number;
    w: number;
    h: number;

    get width(): number {
        return this.w;
    }
    get height(): number {
        return this.h;
    }

    constructor(
        x: number | PeekCanvasBounds = 0.0,
        y: number = 0.0,
        w: number = 0.0,
        h: number = 0.0,
    ) {
        // Copy constructor
        if (x instanceof PeekCanvasBounds) {
            this.x = parseFloat(x.x.toString());
            this.y = parseFloat(x.y.toString());
            this.w = parseFloat(x.w.toString());
            this.h = parseFloat(x.h.toString());
            return;
        }

        this.x = 0.0;
        this.y = 0.0;
        this.w = 0.0;
        this.h = 0.0;

        if (x) this.x = parseFloat(x.toString());

        if (y) this.y = parseFloat(y.toString());

        if (w) this.w = parseFloat(w.toString());

        if (h) this.h = parseFloat(h.toString());

        if (this.w < 0) {
            this.w *= -1;
            this.x = this.x - this.w;
        }

        if (this.h < 0) {
            this.h *= -1;
            this.y = this.y - this.h;
        }
    }

    // Class method
    static fromPoints(points: { x: number; y: number }[]) {
        let geom = [];
        for (let point of points) {
            geom.push(point.x);
            geom.push(point.y);
        }
        return PeekCanvasBounds.fromGeom(geom);
    }

    // Class method
    static fromGeom(geom) {
        const self = new PeekCanvasBounds();

        self.x = geom[0]; // Low x
        self.y = geom[1]; // Upper x
        self.w = 0;
        self.h = 0;

        self.increaseFromGeom(geom);

        return self;
    }

    increaseFromGeom(geom) {
        let ux = this.x + this.w;
        let uy = this.y + this.h;

        for (let i = 0; i < geom.length; i += 2) {
            let pointX = geom[i];
            let pointY = geom[i + 1];

            // Work out our bounds
            if (pointX < this.x) this.x = pointX;

            if (ux < pointX) ux = pointX;

            if (pointY < this.y) this.y = pointY;

            if (uy < pointY) uy = pointY;
        }

        this.w = ux - this.x;
        this.h = uy - this.y;
    }

    increaseFromBounds(bounds) {
        let rx = this.x + this.w; // Right X
        let by = this.y + this.h; // Bottom Y

        const orx = bounds.x + bounds.w; // Right X
        const oby = bounds.y + bounds.h; // Bottom Y

        // Work out our bounds
        if (bounds.x < this.x) this.x = bounds.x;

        if (rx < orx) rx = orx;

        if (bounds.y < this.y) this.y = bounds.y;

        if (by < oby) by = oby;

        this.w = rx - this.x;
        this.h = by - this.y;
    }

    contains(x, y, margin) {
        let b = this;

        // For Bounding Box
        let left = b.x - margin / 2;
        let right = b.x + b.w + margin / 2;
        let top = b.y - margin / 2;
        let bottom = b.y + b.h + margin / 2;

        return (
            left <= x &&
            x <= right && //
            top <= y &&
            y <= bottom
        );
    }

    withIn(x, y, w, h) {
        if (x instanceof PeekCanvasBounds) {
            y = x.y;
            w = x.w;
            h = x.h;
            x = x.x;
        }

        let b = this;
        return (
            x <= b.x &&
            b.x + b.w <= x + w && //
            y <= b.y &&
            b.y + b.h <= y + h
        );
    }

    isEqual(other) {
        if (!(other instanceof PeekCanvasBounds)) return false;

        return (
            this.x === other.x && //
            this.y === other.y && //
            this.w === other.w && //
            this.h === other.h
        ); //
    }

    area() {
        return this.w * this.h;
    }

    center(): { x: number; y: number } {
        return {
            x: this.x + this.w / 2,
            y: this.y + this.h / 2,
        };
    }

    distanceFromPoint(point: { x: number; y: number }): number {
        let center = this.center();
        return Math.sqrt(
            Math.pow(center.x - point.x, 2) + Math.pow(center.y - point.y, 2),
        );
    }

    toString() {
        return `${this.x}x,${this.y}y,${this.w}w,${this.h}h`;
    }
}
