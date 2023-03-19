#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: russionbear
# @file: image_helper.py
# @time: 3/15/2023 1:06 PM
import os
import re
import shutil

from PIL import Image


def split_image_by_size(path, size):
    img = Image.open(path).convert('RGB')
    it = 1
    for y in range(img.size[1]//size[1]):
        for x in range(img.size[0]//size[0]):
            dot_i = path.rindex('.')
            img.crop((x*size[0], y*size[1], x*size[0]+size[0], y*size[1]+size[1])).save(path[:dot_i]+f'_{it}.png')
            it += 1
    print(img)


def _single1(src_dir, tar_dir, size):
    for f in os.listdir(src_dir):
        if re.match(r'.*\.png', f) is None:
            continue
        f_names = f.split('.')[0].split('_')

        try:
            os.mkdir(os.path.join(tar_dir, f"unit.{f_names[-1]}"))
        except FileExistsError:
            shutil.rmtree(os.path.join(tar_dir, f"unit.{f_names[-1]}"))
            os.mkdir(os.path.join(tar_dir, f"unit.{f_names[-1]}"))

        f_path = os.path.join(src_dir, f)
        img = Image.open(f_path).convert('RGBA')
        it = 0
        colors = ['red', 'blue', 'yellow', 'green']
        for y in range(img.size[1] // size[1]):
            for x in range(img.size[0] // size[0]):
                if it % 2 == 1:
                    it += 1
                    continue
                else:
                    it += 1
                img.crop((x * size[0], y * size[1], x * size[0] + size[0], y * size[1] + size[1]))\
                    .convert("RGBA").save(os.path.join(tar_dir, f"unit.{f_names[-1]}", f'{colors[it//2]}.png'))
        img.crop((0, 0, size[0], size[1])).convert('L').convert("RGBA") \
            .save(os.path.join(tar_dir, f"unit.{f_names[-1]}", f'none.png'))
        shutil.copy(r'E:\workspace\game_lab\qins_moon\res\resource\test\demo\advw\sprite\building.city\meta.yml',
                    os.path.join(tar_dir, f"unit.{f_names[-1]}", f'meta.yml'))
        print(img)


if __name__ == '__main__':
    # split_image_by_size(r'E:\workspace\game_lab\tmp\battle\unit\battle_unit_gunnery.png', (100, 100))
    _single1(r'E:\workspace\game_lab\tmp\battle\unit',
             r'E:\workspace\game_lab\qins_moon\res\resource\test\demo\advw\sprite', (100, 100))
