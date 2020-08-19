import time
import logging
import datetime
import asyncio
import html
import logging
import re

from sqlalchemy import func, desc
from bs4 import BeautifulSoup

from ..config import config
from . import base
from . import tables


class FourChanCrawler(base.Crawler):
    base_url = 'http://a.4cdn.org/'
    forum_id = 'fourchan'

    def normalize_text(self, text):
        return BeautifulSoup(text).text

    def timestamp_to_iso(self, timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).isoformat()


class Boards(FourChanCrawler):
    async def get(self):
        url = f'{self.base_url}/boards.json'
        board_list = await self.request(url)

        boards = []

        if 'boards' not in board_list.keys():
            return
        for raw_data in board_list['boards']:
            board = Board(
                id=raw_data['board'],
                name=raw_data['title'],
                description=self.normalize_text(raw_data['meta_description']),
            )
            board.save()

            logging.info(f'Downloaded 4Chan {board.id} board metadata')
            if board.id in config.fourchan_boards:
                boards.append(board)

        await asyncio.gather(*[board.get() for board in boards])


class Board(FourChanCrawler):
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    async def update_thread_status(self):
        archived_threads = set(await self.archive_list())
        active_threads = set(self.get_active_threads().keys())

        update_threads = set.intersection(archived_threads, active_threads)
        # tables.db_session.query(tables.Thread).filter(tables.Thread.id == '21630117').update(
        tables.db_session.query(tables.Thread).filter(tables.Thread.id.in_(update_threads)).update(
            {tables.Thread.active: False}, synchronize_session='fetch')
        tables.db_session.commit()

    async def get(self):
        await self.update_thread_status()
        await self.get_active()
        # await self.get_archive()

    async def get_active(self):
        url = f'{self.base_url}/{self.id}/threads.json'
        pages = await self.request(url)
        for page in pages:
            await self.download_page(page)

    async def download_page(self, page):
        active_threads = self.get_active_threads()
        threads = []
        for thread in page['threads']:
            thread_id = thread['no']
            timestamp = active_threads.get(str(thread_id))
            if not timestamp:
                threads.append(thread_id)
                continue
            if timestamp < datetime.datetime.utcfromtimestamp(thread['last_modified']):
                threads.append(thread_id)
            else:
                logging.info(f'Skipping 4Chan thread {thread_id}')
        await self.get_threads(threads, active=True)

    async def get_archive(self):
        for target in config.targets:
            if target.domain in self.base_url:
                chunksize = target.concurrency
                break
        threads = await self.archive_list()
        for i in range(0, len(threads), chunksize):
            await self.get_threads(threads[i:i+chunksize], active=False)

    async def get_threads(self, threads, active):
        tasks = []
        archived_threads = self.get_archived_threads()
        for thread_id in threads:
            if thread_id in archived_threads:
                continue
            thread = Thread(id=thread_id, board_id=self.id, active=active)
            tasks.append(thread.get())
        await asyncio.gather(*tasks)

    async def archive_list(self):
        url = f'{self.base_url}/{self.id}/archive.json'
        archive = await self.request(url)
        return [str(thread) for thread in archive]

    def get_archived_threads(self):
        threads = tables.db_session.query(tables.Thread.id).filter(
            tables.Thread.active == False).all()
        return [thread[0] for thread in threads]

    def get_active_threads(self):
        threads = tables.db_session.query(tables.Thread.id, tables.Thread.updated_on).filter(
            tables.Thread.active == True).all()
        return {thread[0]: thread[1] for thread in threads}

    def save(self):
        schema = tables.BoardSchema()
        tables.db_session.add(schema.load(self.data))
        tables.db_session.commit()


class Thread(FourChanCrawler):
    def __init__(self, id, board_id, active):
        self.id = str(id)
        self.board_id = board_id

        self.active = active

    @property
    def updated_on(self):
        if not len(self.comments):
            time = self.head['time']
        else:
            time = max(comment['time'] for comment in self.comments)

        return self.timestamp_to_iso(time)

    @property
    def comments(self):
        return self.raw_data['posts'][1:]

    @property
    def data(self):

        return {
            'id': self.id,
            'board_id': self.board_id,
            'author': self.author,
            'title': self.title,
            'text': self.text,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'active': self.active,
        }

    @property
    def created_on(self):
        return self.timestamp_to_iso(self.head['time'])

    @property
    def author(self):
        return self.head['id']

    @property
    def head(self):
        return self.raw_data['posts'][0]

    @property
    def title(self):
        title = self.head.get('sub')
        return self.normalize_text(title) if title else ''

    @property
    def text(self):
        text = self.head.get('com')
        return self.normalize_text(text) if text else ''

    async def get(self):
        url = f'{self.base_url}/{self.board_id}/thread/{self.id}.json'
        self.raw_data = await self.request(url)
        if self.raw_data == 404:
            return
        if 'posts' not in self.raw_data.keys():
            return
        self.save()
        for comment in self.comments:
            Comment(comment, self.id).save()

        active_string = 'active' if self.active else 'archived'
        logging.info(f'Downloaded 4Chan thread {self.id} ({active_string})')

    def save(self):
        schema = tables.ThreadSchema()
        tables.db_session.add(schema.load(self.data))
        tables.db_session.commit()


class Comment(FourChanCrawler):
    parent_regex = re.compile('>>[0-9]{7,8}')

    def __init__(self, raw_data, thread_id):
        self.thread_id = thread_id
        self.raw_data = raw_data

    @property
    def data(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'author': self.author,
            'created_on': self.created_on,
            'parent_comment_id': self.parent,
            'text': self.text[len(self.parent)+2:] if self.parent else self.text,
        }

    @property
    def id(self):
        return str(self.raw_data['no'])

    @property
    def author(self):
        return self.raw_data['id']

    @property
    def text(self):
        text = self.raw_data.get('com')
        return self.normalize_text(text) if text else ''

    @property
    def created_on(self):
        return self.timestamp_to_iso(self.raw_data['time'])

    @property
    def parent(self):
        match = self.parent_regex.search(self.text)
        if match:
            return match.group()[2:]
        else:
            return None

    def save(self):
        schema = tables.CommentSchema()
        tables.db_session.add(schema.load(self.data))
        tables.db_session.commit()
