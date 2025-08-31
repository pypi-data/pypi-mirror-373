'use strict'

try {
    window.innerHeight = 720
    window.outerHeight = 896
    window.outerWidth = 414
    window.innerWidth = 414
    Object.defineProperty(Object.getPrototypeOf(document.body), 'clientWidth', {
        get: () => 414,
    })
    Object.defineProperty(Object.getPrototypeOf(document.body), 'clientHeight', {
        get: () => 1361,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'width', {
        get: () => 414,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'height', {
        get: () => 896,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'availWidth', {
        get: () => 414,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'availHeight', {
        get: () => 896,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'colorDepth', {
        get: () => 32,
    })
    Object.defineProperty(Object.getPrototypeOf(screen), 'pixelDepth', {
        get: () => 32,
    })
    window.devicePixelRatio = 2
} catch (err) {
}
