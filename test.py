#-*- coding:utf-8 -*-


import os
import shutil 

#root dir
root_dir_content = os.listdir(ur'I:/TDDOWNLOAD/紗奈')

#path 
path = 'I://TDDOWNLOAD//紗奈//'

for i in root_dir_content:
    child_path = ('%s%s')%(path,i)
    if os.path.isdir(child_path):
        #get children dir content
        child_dir_content = os.listdir(child_path)
        print child_dir_content
        if len(child_dir_content)<=1:
            pass
        else:
            print child_path
            try:
                shutil.move(child_path, ur'I:/3k')
                os.rmdir(child_path)
            except:
                continue  
                
'''
Created on 2012-10-12

@author: zhyq
'''


import os
import shutil 

#root dir
root_dir_content = os.listdir('I://TDDOWNLOAD//Graphis Gals')

#path 
path = 'I://TDDOWNLOAD//Graphis Gals//'

for i in root_dir_content:
    child_path = ('%s%s')%(path,i)
    if os.path.isdir(child_path):
        #get children dir content
        child_dir_content = os.listdir(child_path)
        print child_dir_content
        if not child_dir_content:
            os.rmdir(child_path)
        else:  
            for j in child_dir_content:
                child_son_path = ('%s%s//%s')%(path,i,j)
                if os.path.isdir(child_son_path):
                    try:
                        shutil.move(child_son_path, 'I://TDDOWNLOAD//Graphis Gals//new')
                    except:
                        continue
                
        
    

