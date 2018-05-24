# coding: utf-8

import os
import csv
import requests
import time
import glob
import random

from datetime import timedelta

from config import API_KEY, API_SECRET, USERNAME, PASSWORD

API_TOKEN_URL = 'https://frodo.douban.com/service/auth2/token'

FRODO_USER_AGENT = 'api-client/1 com.douban.frodo/5.24.0(132) Android/22 product/PD1602 vendor/vivo model/vivo X7 rexxardev'
FRODO_UPLOAD_URL = 'https://frodo.douban.com/api/v2/status/upload'
FRODO_STATUS_URL = 'https://frodo.douban.com/api/v2/status/create_status'
FRODO_COMMENT_URL = 'https://frodo.douban.com/api/v2/status/%s/create_comment'

PWD = os.path.dirname(os.path.abspath('__file__'))
IMAGE_DIR = os.path.join(PWD, 'images')
DIALOGUE_DIR = os.path.join(PWD, 'dialogues')
TOKEN_FILE = os.path.join(PWD, 'token')


def pick_image():
    # return path, text, comment
    dialogue = random.choice(glob.glob(os.path.join(DIALOGUE_DIR, '*')))
    episode = os.path.split(dialogue)[-1].replace('.csv', '')
    with open(dialogue) as f:
        csv_reader = csv.reader(f)
        ts_text_list = list(csv_reader)
        # 开头结尾选出一张，然后与正片一起随机挑选
        ts, text = random.choice(
            [random.choice(ts_text_list[:23] + ts_text_list[-30:])] +
            ts_text_list[23:-31])
        image_path = os.path.join(IMAGE_DIR, episode, '{ts}.jpg'.format(ts=ts))
        pos = str(timedelta(seconds=float(ts))).rstrip('0')
        comment = '{episode} @ {pos}'.format(episode=episode, pos=pos)
        return image_path, text, comment


def get_access_token():
    with open(TOKEN_FILE) as f:
        return f.read()


def build_headers():
    return {
        'User-Agent': FRODO_USER_AGENT,
        'Authorization': 'Bearer %s' % get_access_token(),
    }


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


def create_status(image_path, text):
    with open(image_path, 'rb') as image:
        files = {'image': image}
        r = requests.post(
            FRODO_UPLOAD_URL, headers=build_headers(), files=files)
        if not r.status_code == requests.codes.ok:
            fresh_access_token()
            return False, r.json()

        data = {'text': text, 'image_urls': r.json()['url']}
        r = requests.post(FRODO_STATUS_URL, headers=build_headers(), data=data)
        return True, r.json()


def create_comment(status_id, comment):
    url = FRODO_COMMENT_URL % status_id
    data = {'text': comment}
    r = requests.post(url, headers=build_headers(), data=data)
    print(r.content)


def upload_image(image_path):
    with open(image_path, 'rb') as image:
        files = {'image': image}
        r = requests.post(
            FRODO_UPLOAD_URL, headers=build_headers(), files=files)
        print(r.content)


def main():
    image_path, text, comment = pick_image()
    ok, result = create_status(image_path, text)
    if not ok:
        time.sleep(2)
        _, result = create_status(image_path, text)

    status_id = result.get('id')
    if status_id:
        time.sleep(1)
        create_comment(status_id, comment)


if __name__ == '__main__':
    main()