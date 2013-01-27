#-*- coding: utf-8 -*-

import os
import uuid
import zipfile
import datetime
import subprocess
from xml.dom import minidom as m

def save_tmp_apk(fileValue):
    if not fileValue:
        return None,None
    filename = str(uuid.uuid4())+'.apk'
    savepath = os.path.join('/tmp/'+filename)
    
    if os.path.exists(savepath):
        return None

    try:
        f = open(savepath,'w')
        f.write(fileValue['body'])
    except:
        return None 
    finally:
        f.close()

    return savepath


def analyze_tmp_apk(savepath):
    as_dict = {'pn':None,'ver':None,'sdk':None,'size':None}
    if not os.path.isfile(savepath):
        return None

    xml = "AndroidManifest.xml"
    iconId = None
    try:
        z = zipfile.ZipFile(savepath)
        if xml not in z.namelist():
            raise
    except:
        return None 

    manifestxml = config.Tmp.androidmanifest % str(uuid.uuid4())

    with open(manifestxml,'w') as f:
        f.write(z.read(xml))

    argv = ['java','-jar', config.Path.axmlprinter2, manifestxml]
    dom = m.parseString(
            subprocess.Popen(argv, stdout=subprocess.PIPE).stdout.read()
            )
    root = dom.documentElement

    if root.hasAttribute("package"):
        as_dict['pn'] = root.getAttribute("package")

    if root.hasAttribute("android:versionName"):
        as_dict['ver'] = root.getAttribute("android:versionName")
    
    size = os.path.getsize(savepath)
    size = size/(1024*1024.0)
    size = round(size,1)
    as_dict['size'] = size

    sdk = dom.getElementsByTagName('uses-sdk')
    try:
        if sdk[0].hasAttribute('android:minSdkVersion'):
            as_dict['sdk'] = sdk[0].getAttribute('android:minSdkVersion')
    except:
        raise 

    os.unlink(manifestxml)
    os.unlink(savepath)

    return as_dict
