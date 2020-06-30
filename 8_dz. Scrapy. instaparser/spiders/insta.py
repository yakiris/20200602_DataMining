# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_log_link = 'https://www.instagram.com/accounts/login/ajax/'
    insta_log = ''
    insta_pas = ''
    parse_user = '1cbitrix'

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = 'c76146de99bb02f6415203be841dd25a' # подписчики
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076' # подписки

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_log_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_log, 'enc_password': self.insta_pas},
            headers={'X-CSRFToken':csrf_token}
        )

    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            yield response.follow(
                f'/{self.parse_user}',
                callback=self.user_data_parse,
                cb_kwargs={'username': self.parse_user}
            )

    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'include_reel': 'true',
                     'fetch_mutual': 'false',
                     'first': 50}
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.user_follower_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})

    def user_following_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                            'user_id': user_id,
                            'variables': deepcopy(variables)})
        follows = j_data.get('data').get('user').get('edge_follow').get('edges')
        for follow in follows:
            item = InstaparserItem(
                user_id = user_id,
                follower_id = None,
                follower_name = None,
                following_id = follow['node']['id'],
                following_name = follow['node']['username'],
                node = follow['node'])
            yield item

    def user_follower_parse(self, response:HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_follower_parse,
                cb_kwargs={'username': username,
                            'user_id': user_id,
                            'variables': deepcopy(variables)})
        follows = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follow in follows:
            item = InstaparserItem(
                user_id = user_id,
                following_id = None,
                following_name = None,
                follower_id = follow['node']['id'],
                follower_name = follow['node']['username'],
                node = follow['node'])
            yield item

    # Получаем токен для авторизаци
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
