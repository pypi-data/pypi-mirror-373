/* Canvas 2d context - roundRect
 *
 * Accepts 5 parameters, the start_x and start_y points, the end_x and end_y points, and the radius of the corners
 *
 * No return value
 */

interface CanvasRenderingContext2D {
    roundRect(x: number, y: number, w: number, h: number, r: number);

    dashedLine(x1: number, y1: number, x2: number, y2: number, dashLen: number);

    dashedRect(x: number, y: number, w: number, h: number, dashLen: number);
}

let __CanvasRenderingContext2DPrototype: CanvasRenderingContext2D =
    CanvasRenderingContext2D.prototype;

__CanvasRenderingContext2DPrototype.roundRect = function (x, y, w, h, r) {
    let ex = x + w;
    let ey = y + h;

    let r2d = Math.PI / 180;

    // ensure that the radius isn't too large for x
    if (ex - x - 2 * r < 0) r = (ex - x) / 2;

    // ensure that the radius isn't too large for y
    if (ey - y - 2 * r < 0) r = (ey - y) / 2;

    this.beginPath();
    this.moveTo(x + r, y);
    this.lineTo(ex - r, y);
    this.arc(ex - r, y + r, r, r2d * 270, r2d * 360, false);
    this.lineTo(ex, ey - r);
    this.arc(ex - r, ey - r, r, r2d * 0, r2d * 90, false);
    this.lineTo(x + r, ey);
    this.arc(x + r, ey - r, r, r2d * 90, r2d * 180, false);
    this.lineTo(x, y + r);
    this.arc(x + r, y + r, r, r2d * 180, r2d * 270, false);
    this.closePath();
};

__CanvasRenderingContext2DPrototype.dashedLine = function (
    x1,
    y1,
    x2,
    y2,
    dashLen,
) {
    this.moveTo(x1, y1);

    let dX = x2 - x1;
    let dY = y2 - y1;
    let dashes = Math.floor(Math.sqrt(dX * dX + dY * dY) / dashLen);
    let dashX = dX / dashes;
    let dashY = dY / dashes;

    let q = 0;
    while (q++ < dashes) {
        x1 += dashX;
        y1 += dashY;
        this[q % 2 == 0 ? "moveTo" : "lineTo"](x1, y1);
    }
    this[q % 2 == 0 ? "moveTo" : "lineTo"](x2, y2);
};

__CanvasRenderingContext2DPrototype.dashedRect = function (
    x,
    y,
    w,
    h,
    dashLen,
) {
    if (dashLen == 0) {
        this.beginPath();
        this.rect(x, y, w, h);
        this.closePath();
    } else {
        this.beginPath();
        let ex = x + w;
        let ey = y + h;
        this.dashedLine(x, y, ex, y, dashLen);
        this.dashedLine(ex, y, ex, ey, dashLen);
        this.dashedLine(ex, ey, x, ey, dashLen);
        this.dashedLine(x, ey, x, y, dashLen);
        this.closePath();
    }
};
