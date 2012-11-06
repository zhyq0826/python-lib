*- coding:utf-8 -*-

import os
import shutil
import time 
import platform

from struct import pack, unpack
from hashlib import sha256 as password_hash
import random,string
from urllib import unquote_plus as de
from math import ceil,floor
import re

import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 


##################################################################################
#加密工具
##################################################################################
def random_char(maxlength=6):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:maxlength])

def hash_password(id,password):
    return password_hash("%s%s"%(password, pack('Q', int(id)))).digest()


##################################################################################
#分页工具
##################################################################################
class InvalidPage(Exception):
    pass

class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass


class Paginator(object):
    def __init__(self,total_records=None,per_page=None,display_certain_size=5):

        #总条数
        self.total_records = total_records

        #每页显示的条数
        self.per_page = per_page

        #计算出来的页数
        self.total_pages=0

        #计算出来的数据
        self.data={}

        #当前每个页面显示的链接数比如1,2,3 共三个链接
        self.display_certain_size=display_certain_size

        #开始计算分页
        self.__judge__()
        
        
    def __judge__(self):
        #如果总记录不够在一页显示，则开始分页
        if self.total_records>self.per_page:
            #计算总页数 向下取整
            self.total_pages = int(floor(self.total_records/float(self.per_page)))

            #计算每页的起始和结束位置即[start:end]
            for i in range(0,self.total_pages):
                if i==0:
                    self.data[i+1]=Page(i+1,i,i+self.per_page,self)
                else:
                    self.data[i+1]=Page(i+1,self.data[i].end,self.data[i].end+self.per_page,self)
            
            #如果计算出来的页数不恰巧是个整数，那么还需要计算最后一页
            if self.total_pages<(self.total_records/float(self.per_page)):
                #计算最后一页,因为最后一页肯定是能全页显示的
                self.data[self.total_pages+1]=Page(self.total_pages+1,self.data[self.total_pages].end,self.total_records,self)
        else:
            self.total_pages=1
            self.data[1]=Page(1,0,self.total_records,self)
            
    #根据页码，返回每页数据的开始和结束位置
    def page(self,page_number):
        page_number = int(page_number)
        if page_number in self.data.keys():
            return self.data[page_number]
        else:
            raise EmptyPage("the page contains no results")
        
    #判断是否总页数少于一次性显示的页数，这个主要是可以自己定制页面的链接数的显示，比如如果为true，那么下一页和上一页就可以不显示
    def check_less_than_certain_size(self):
        if len(self.data)<=self.display_certain_size:
            return True
        else:
            return False
        
    #根据计算每次需要显示的页面链接数,即如果当前是:2,3,4,5 当点击4时,页面的显示应该怎样显示
    def calculate_display_pages(self,page_number):
        
        #如果当前请求的页面数小于每次显示的链接数
        display_pages={}
        #全部链接都显示，如果只有一页不显示链接数
        if len(self.data)==1:
            return None
        elif self.check_less_than_certain_size():
            return self.sort_dict_values(self.data)
        else:
            if page_number<=self.display_certain_size/float(2):
                for i in range(0,self.display_certain_size):
                    display_pages[i+1]=self.data[i+1]
            else:
                #当前页面减去显示大小的一半 还大于0，加上显示大小的一半还小于总的大小
                half_of_display_certain_size = int(floor(self.display_certain_size/float(2)))
                if page_number-half_of_display_certain_size>0 and page_number+half_of_display_certain_size<=len(self.data):
                    for i in range(page_number-half_of_display_certain_size,page_number+half_of_display_certain_size+1):
                        display_pages[i]=self.data[i]
                else:
                    for i in range(len(self.data)-self.display_certain_size+1,len(self.data)+1):
                        display_pages[i]=self.data[i]
                        
                        
        return self.sort_dict_values(display_pages)
    
    #因为字典是无序的，先进行排序
    def sort_dict_values(self,adict):
        keys = adict.keys()
        keys.sort()
        
        return [(key,adict[key]) for key in keys]


#页面类 包含每页取数的开始和结束位置，以及页面的位置
class Page(object):

    def __init__(self,page_number=1,start=0,end=0,paginator=None):
        #每页的起始位置
        self.start=start

        #每页的结束位置
        self.end=end

        #每页的页码
        self.page_number=page_number

        #分页工具类
        self.paginator = paginator

        #下一页
        self.next_page_number = self.page_number+1

        #上一页
        self.prev_page_number = self.page_number-1

    def __repr__(self):
        return '<Page start at %s end at %s>' % (self.start,self.end)

    #是否具有下一页
    def has_next(self):
        return self.page_number<self.paginator.total_records/float(self.paginator.per_page)

    #是否有前一页
    def has_prev(self):
        return self.page_number>1


####################################
#递归删除某个目录下面所有的同名文件夹
#如果删除的文件夹不为空则清空
####################################
def recursive_rm_folder(path,foldername):
    if not foldername:
        return 

    #if current path is dirctory, get dirctory 
    if os.path.isdir(path):
        #get current path content
        path_content = os.listdir(path)
        # if current dirctory content is empty, return 
        if not path_content:
            return 

        for i in path_content:
            child_path = os.path.join(path,i)
            #process if child path is dirctory
            if os.path.isdir(child_path):
                #if dirctory is svn 
                if i == foldername:
                    #because os.rmdir can't be allowed to deldte not-empty dirctory must empty svn dirctory
                    for root,dirs,files in os.walk(child_path,topdown=False):
                        for name in files:
                            os.remove(os.path.join(root,name))
                        for name in dirs:
                            os.rmdir(os.path.join(root,name))
                    try:
                        os.rmdir(child_path)
                    except:
                        raise 
                else:
                    recursive_clean_svn(child_path)
            else:
                continue
    else:
        return


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
    
    #sys platform
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
    paginator = Paginator()
    page = Page()

