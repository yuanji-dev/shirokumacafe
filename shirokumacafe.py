# coding: utf-8

import os
import requests
import time
import glob
import random

from config import API_KEY, API_SECRET, USERNAME, PASSWORD

API_TOKEN_URL = 'https://frodo.douban.com/service/auth2/token'
STATUS_URL = 'https://api.douban.com/v2/lifestream/statuses'
USER_AGENT = 'api-client/2.0 com.douban.shuo/2.2.7(123) Android/22 product/PD1602 vendor/vivo model/vivo X7'

PWD = os.path.dirname(os.path.abspath('__file__'))
IMAGE_DIR = os.path.join(PWD, 'images')
TOKEN_FILE = os.path.join(PWD, 'token')

def pick_image():
    episode_dir = random.choice(glob.glob(os.path.join(IMAGE_DIR, '*')))
    return random.choice(glob.glob(os.path.join(episode_dir, '*')))

def get_access_token():
    with open(TOKEN_FILE) as f:
        return f.read()

def fresh_access_token():
    data = {
        'client_id': API_KEY,
        'client_secret': API_SECRET,
        'redirect_uri': '',
        'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD,
    }
    r = requests.post(API_TOKEN_URL, data=data)
    r.raise_for_status()
    access_token = r.json()['access_token']
    with open(TOKEN_FILE, 'w') as f:
        f.write(access_token)

def create_status():
    access_token = get_access_token()
    with open(pick_image(), 'rb') as image:
        files = {
            'image': image
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Authorization': 'Bearer %s' % access_token,
        }

        data = {
            'version': 2,
            'text': ''
        }

        r = requests.post(STATUS_URL, headers=headers, files=files, data=data)
        print(r.content)
        if not r.status_code == requests.codes.ok:
            fresh_access_token()
            return False
        return True

def main():
    if not create_status():
        time.sleep(2)
        create_status()

if __name__ == '__main__':
    main()