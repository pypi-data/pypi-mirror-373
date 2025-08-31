if (opts.navigator_device_memory) {
    Object.defineProperty(Object.getPrototypeOf(navigator), 'deviceMemory', {
        get: () => opts.navigator_device_memory,
    })
}