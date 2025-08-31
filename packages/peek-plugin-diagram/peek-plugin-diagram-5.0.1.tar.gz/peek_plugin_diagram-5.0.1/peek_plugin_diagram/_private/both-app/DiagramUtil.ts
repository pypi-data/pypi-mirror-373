/**
 * Date String
 *
 * @return A date and time formatted to a string for log messages.
 */
export function dateStr(): string {
    let d = new Date();
    return d.toTimeString().split(" ")[0] + "." + d.getUTCMilliseconds() + ": ";
}

// ----------------------------------------------------------------------------
/**
 * Keys from Object
 *
 * Extract an array of keys from a json object.
 * This will not include keys starting with an underscore.
 *
 * @param obj: The object to get the keys from.
 * @param includeUnderscore: Should keys with underscores be included?
 * @return A list of keys from the object.
 */
export function dictKeysFromObject(
    obj: {},
    includeUnderscore = false,
): string[] {
    let keys = [];
    for (let k in obj) {
        if (
            (!k.startsWith("_") || includeUnderscore) &&
            obj.hasOwnProperty(k) &&
            typeof k !== "function"
        ) {
            keys.push(k);
        }
    }
    return keys;
}

// ----------------------------------------------------------------------------
/**
 * Values from Object
 *
 * Extract an array representing the values from a json object.
 *
 * @param obj: The object to get the keys from.
 * @return A list of keys from the object.
 */
export function dictValuesFromObject(obj: {}): any[] {
    let values = [];
    for (let k in obj) {
        if (!k.startsWith("_")) values.push(obj[k]);
    }
    return values;
}

// ----------------------------------------------------------------------------
/**
 * Values from Object
 *
 * Extract an array representing the values from a json object.
 *
 * @param arr: The array of objects to become the kets in the dict
 * @return A list of keys from the object.
 */
export function dictSetFromArray(arr: any[]): {} {
    let dict = {};

    // Create the dict of the grid keys, for faster processing
    for (let i = 0; i < arr.length; i++) {
        dict[arr[i]] = true;
    }

    return dict;
}

// ----------------------------------------------------------------------------
/**
 * Bind
 *
 * Bind an object that will become "this" when the function is called.
 *
 * @param obj: The object that will become "this"
 * @param method: The function to call
 * @return A bound method
 */
export function bind(obj, method) {
    return function () {
        return method.apply(obj, arguments);
    };
}

// ----------------------------------------------------------------------------
/** Assert Exception
 *
 * This exception is thrown when an assertion fails.
 *
 */
export class AssertException {
    constructor(public message) {}

    toString() {
        return "AssertException: " + this.message;
    }
}

/**
 * Assert
 *
 * Asserts a condition, else, throws an exception
 *
 * @param exp: The condition to assert true
 * @param message: The message of the thrown exception if the condition is false.
 * @return void
 */
export function assert(exp, message): void {
    if (exp) return;

    console.trace();
    throw new AssertException(message);
}

// ----------------------------------------------------------------------------
export function pointToPixel(point: number): number {
    return (point * 96) / 72;
}

export function pixelToPoint(pixel: number): number {
    return (pixel * 72) / 96;
}
