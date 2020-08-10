from scrapy import Spider
from scrapy.selector import Selector
from crawl.items import Board, Thread, Comment
from datetime import datetime
import dateparser
from scrapy.utils.project import get_project_settings
import pymongo
settings = get_project_settings()


class BitcoinTalkSpider(Spider):
    name = 'bitcointalk'
    allowed_domains = ['bitcointalk.org']
    start_urls = [
        'http://bitcointalk.org/',
    ]

    boards_to_crawl = [
        'b67',
    ]

    def parse(self, response):

        boards = Selector(response).xpath(
            '//tr/td/b/a[starts-with(@name, "b")]/../../..'
        )

        threads = Selector(response).xpath(
            '//span[starts-with(@id, "msg")]/../..'
        )

        comments = Selector(response).xpath(
            '//div[starts-with(@id, "subject")]/../../../../../..'
        )

        next_page = Selector(response).xpath(
            '//span[@class="prevnext"]/child::*'
        )

        # handle boards
        for board in boards:
            item = self.parse_board(response, board)
            if self.valid_item(item, self.db.boards):
                yield item
                yield response.follow(
                    item['url'],
                    callback=self.parse,
                    meta={'board': item['id']}
                )

        updated_threads = False
        if response.meta.get('board') in self.boards_to_crawl:
            # handle threads
            for thread in threads:
                item = self.parse_thread(response, thread)
                if self.valid_item(item, self.db.threads):
                    updated_threads = True
                    yield item
                    yield response.follow(
                        item['url'],
                        callback=self.parse,
                        meta={
                            'thread': item['id'],
                            'board': response.meta.get('board'),
                        }
                    )

            # handle comments
            oldest_comment_timestamp = datetime.utcfromtimestamp(0)
            for comment in comments:
                item = self.parse_comment(response, comment)
                comment_id = item['id']
                oldest_comment_timestamp = min(
                    oldest_comment_timestamp, item['timestamp'])

                db_comment = self.db.comments.find_one({'id': comment_id})

                if not db_comment or self.archive:
                    yield item

            # handle next page
            latest_db_timestamp = self.latest_saved_comment_timestamp(
                response.meta.get('thread'))
            next_page_link = self.get_next_page_link(next_page)

            if next_page_link:
                if self.archive or (updated_threads or
                                    oldest_comment_timestamp >
                                    latest_db_timestamp):

                    yield response.follow(
                        next_page_link,
                        callback=self.parse,
                        meta=response.meta
                    )

    def get_next_page_link(self, next_page):
        prevnext_links = next_page.xpath('child::text()')
        next_page_link = None
        for i, prevnext_text in enumerate(prevnext_links.extract()):

            if ord(prevnext_text) == 187:
                next_page_link = next_page[i].xpath(
                    '@href'
                ).extract_first()

        return next_page_link

    def latest_saved_comment_timestamp(self, comment_thread):
        most_recent_db_comment = self.db.comments.find_one(
            filter={'thread': comment_thread},
            sort=[('timestamp', pymongo.DESCENDING)]
        )

        if most_recent_db_comment is not None:
            latest_db_timestamp = most_recent_db_comment['timestamp']
        else:
            latest_db_timestamp = datetime.utcfromtimestamp(0)

        return latest_db_timestamp

    def valid_item(self, item, collection):
        if self.archive:
            return True

        db_thread = collection.find_one({'id': item['id']})

        if not db_thread:
            return True
        elif db_thread['last_scraped'] < item['last_post']:
            return True

        return False

    def parse_board(self, response, board):

        item = Board()
        item['name'] = board.xpath(
            'descendant::a[starts-with(@name, "b")]/text()'
        ).extract_first()

        item['id'] = board.xpath(
            'descendant::a[starts-with(@name, "b")]/@name'
        ).extract_first()

        item['url'] = board.xpath(
            'descendant::a[starts-with(@name, "b")]/@href'
        ).extract_first()

        item['description'] = ''.join(board.xpath(
            'descendant::td/text()'
        ).extract()).strip()

        item['last_scraped'] = datetime.utcnow()

        item['last_post'] = dateparser.parse(board.xpath(
            'descendant::b[contains(text(), "Last post")]/..'
        ).xpath('normalize-space()').extract_first().split('on ')[-1],
                                             settings={'TIMEZONE': 'UTC'})

        return self.verify_date(item, 'last_post')

    def parse_thread(self, response, thread):
        item = Thread()
        item['title'] = thread.xpath(
            'descendant::span[starts-with(@id, "msg")]/a/text()'
        ).extract_first()

        item['url'] = thread.xpath(
            'descendant::span[starts-with(@id, "msg")]/a/@href'
        ).extract_first()

        item['id'] = item['url'].split('topic=')[1].split('.')[0]

        item['author'] = thread.xpath(
            'descendant::a[starts-with(@title, "View")]/text()'
        ).extract_first()

        item['board'] = response.meta.get('board')

        item['last_scraped'] = datetime.utcnow()

        item['last_post'] = dateparser.parse(thread.xpath(
            'descendant::span[@class="smalltext"]'
        ).xpath('normalize-space()').extract_first().split(' by')[0],
                                             settings={'TIMEZONE': 'UTC'})

        return self.verify_date(item, 'last_post')

    def parse_comment(self, response, comment):
        item = Comment()
        item['author'] = comment.xpath(
            'descendant::td[@class="poster_info"]/b/a/text()'
        ).extract_first()

        if not item['author']:
            item['author'] = 'Guest'

        item['text'] = comment.xpath(
            'descendant::div[@class="post"]'
        ).xpath('normalize-space()').extract_first()

        item['timestamp'] = dateparser.parse(comment.xpath(
            'descendant::table/descendant::div[@class="smalltext"]'
        ).xpath('normalize-space()').extract_first().split('Last')[0],
                                             settings={'TIMEZONE': 'UTC'})

        item['id'] = comment.xpath(
            'descendant::div[starts-with(@id, "subject")]/@id'
        ).extract_first().split('_')[-1]

        item['board'] = response.meta.get('board')

        item['thread'] = response.meta.get('thread')

        return self.verify_date(item, 'timestamp')

    def verify_date(self, item, time_item):
        # Handle race condition - post may have been retrieved before
        # midnight but processed here shortly after midnight resulting in
        # the translation of 'Today' to datetime being off by one day

        if item[time_item] > datetime.utcnow():
            item[time_item] = item[time_item].shift(days=-1)

        return item
