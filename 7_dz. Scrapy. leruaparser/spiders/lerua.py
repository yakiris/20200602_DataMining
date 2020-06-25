# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lerua.leruaparser.items import LeruaparserItem
from scrapy.loader import ItemLoader

class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath('//div[@class="next-paginator-button-wrapper"]/a')
        links = response.xpath('//div[@class="product-name"]/a')
        for link in links:
            yield response.follow(link, callback=self.parse_link)
        yield response.follow(next_page, callback=self.parse)

    def parse_link(self, response:HtmlResponse):
        loader = ItemLoader(item=LeruaparserItem(), response=response)
        loader.add_css('name', 'h1::text')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//uc-pdp-price-view[@slot="primary-price"]//span[@slot="price"]/text()')
        loader.add_xpath('photos', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('param_key','//dl//dt/text()')
        loader.add_xpath('param_value', '//dl//dd/text()')
        yield loader.load_item()

