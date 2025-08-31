const override = {
    acceptLanguage: 'en-US,en',
    platform: this.opts.platform
}

page._client.send('Network.setUserAgentOverride', override)