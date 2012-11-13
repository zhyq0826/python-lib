#-*- coding:utf-8 -*-

import os
import shutil 
import time
import platform


def find_same_file(path):

    if not os.path.isdir(path):
        return

    content = os.listdir(path)
    content.sort()
    for i in content:
        file_path = os.path.join(path,i)
        if i.endswith('1.mp3'):
            os.remove(file_path)

if __name__ == '__main__':
    path = ur'/home/zhyq/音乐/baidumusic'
    find_same_file(path)
