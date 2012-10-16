#-*- coding:utf-8 -*-

import os
import shutil 


#批量移动文件夹下面的文件夹到某个指定的目录
def move_batch_folder_to_some_dirctory(source_path,target_path):
    if not os.path.isdir(source_path) or not os.path.isdir(target_path):
        return

    path_content = os.listdir(source_path)
    for i in path_content:
        child_path = os.path.join(source_path,i)
        if os.path.isdir(child_path):
            try:
                shutil.move(child_path,target_path)
            except:
                raise


#批量移动文件夹下面的文件到某个指定的目录
def move_batch_file_to_some_dirctory(source_path,target_path):
    if not os.path.isdir(source_path) or not os.path.isdir(target_path):
        return

    path_content = os.listdir(source_path)
    for i in path_content:
        child_path = os.path.join(source_path,i)
        if os.path.isfile(child_path):
            try:
                shutil.move(child_path,target_path)
            except:
                raise

