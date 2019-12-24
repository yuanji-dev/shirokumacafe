# coding: utf-8

import os
import csv
import time
import glob
import random
import base64
import hashlib
import hmac

from datetime import datetime, timedelta

import requests


from config import API_KEY, API_SECRET, USERNAME, PASSWORD


DEFAULT_UA = 'api-client/1 com.douban.frodo/6.9.0(148) Android/23 product/meizu_MX6 vendor/Meizu model/MX6 rom/flyme4 network/wifi platform/mobile'
DEFAULT_HOST = 'frodo.douban.com'

PWD = os.path.dirname(os.path.abspath('__file__'))
IMAGE_DIR = os.path.join(PWD, 'images')
GIF_DIR = os.path.join(PWD, 'gifs')
DIALOGUE_DIR = os.path.join(PWD, 'dialogues')
DIALOGUE_DIR_1 = os.path.join(PWD, 'dialogues_1')
TOKEN_FILE = os.path.join(PWD, 'token')

class DouBanApi:


    def __init__(self, api_key, api_secret, ua=DEFAULT_UA, host=DEFAULT_HOST):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ua = ua
        self.host = DEFAULT_HOST

    def create_status(self, text, image_path=None):
        data = {
            'text': text
        }
        if image_path:
            with open(image_path, 'rb') as image:
                files = {'image': image}
                r = self._request('post', '/api/v2/status/upload', files=files, need_login=True)

                data['image_urls'] = r['url']
        return self._request('post', '/api/v2/status/create_status', data=data, need_login=True)

    def create_comment(self, status_id, text):
        data = {
            'text': text
        }
        return self._request('post', '/api/v2/status/%s/create_comment' % status_id, data=data, need_login=True)

    def login(self, username, password):
        data = {
            'client_id': self.api_key,
            'client_secret': self.api_secret,
            'redirect_uri': 'frodo://app/oauth/callback/',
            'grant_type': 'password',
            'username': username,
            'password': password,
        }
        r = self._request('post', '/service/auth2/token', data=data)
        if not r:
            return
        access_token = r['access_token']
        with open(TOKEN_FILE, 'w') as f:
            f.write(access_token)

    @staticmethod
    def _get_access_token():
        with open(TOKEN_FILE) as f:
            return f.read()

    def _request(self, method, path, params=None, data=None, files=None, need_login=False):
        headers = {
            'User-Agent': self.ua,
        }
        if need_login:
            headers['Authorization'] = 'Bearer %s' % self._get_access_token()
        # 签名
        if params is None:
            params = {}
        params['_ts'] = str(int(time.time()))
        params['apikey'] = self.api_key
        sign_src = '&'.join([
            method.upper(),
            path.replace('/', '%2F'),
            params['_ts'],
        ])
        params['_sig'] = base64.b64encode(hmac.new(self.api_secret.encode('utf-8'), sign_src.encode(), hashlib.sha1).digest())
        url = 'https://' + self.host + path
        api_res = requests.request(method, url, params=params, data=data, files=files, headers=headers)
        if api_res.status_code == 200:
            return api_res.json()
        else:
            print(api_res.json())
            return None


def pick_image():
    # return path, text, comment
    dialogue = random.choice([p for p in glob.glob(os.path.join(DIALOGUE_DIR, '*')) if 'クリスマス' in p])
    episode = os.path.split(dialogue)[-1].replace('.csv', '')
    with open(dialogue) as f:
        csv_reader = csv.reader(f)
        ts_text_list = list(csv_reader)
        # 开头结尾选出一张，然后与正片一起随机挑选
        ts, text = random.choice(ts_text_list[23:-31])
        image_path = os.path.join(IMAGE_DIR, episode, '{ts}.jpg'.format(ts=ts))
        pos = str(timedelta(seconds=float(ts))).rstrip('0')
        comment = '{episode} @ {pos}'.format(episode=episode, pos=pos)
        return image_path, text, comment


def pick_gif():
    sub_gif_dir = random.choice([p for p in glob.glob(os.path.join(GIF_DIR, '*')) if 'クリスマス' in p])
    episode = os.path.split(sub_gif_dir)[-1]
    gif_path = random.choice(glob.glob(os.path.join(sub_gif_dir, '*')))
    gif_name = os.path.split(gif_path)[-1].replace('.gif', '')
    start, end = gif_name.replace('_', ':').split('-')
    comment = '{episode}  {start} ~ {end}'.format(
        episode=episode, start=start, end=end)
    text = find_gif_text(episode, start, end)
    return gif_path, text, comment


def find_gif_text(episode, start, end):
    print(start, end)
    dialogue = os.path.join(DIALOGUE_DIR_1, '{episode}.csv'.format(episode=episode))
    sentences = []
    is_matched = None
    with open(dialogue) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0] == start:
                is_matched = True

            if is_matched is not None:
                if is_matched:
                    sentences.append('- %s' % row[5])
                else:
                    break

            if row[1] == end:
                is_matched = False
    text = '\n'.join(sentences)
    return text if is_matched == False else ''

def get_access_token():
    with open(TOKEN_FILE) as f:
        return f.read()


douban_api = DouBanApi(API_KEY, API_SECRET)

def create_status(image_path, text):
    r = douban_api.create_status(text, image_path)
    if r:
        return True, r
    return False, None

def create_comment(status_id, comment):
    r = douban_api.create_comment(status_id, comment)
    print(r)

def main():
    if (datetime.now() + timedelta(seconds=10)).hour % 4 == 0:
        pick_method = pick_gif
    else:
        pick_method = pick_image
    image_path, text, comment = pick_method()
    if not os.path.exists(TOKEN_FILE):
        douban_api.login(USERNAME, PASSWORD)
    ok, result = create_status(image_path, text)
    if not ok:
        time.sleep(2)
        douban_api.login(USERNAME, PASSWORD)
        _, result = create_status(image_path, text)

    status_id = result.get('id')
    if status_id:
        time.sleep(1)
        create_comment(status_id, comment)


if __name__ == '__main__':
    main()
