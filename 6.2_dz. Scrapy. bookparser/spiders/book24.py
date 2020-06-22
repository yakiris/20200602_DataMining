# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from book.bookparser.items import BookparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=программирование']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a._text::attr(href)').extract_first()
        book_links = response.css('div.catalog-products__list div.book__content a.book__title-link::attr(href)').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.css('h1::text').extract_first()
        key = response.css('div.item-tab__chars-item a.item-tab__chars-link::text').extract()
        feature = response.css('div.item-tab__chars-item span::text').extract()
        rating = response.css('span.rating__rate-value::text').extract_first()
        price = response.css('div.item-actions__price b::text').extract_first()
        link = response.url
        yield BookparserItem(name=name, feature=feature, key=key, rating=rating, price=price, link=link)
