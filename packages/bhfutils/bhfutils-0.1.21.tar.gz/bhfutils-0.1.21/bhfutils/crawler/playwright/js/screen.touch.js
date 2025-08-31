if (opts.max_touch_points) {
    // Change maxTouchPoints as for iPhone
    Object.defineProperty(Object.getPrototypeOf(navigator), 'maxTouchPoints', {
        get: () => opts.max_touch_points,
    })
    // Recreate createEvent to skip error when touch not supported
    const addTouchEventErrorByPass = () => {
        /* global document */
        const createEventHandler = {
            // Make toString() native
            get(target, key) {
                return Reflect.get(target, key)
            },
            apply: function (target, thisArg, args) {
                const isTouchEvent =
                    args && args.length && `${args[0]}` === 'TouchEvent'
                if (!isTouchEvent) {
                    // Everything as usual
                    return target.apply(thisArg, args)
                } else {
                    return new Event('TouchEvent')
                }
            }
        }
        utils.replaceWithProxy(
            document,
            'createEvent',
            createEventHandler
        )
    }
    addTouchEventErrorByPass()
    // Mock ontouchstart
    Object.defineProperty(window, 'ontouchstart', {
        writable: true,
        enumerable: true,
        configurable: false,
        value: {}
    })
}
