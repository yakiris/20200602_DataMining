# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=&st=searchVacancy&text=Python&fromSearch=true&from=suggest_post']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        vacancy_links = response.css('div.vacancy-serp-item a.HH-LinkModifier::attr(href)').extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacansy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response:HtmlResponse):
        date = response.css('p.vacancy-creation-time::text').extract()
        name_job = response.css('h1::text').extract_first()
        salary = response.css('p.vacancy-salary span::text').extract()
        company = response.css('span.bloko-section-header-2::text').extract()
        city = response.xpath(".//p[@data-qa='vacancy-view-location']//text()").extract()
        link = response.url
        yield JobparserItem(date=date, name=name_job, salary=salary, company=company, city=city, link=link)