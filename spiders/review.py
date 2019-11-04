# -*- coding: utf-8 -*-
import scrapy
from jtnews.items import Reviewer, Review
import jtnews.settings as settings
import re
import time


class ReviewSpider(scrapy.Spider):
    name = 'review'
    allowed_domains = ['jtnews.jp']
    start_urls = [
        'https://www.jtnews.jp/cgi-bin_o/revrank.cgi?RANK_KIND=5&YEAR=1{}'
        .format(str(1890 + i * 10)) for i in range(2)
    ]
    request_count = 0

    def parse(self, response):
        self.logger.info('A response from %s', response.url)
        for tr in response.xpath('/html/body/table[2]/tr/td[2]/table[1]/tr/td/table/tr'):
            if not tr.xpath('td'):
                continue
            review_count = tr.xpath('td[5]/font/text()').extract()[0].replace('人', '')
            # reviewが多すぎるため、ある程度のreview数がないとskip
            if int(review_count) < settings.MIN_REVIEW_COUNT:
                continue
            movie_url = response.urljoin(tr.xpath('td[1]/a/@href').extract()[0])

            yield scrapy.Request(movie_url, callback=self.parse_review)

    def parse_review(self, response):
        self.request_count += 1
        if self.request_count % settings.REQUEST_COUNT_FOR_DELAY == 0:
            time.sleep(settings.REQUEST_DELAY)
        self.logger.info('Movie: %s', response.url)
        fonts = response.xpath('/html/body/table[2]/tr/td[2]/font[@color="#000088"]')
        title = response.xpath('/html/body/center[1]/table/tr[1]/td[1]/table/tr[1]/th/h1/a/text()').extract()[0]
        for font in fonts:
            nodes = font.xpath('following-sibling::node()')
            texts = nodes.extract()
            review = Review()
            review['reviewer_name'] = font.xpath('following-sibling::font[@color="BLUE"][1]/a/text()').extract()[0]
            review['title'] = title
            point_text = font.xpath('following-sibling::font[@color="GREEN"][1]/text()')
            review['point'] = point_text.extract()[0].replace('点', '')
            review['body'] = ''
            has_br = True
            for string in texts:
                if 'color="RED"' in string:
                    continue # ネタバレ
                elif string == '<br>':
                    has_br = True # 改行
                elif not has_br:
                    break # 文章の次に改行がなければbreak
                else:
                    review['body'] += string
                    has_br = False

            reviewed_on_index = [i for i, x in enumerate(texts) if x.startswith('<font color="GREEN">')][0] + 1
            review['reviewed_on'] = re.search('(\d+)-(\d+)-(\d+)', texts[reviewed_on_index]).group()
            yield review

        
        # Request
        xp = response.xpath('/html/body/table[2]/tr/td[2]/center[1]/table/tr/td')
        th = xp.xpath('table/tr/th/font[@color="red"]/..')
        href = th.xpath('following-sibling::td[1]/a/@href') or th.xpath('../following-sibling::tr[1]/td[1]/a/@href')
        if not href:
            return
        next_url = response.urljoin(href.extract()[0])
        yield scrapy.Request(next_url, callback=self.parse_review)
