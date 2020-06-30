from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['insta_scrapy']

follow = db.follow
node = db.node

# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
for fol in follow.find({'user_id': '588273420', 'following_id': None}, {'follower_name':1}):
     pprint(fol)
print('*' * 100)
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
for fol in follow.find({'user_id': '588273420', 'follower_id': None}, {'following_name':1}):
     pprint(fol)
