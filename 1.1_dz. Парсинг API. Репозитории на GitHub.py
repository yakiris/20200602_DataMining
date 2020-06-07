# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests

user = 'yakiris'
main_link = 'https://api.github.com/users/' + user + '/repos'
response = requests.get(main_link)
data = response.json()

with open('1.1_dz. GitHub_repos.json', 'wb') as f:
    f.write(response.content)

print(f'Список репозиториев пользователя {user}:')
for i in data:
    print(f'- {i["name"]}')