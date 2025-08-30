const typeMap = {};

export function registerType(shapeType: string, Wrapper: any) {
    typeMap[shapeType] = Wrapper;
}

export function getWrapper(shapeType: string): any {
    return typeMap[shapeType];
}
