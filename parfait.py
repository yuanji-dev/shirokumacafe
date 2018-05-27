# coding: utf-8

import csv
import glob
import pysubs2
import re

from collections import defaultdict

from pysubs2.time import ms_to_str

STYLE_BLACKLIST = ['警示广告', '制作成员', '白熊警示广告', '白熊制作成员']


def extract_dialogues(subtitle):
    sub = pysubs2.load(subtitle)
    events = sorted(sub.events, key=lambda e: e.start)
    d = defaultdict(list)
    for event in filter(lambda e: e.text and e.style not in STYLE_BLACKLIST,
                        events):
        d[event.start].append(event)
    return d


def main():
    subtitles = sorted(glob.glob('subtitles/*'))
    for subtitle in subtitles:
        dialogue_name = subtitle.replace('subtitles', 'dialogues_1').replace(
            '.ass', '.csv')
        with open(dialogue_name, 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([
                'start', 'end', 'is_op', 'is_ed', 'is_next', 'cn_text',
                'jp_text'
            ])
            for _, v in extract_dialogues(subtitle).items():
                start = ms_to_str(v[0].start, True)
                end = ms_to_str(v[0].end, True)
                if len(v) > 1:
                    cn_text = v[1].plaintext.replace('\n', '')
                    cn_style = v[1].style
                    jp_text = v[0].plaintext.replace('\n', '')
                    jp_style = v[0].style
                else:
                    cn_text = v[0].plaintext.replace('\n', '')
                    cn_style = v[0].style
                    jp_text = ''
                    jp_style = ''

                style = cn_style + jp_style
                is_op = 'OP' in style.upper()
                is_ed = 'ED' in style.upper() or '片尾' in style
                is_next = '预告' in style
                csv_writer.writerow(
                    [start, end, is_op, is_ed, is_next, cn_text, jp_text])
            print('[SUCCESS] %s done.' % dialogue_name)


if __name__ == '__main__':
    main()
