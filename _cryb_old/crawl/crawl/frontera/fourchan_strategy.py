from frontera.core.components import States
from frontera.strategy import BaseCrawlingStrategy


class FourchanCrawlingStrategy(BaseCrawlingStrategy):
    def read_seeds(self, stream):
        request = self.create_request(r'http://a.4cdn.org/boards.json')
        self.schedule(request)

    def filter_extracted_links(self, request, links):
        return links

    def links_extracted(self, request, links):
        for link in links:
            if link.meta[b'state'] == States.NOT_CRAWLED:
                self.schedule(link)
                link.meta[b'state'] = States.QUEUED

    def page_crawled(self, response):
        response.meta[b'state'] = States.CRAWLED

    def request_error(self, request, error):
        request.meta[b'state'] = States.ERROR

