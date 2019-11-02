# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Reviewer(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    gender = scrapy.Field()
    age = scrapy.Field()
    review_count = scrapy.Field()
    last_reviewed_on = scrapy.Field()

class Review(scrapy.Item):
    id = scrapy.Field()
    reviewer_name = scrapy.Field()
    title = scrapy.Field()
    point = scrapy.Field()
    body = scrapy.Field()
    reviewed_on = scrapy.Field()
