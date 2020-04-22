from scrapy import Spider
from scrapy.selector import Selector
from crawl.items import Board, Thread, Comment
from datetime import datetime
from scrapy.utils.project import get_project_settings
import json

settings = get_project_settings()


class FourChanSpider(Spider):
    name = 'fourchan'
    boards_to_crawl = [
        'biz',
    ]

    def parse(self, response):
        response_data = self._normalize_response(response)

        boards = self._check_list(response_data.get('boards'))
        for board in boards:
            item = self.parse_board(response, board)
            yield item

            if item['id'] in self.boards_to_crawl:

                yield response.follow(
                    item['url'],
                    callback=self.parse,
                    meta={'board': item['id']}
                )

        if response.meta.get('board') in self.boards_to_crawl:

            threads = self._check_list(response_data.get('threads'))
            for thread in threads:
                item = self.parse_thread(response, thread)
                yield item
                yield response.follow(
                    item['url'],
                    callback=self.parse,
                    meta={
                        'thread': item['id'],
                        'board': response.meta.get('board'),
                    }
                )
            comments = self._check_list(response_data.get('posts'))
            for comment in comments:
                item = self.parse_comment(response, comment)
                if item is not None:
                    yield item

    def parse_board(self, response, board):
        item = Board()

        item['name'] = board['title']
        item['id'] = board['board']
        item['url'] = ('http://a.4cdn.org/{board_id}/catalog.json').format(
                           board_id=item['id'])
        item['description'] = Selector(text=board['meta_description']).xpath(
            'normalize-space()').extract_first()

        return item

    def parse_thread(self, response, thread):
        item = Thread()
        item['title'] = thread.get('sub')
        if item['title'] is None:
            item['title'] = ''

        item['id'] = thread['no']

        item['author'] = thread['id']

        item['board'] = response.meta.get('board')

        item['url'] = ('http://a.4cdn.org/'
                       '{board_id}/thread/{thread_id}.json').format(
                           board_id=item['board'], thread_id=item['id'])

        return item

    def parse_comment(self, response, comment):
        if comment.get('com') is None:
            return None
        item = Comment()
        item['author'] = comment['id']
        item['text'] = Selector(text=comment['com']).xpath(
            'normalize-space()').extract_first()

        item['timestamp'] = datetime.utcfromtimestamp(comment['time'])

        item['id'] = comment['no']

        item['board'] = response.meta.get('board')

        item['thread'] = response.meta.get('thread')

        return item

    @staticmethod
    def _normalize_response(response):

        response_data = json.loads(response.text)
        if type(response_data) == list:
            threads = []
            for page in response_data:
                threads += page['threads']

            return {'threads': threads}

        return response_data

    @staticmethod
    def _check_list(list):
        if list is None:
            return []
        else:
            return list
