# -*- coding: utf-8 -*-
import scrapy
from jtnews.items import Reviewer


class ReviewerSpider(scrapy.Spider):
    name = 'reviewer'
    allowed_domains = ['jtnews.jp']
    start_urls = [
        'https://www.jtnews.jp/cgi-bin_o/revlist.cgi?PAGE_NO={}'.format(str(i))
        for i in range(1, 3)
    ]

    def parse(self, response):
        self.logger.info('A response from %s', response.url)
        for tr in response.xpath('/html/body/table[2]/tr/td[2]/table[2]/tr/td/table/tr'):
            if not tr.xpath('td'):
                continue
            reviewer = {}
            reviewer['id'] = tr.xpath('th[1]/font/text()').extract()[0]
            reviewer['name'] = tr.xpath('td[1]/a/text()').extract()[0]
            reviewer['review_count'] = tr.xpath('td[2]/text()').extract()[0]
            reviewer['last_reviewed_on'] = tr.xpath('td[3]/text()').extract()[0]
            reviewer_url = response.urljoin(tr.xpath('td[1]/a/@href').extract()[0])

            yield scrapy.Request(reviewer_url, callback=self.parse_reviewer,
                                 meta={'reviewer':reviewer})

    def parse_reviewer(self, response):
        self.logger.info('Reviewer: %s', response.url)
        reviewer = response.meta['reviewer']
        fonts = response.xpath('/html/body/table[2]/tr/td[2]/table[1]/tr/td/table/tr/th/font')
        for font in fonts:
            attr = font.xpath('text()').extract()[0]
            text = font.xpath('../following-sibling::td[1]/text()')
            if attr == '性別':
                reviewer['gender'] = text.extract()[0].replace('\r\n', '')
            elif attr == '年齢':
                reviewer['age'] = text.extract()[0].replace('\r\n', '')

        yield Reviewer(
            id=reviewer.get('id'),
            name=reviewer.get('name'),
            gender=reviewer.get('gender', ''),
            age=reviewer.get('age', ''),
            review_count=reviewer.get('review_count'),
            last_reviewed_on=reviewer.get('last_reviewed_on'),
        )
