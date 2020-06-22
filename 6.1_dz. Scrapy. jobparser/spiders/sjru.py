# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.f-test-link-Dalshe::attr(href)').extract_first()
        vacancy_links = response.css('div._1NAsu a._2JivQ::attr(href)').extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacansy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response:HtmlResponse):
        date = response.css('div._183s9 span::text').extract()
        name_job = response.css('h1::text').extract_first()
        salary = response.css('span.ZON4b span._2Wp8I::text').extract()
        company = response.css('h2.PlM3e::text').extract()
        city = response.css('span._6-z9f span::text').extract()
        link = response.url
        yield JobparserItem(date=date, name=name_job, salary=salary, company=company, city=city, link=link)