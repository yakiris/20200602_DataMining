# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from book.bookparser.items import BookparserItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/программирование/']

    def parse(self, response):
        next_page = response.css('a.pagination-next__text::attr(href)').extract_first()
        book_links = response.css('a.product-title-link::attr(href)').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.css('h1::text').extract_first()
        author = response.css('div.authors a::text').extract_first()
        year = response.css('div.publisher::text').extract()
        publisher = response.css('div.publisher a::text').extract_first()
        rating = response.css('div.left div::text').extract_first()
        pages = response.css('div.pages2::text').extract()
        price = response.css('span.buying-price-val-number::text').extract_first()
        link = response.url
        yield BookparserItem(name=name, price=price, link=link, author=author, year=year, publisher=publisher, rating=rating, pages=pages)

