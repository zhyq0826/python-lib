# -*- coding:utf-8 -*-
from hashlib import sha256
from datetime import datetime,timedelta
from types import DictType,ListType,BooleanType,IntType,StringType
from types import UnicodeType as DefaultStrType
import time
import logging

from bson.objectid import ObjectId
from pymongo import ASCENDING,DESCENDING
from exception import * 
import mongo
import dockey

def hash_password(password):
    return sha256(password).hexdigest()

class Document(object):
    
    collect_model = {
            'UserDoc':mongo.user,
            }
    
    property_model={'UserDoc':dockey.user}

    db ={'m':mongo} 
    db_file = {'m':mongo.db_file}

    collect = None
    properties = None 
    collum = None
    init_value = {ListType:[],DictType:{},IntType:0}

    def __init__(self):
        self.collect = self.collect_model.get(self.__class__.__name__,None)
        self.properties = self.property_model.get(self.__class__.__name__,None)

    def __setitem__(self,k,v):
        setattr(self,k,v)
    

    def __getitem__(self,k):
        getattr(self,k)


    def _repr__(self):
        if self.collect:
            return '<%s>'%self.collect.name
        else:
            return '<%s>'%self.collect


    def insert(self,doc_or_docs,
            safe=False, **kwargs):

        return  self.collect.insert(doc_or_docs,safe=safe,**kwargs)
    

    def save(self,to_save,
            safe=False, **kwargs):

        return self.collect.save(to_save,
                safe=safe, **kwargs)


    def find_one(self,spec_or_id=None, *args, **kwargs):
        return self.collect.find_one(spec_or_id,*args,**kwargs)


    def find(self,*args, **kwargs):
        return self.collect.find(*args,**kwargs)

    
    def update(self,spec, document,
            safe=False, multi=False,**kwargs):

        return self.collect.update(spec, document,safe=safe,multi=multi,**kwargs)
    

    def remove(self,spec_or_id=None,safe=False,**kwargs):
        return self.collect.remove(spec_or_id,safe,**kwargs)


    def get_as_id(self,objid,collum=None):
        try:
            document_id = self.to_objectid(objid)
        else:
            return None

        doc =  self.collect.find_one({'_id':document_id},collum)
        return doc

    
    def get_as_collum(self,condition=None,collum=None,skip=0,limit=0,sort=None):
        if collum is None:
            collum = self.collum

        return self.find(condition,collum,skip=skip,limit=limit,sort=sort)


    def get_as_dict(self,condition=None,collum=None,skip=0,limit=0,sort=None):
        if collum is None:
            collum = self.collum

        as_list = list(self.collect.find(condition,collum,skip=skip,limit=limit,sort=sort))
        as_dict={}
        for i in as_list:
            if unicode(i['_id']) not in as_dict:
                as_dict[unicode(i['_id'])]=i

        return as_dict,as_list


    def is_valid_doc(self,doc):
        if isinstance(doc,dict):
            p_keys,d_keys = set(self.properties.keys()),set(doc.keys())
            if p_keys == d_keys:
                for k in p_keys:
                    if doc[k] is not None and not isinstance(doc[k],self.properties[k]):
                        return False
            else:
                return False
        else:
            return False
        
        return True


    def to_objectid(self,objid):
        if isinstance(objid,ObjectId):
            return objid
        elif objid is None:
            logging.error(unicode(objid)+' invalid objectid')
            raise ObjectidException('非法id')
        else:
            try:
                objid = ObjectId(objid)
            except:
                logging.error(unicode(objid)+' invalid objectid')
                raise ObjectidException('非法id')

        return objid 


    def inc(self,objid,key,num=1):
        self.collect.update({'_id':objid},{'$inc':{key:num}})

    
    def create(self,doc,safe=True):
        if not isinstance(doc,dict):
            return None
        
        if self.properties is None:
            logging.error('collection properties is None')
            raise InvalidDocException('collection properties is None')
        
        p_keys,d_keys = set(self.properties.keys()),set(doc.keys())
        if not p_keys>=d_keys:
            logging.error('error collection key')
            raise InvalidDocException('error collection key')

        diff_keys = p_keys.difference(d_keys)
        for i in diff_keys:
            doc[i] = self.init_value.get(self.properties[i],None) 

        if self.is_valid_doc(doc):
            objid = self.collect.insert(doc,safe=safe)
        else:
            s = ('%s %s ')%(self.collect,'invalid document')
            logging.error(s)
            raise InvalidDocException(s)

        return objid

    def to_str(self,value):
        for k,v in value.items():
            if isinstance(v,ObjectId):
                value[k] = unicode(v)

            if isinstance(v,dict):
                for k1,v1 in v.items():
                    if isinstance(v1,ObjectId):
                        v[k1] = unicode(v1)

            if isinstance(v,list):
                for num,j in enumerate(v):
                    if isinstance(j,ObjectId):
                        v[num] = unicode(j)

            if isinstance(v,datetime):
                value[k] = time.mktime(v.timetuple()) 
            
            if isinstance(v,basestring):
                value[k] = v.strip()

        return value

