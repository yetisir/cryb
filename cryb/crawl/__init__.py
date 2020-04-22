# import scrapy
from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings

from cryb import common


class CrawlEntryPoint(common.EntryPoint):
    name = 'crawl'
    description = 'Cryb Crawl Scheduler'

    def run(self, parameters):
        process = CrawlerProcess()
        process.crawl(parameters.spider)

    def build_parser(self, parser):
        parser.add_argument('spider')
        parser.add_argument('seed_urls')


if __name__ == '__main__':
    CrawlEntryPoint.main()
