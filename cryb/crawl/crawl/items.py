# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Thread(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    board = scrapy.Field()
    # timestamp = scrapy.Field()


class Comment(scrapy.Item):
    id = scrapy.Field()
    author = scrapy.Field()
    text = scrapy.Field()
    timestamp = scrapy.Field()
    thread = scrapy.Field()
    board = scrapy.Field()


class Board(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
