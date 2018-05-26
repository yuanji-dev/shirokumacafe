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
STATUS_URL = 'https://api.douban.com/v2/lifestream/statuses'
COMMENT_URL = 'https://api.douban.com/v2/lifestream/status/%s/comments'
USER_AGENT = 'api-client/2.0 com.douban.shuo/2.2.7(123) Android/22 product/PD1602 vendor/vivo model/vivo X7'

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
        'User-Agent': USER_AGENT,
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

        data = {'version': 2, 'text': text}

        r = requests.post(
            STATUS_URL, headers=build_headers(), files=files, data=data)
        print(r.content)
        if not r.status_code == requests.codes.ok:  #pylint: disable=E1101
            fresh_access_token()
            return False, r.json()
        return True, r.json()


def create_comment(status_id, comment):
    url = COMMENT_URL % status_id
    data = {'text': comment}
    r = requests.post(url, headers=build_headers(), data=data)
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