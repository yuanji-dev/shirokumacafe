# coding: utf-8

import os
import csv
import glob
import subprocess
import sys
from multiprocessing import Pool
from pysubs2.time import TIMESTAMP, timestamp_to_ms, ms_to_str


def screenshot(start, end, src, dst):
    cmd = [
        'ffmpeg', '-ss', start, '-to', end, '-i', src, '-y', '-vf',
        'scale=800:-1', '-r', '10', dst
    ]
    subprocess.run(cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)


def generate_gifs(dialogue):
    result = []
    with open(dialogue) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for start, end, is_op, is_ed, is_next, _, _ in csv_reader:
            if any([eval(is_op), eval(is_ed), eval(is_next)]):
                continue
            start = timestamp_to_ms(TIMESTAMP.match(start).groups())
            end = timestamp_to_ms(TIMESTAMP.match(end).groups())
            result.append((start, end))

    r = []
    i, j = 0, 1
    delta = []
    delta_2 = []

    for idx, (start, end) in enumerate(result[1:]):
        delta.append(start - result[idx][1])
    delta = list(filter(lambda d: d > 150 and d <= 2500, delta))
    span_avg = sum(delta) / len(delta)
    print('span: %s' % span_avg)

    while i < len(result):
        si, ei = result[i]

        while j < len(result):
            sj, ej = result[j]
            if sj - ei < span_avg:
                ei = ej
                i = j
            else:
                break
            j += 1

        p = (si, ei)
        delta_2.append(ei - si)
        r.append(p)
        i += 1
        j = i + 1

    duration_avg = sum(delta_2) / len(delta_2)
    print('duration: %s' % duration_avg)

    r = list(filter(lambda v: 3000 < v[1] - v[0] < duration_avg * 1.5, r))

    for i, (start, end) in enumerate(r):
        start = ms_to_str(start, True)
        end = ms_to_str(end, True)
        dst = '%s-%s.gif' % (start.replace(':', '_'), end.replace(':', '_'))
        src = 'videos/%s' % os.path.split(dialogue)[-1].replace('.csv', '.mkv')
        dst_dir = 'gifs/%s' % os.path.split(dialogue)[-1].replace('.csv', '')
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        dst = os.path.join(dst_dir, dst)
        print(start, end, i, dst)
        screenshot(start, end, src, dst)
        try:
            stat = os.stat(dst)
            if stat.st_size >= 5 * 1024 * 1024:
                os.remove(dst)
        except:
            pass


def main():
    dialogues = glob.glob('dialogues_1/*')
    dialogues.sort()
    with Pool(4) as p:
        p.map(generate_gifs, dialogues)


if __name__ == '__main__':
    main()
