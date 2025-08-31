from scrapy.downloadermiddlewares.retry import RetryMiddleware


unserializable_meta_params = ['playwright_page_methods']


class RedisRetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        if retries <= self.max_retry_times:
            retryreq = request.copy()
            # remove unserializable parameters
            for unserializable_meta_param in unserializable_meta_params:
                if unserializable_meta_param in retryreq.meta:
                    del retryreq.meta[unserializable_meta_param]
            # add params
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            # low priority
            retryreq.meta['priority'] = retryreq.meta['priority'] - 10

            return retryreq
