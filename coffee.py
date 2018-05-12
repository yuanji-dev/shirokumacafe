# coding: utf-8

import csv
import glob
import pysubs2
import re

from collections import defaultdict

STYLE_BLACKLIST = ['警示广告', '制作成员', '白熊警示广告', '白熊制作成员']

def extract_dialogues(subtitle):
    sub = pysubs2.load(subtitle)
    events = sub.events
    d = defaultdict(list)
    for event in filter(lambda e: e.text and e.style not in STYLE_BLACKLIST, events):
        d[event.start].append(event)

    merged_events = []
    for k, v in d.items():
        e = v[0]
        text = u' *** '.join(map(lambda i: i.text, v)).replace(r'\N', '')
        e.text = re.sub(r'{.*?}', '', text)
        merged_events.append(e)

    return sorted(merged_events, key=lambda e: e.start)


def main():
    subtitles = glob.glob('subtitles/*')
    for subtitle in subtitles:
        events = extract_dialogues(subtitle)
        dialogue_name = subtitle.replace('subtitles', 'dialogues').replace('.ass', '.csv')
        with open(dialogue_name, 'w') as f:
            csv_writer = csv.writer(f) 
            for event in events:
                time = float((event.start + event.end)) / 2 / 1000 # msec => sec
                if time == 0.0:
                    continue
                text = event.text
                csv_writer.writerow((time, text))
            print('[SUCCESS] %s done.' % dialogue_name)
        
if __name__ == '__main__':
    main()