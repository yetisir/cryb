import time
import logging
import datetime
import asyncio
import html
import logging
import re

from sqlalchemy import func, desc

from ..config import config
from . import base
from . import tables


class RedditCrawler(base.Crawler):
    base_url = 'http://api.reddit.com/r'
    forum_id = 'reddit'


class Boards(RedditCrawler):
    async def get(self):
        boards = []

        for board_id in config.reddit_boards:
            board = Board(id=board_id)
            boards.append(board)

        await asyncio.gather(*[board.get() for board in boards])


class Board(RedditCrawler):
    def __init__(self, id):
        self.id = id

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    @property
    def name(self):
        return self.raw_data['data']['title']

    @property
    def description(self):
        return self.normalize_text(self.raw_data['data']['public_description'])

    async def get_info(self):
        url = f'{self.base_url}/{self.id}/about'
        self.raw_data = await self.request(url)
        self.save()

    async def get(self):
        await self.get_info()
        saved_threads = self.get_saved_threads()

        for target in config.targets:
            if target.domain in self.base_url:
                chunksize = target.concurrency
                break
        after = 'start'
        while after:
            response = await self.hot_threads(after=after)
            after = response['after']
            threads = response['children']
            for i in range(0, len(threads), chunksize):
                await self.get_threads(threads[i:i+chunksize], saved_threads)

    async def hot_threads(self, after=None):
        url_parameters = self.api_parameters(
            limit=100,
            after=after,
        )
        url = f'{self.base_url}/{self.id}/hot/{url_parameters}'
        response = await self.request(url)
        return response['data']

    async def get_threads(self, threads, saved_threads):
        tasks = []
        for thread in threads:
            if thread['kind'] != 't3':
                continue
            thread = Thread(raw_data=thread['data'], board_id=self.id)
            saved_comments = saved_threads.get(thread.id)
            if saved_comments:
                if saved_comments == thread.comments:
                    logging.info(f'Skipping Reddit thread {thread.id}')
                    continue
            tasks.append(thread.get())
        await asyncio.gather(*tasks)

    def get_saved_threads(self):
        threads = tables.Database.session.query(
            tables.reddit.Thread.id,
            tables.reddit.Thread.comments,
        ).all()
        return {thread[0]: thread[1] for thread in threads}

    def save(self):
        schema = tables.reddit.BoardSchema()
        tables.Database.session.add(schema.load(self.data))
        tables.Database.session.commit()


class Thread(RedditCrawler):
    def __init__(self, raw_data, board_id):
        self.raw_data = raw_data
        self.board_id = board_id

    @property
    def data(self):

        return {
            'id': self.id,
            'board_id': self.board_id,
            'author': self.author,
            'title': self.title,
            'text': self.text,
            'created_on': self.created_on,
            'comments': self.comments,
        }

    @property
    def id(self):
        return self.raw_data['id']

    @property
    def created_on(self):
        return self.timestamp_to_iso(self.raw_data['created_utc'])

    @property
    def author(self):
        return self.raw_data['author']

    @property
    def title(self):
        return self.raw_data['title']

    @property
    def text(self):
        return self.normalize_text(self.raw_data['selftext'])

    @property
    def comments(self):
        return int(self.raw_data['num_comments'])

    async def get(self):
        self.save()
        url = f'{self.base_url}/{self.board_id}/comments/{self.id}'
        response = await self.request(url)
        comments = response[1]['data']['children']
        if response == 404:
            return
        for comment in comments:
            if comment['kind'] != 't1':
                continue
            Comment(comment['data'], self.id).save()

        logging.info(f'Downloaded Reddit thread {self.id}')

    def save(self):
        schema = tables.reddit.ThreadSchema()
        tables.Database.session.add(schema.load(self.data))
        tables.Database.session.commit()


class Comment(RedditCrawler):

    def __init__(self, raw_data, thread_id, parent=None):
        self.thread_id = thread_id
        self.raw_data = raw_data
        self.parent = parent

        replies = self.raw_data['replies']
        if replies:
            for reply in replies['data']['children']:
                if 'replies' not in reply['data'].keys():
                    continue
                Comment(reply['data'], thread_id, self.id).save()

    @property
    def data(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'author': self.author,
            'created_on': self.created_on,
            'parent_comment_id': self.parent,
            'text': self.text,
        }

    @property
    def id(self):
        return str(self.raw_data['id'])

    @property
    def author(self):
        return self.raw_data['author']

    @property
    def text(self):
        return self.raw_data['body']

    @property
    def created_on(self):
        return self.timestamp_to_iso(self.raw_data['created_utc'])

    def save(self):
        schema = tables.reddit.CommentSchema()
        tables.Database.session.add(schema.load(self.data))
        tables.Database.session.commit()
