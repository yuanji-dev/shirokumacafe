# coding: utf-8

import os
import csv
import glob
import subprocess
import sys


def screenshot(ts, src, dst):
    cmd = [
        'ffmpeg', '-ss', ts, '-i', src, '-y', '-f', 'image2', '-vframes', '1',
        dst
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    sys.stdout.buffer.write(res.stdout)


def main():
    dialogues = glob.glob('dialogues/*')
    dialogues.sort()
    for dialogue in dialogues:
        dst_dir = 'images/%s' % os.path.split(dialogue)[-1].replace('.csv', '')
        src = 'videos/%s' % os.path.split(dialogue)[-1].replace('.csv', '.mkv')
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        with open(dialogue) as f:
            csv_reader = csv.reader(f)
            for ts, _ in csv_reader:
                dst = os.path.join(dst_dir, '%s.jpg' % ts)
                screenshot(ts, src, dst)


if __name__ == '__main__':
    main()
