# coding: utf-8

import requests


API_TOKEN_URL = 'https://frodo.douban.com/service/auth2/token'
STATUS_URL = 'https://api.douban.com/v2/lifestream/statuses'
USER_AGENT = 'api-client/2.0 com.douban.shuo/2.2.7(123) Android/22 product/PD1602 vendor/vivo model/vivo X7'

def login(username, password):
    data = {
        'client_id': '',
        'client_secret': '',
        'redirect_uri': '',
        'grant_type': 'password',
        'username': username,
        'password': password,
    }

    res = requests.post(API_TOKEN_URL, data=data)
    res.raise_for_status()
    #{'access_token': '', 'douban_user_name': '白熊咖啡馆', 'douban_user_id': '178473869', 'expires_in': 7775999, 'refresh_token': ''}
    return res.json()

def create_status():
    with open('./icon.jpg', 'rb') as image:
        files = {
            'image': image
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Authorization': 'Bearer %s',
        }

        data = {
            'version': 2,
            'text': 'ようこそ'
        }

        res = requests.post(STATUS_URL, headers=headers, files=files, data=data)
        print(res.content)
        print(res.json())

def main():
    print(login('', ''))
    create_status()

if __name__ == '__main__':
    main()