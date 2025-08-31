if (opts.hardwareConcurrency) {
  (utils) => {
    utils.replaceGetterWithProxy(
        Object.getPrototypeOf(navigator),
        'hardwareConcurrency',
        utils.makeHandler().getterValue(opts.hardwareConcurrency)
    )
  }, {
    opts: this.opts
  }
}