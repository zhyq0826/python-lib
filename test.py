#-*- coding:utf-8 -*-

import os
import shutil 
import time
import platform

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

#firefox netvideo 下载的豆瓣音乐文件 进行重命名和分类
#移动同一天下载的豆瓣mp3文件到 已时间命名的文件加
#所有的路径都是绝对路径
def move_douban_mp3_to_folder(path):
    '''
    move the same day download mp3 file to the same folder named by mp3 created time

    '''
    if not os.path.isdir(path):
        return
    
    print 'Start moving ...'

    system = platform.system

    #list all dirctory  content 
    contents = os.listdir(path)
    
    time_infor_dic ={}.fromkeys(('year','mon','day','hour','min','sec'),None)

    for i in contents:
        child_path = os.path.join(path,i)
        if os.path.isfile(child_path):
            
            #get file created time 
            file_stat = os.stat(child_path)
            
            stime = time.localtime(file_stat.st_ctime)
            
            time_infor_dic['year'] = getattr(stime, 'tm_year')
            time_infor_dic['mon'] = getattr(stime, 'tm_mon')
            time_infor_dic['day'] = getattr(stime, 'tm_mday') 
            time_infor_dic['hour'] = getattr(stime, 'tm_hour')
            time_infor_dic['min'] = getattr(stime, 'tm_min')
            time_infor_dic['sec'] = getattr(stime, 'tm_sec')
            
            #get file name and extendtion
            filename,extendtion= os.path.splitext(child_path)
            
            #remove dirctory name but reserved filename  format as:1953 - 豆瓣FM 必须注意文件类型
            #under linux system,filetype is marked by other infor not extendtion
            if system == 'Linux':
                true_file_name = ("%s%s")%(os.path.basename(filename)[0:-10],extendtion)
            elif system == 'Windows':
                true_file_name = ("%s.%s")%(os.path.basename(filename)[0:-7],extendtion)
            
            create_time = ('%s-%s-%s')%(time_infor_dic['year'],time_infor_dic['mon'],time_infor_dic['day'])
           
            #new folder
            new_folder = os.path.join(path,('%s %s')%(u'豆瓣',create_time))
            
            #if  dirctory existed pass else create it 
            if os.path.isdir(new_folder):
                pass
            else:
                os.mkdir(new_folder)
                
            try:
                #copy file to new folder
                shutil.copy(child_path,new_folder)
                
                #rename file 
                old_file = os.path.join(new_folder,i)
                new_file = os.path.join(new_folder,true_file_name)
                os.rename(old_file,new_file)
            except:
                #print 'new folder is %s ' % new_folder
                #if the file name existed print it 
                print 'new file is %s ' % filename

    print 'Finshed! :) '


if __name__ == '__main__':
    path = ur'/home/zhyq/音乐'
    #move_sametime_mp3file_to_samefolder(path)
