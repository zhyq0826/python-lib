# -*- coding:utf-8 -*-
from hashlib import sha256
from datetime import datetime,timedelta
from types import DictType,ListType,BooleanType,IntType,StringType
from types import UnicodeType as DefaultStrType
import time

from bson.objectid import ObjectId
from pymongo import ASCENDING,DESCENDING
from exception import * 
import mongo


def hash_password(mid,password):
    return sha256('%s%s'%(unicode(mid),password)).hexdigest()

user_key={
    'nickname':DefaultStrType,
    'email':DefaultStrType,
    'passwd':DefaultStrType,
    'atime':datetime
   }


class Document(object):
    
    collect_map_model = {
            'UserDoc':mongo.user,
            }
    
    property_map_model={}

    db ={'m':mongo} 
    db_file = {'m':mongo.db_file}

    collect = None
    properties = None 
    collum = None

    def __init__(self):
        self.collect = self.collect_map_model.get(self.__class__.__name__,None)
        self.properties = self.property_map_model.get(self.__class__.__name__,None)

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
            if unicode(i['_id']) in as_dict:
                pass
            else:
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
            raise ObjectidException('非法id')
        else:
            try:
                objid = ObjectId(objid)
            except:
                raise ObjectidException('非法id')

        return objid 


    def inc(self,objid,key,num=1):
        self.collect.update({'_id':objid},{'$inc':{key:num}})

    
    def create(self,doc,safe=True):
        if not isinstance(doc,dict):
            return None
        
        if self.properties is None:
            raise InvalidDocException('collection properties is None')
        
        p_keys,d_keys = set(self.properties.keys()),set(doc.keys())
        if not p_keys>=d_keys:
            raise InvalidDocException('error collection key')

        #init empty key 
        type_map = {ListType:[],DictType:{},IntType:0}
        diff_keys = p_keys.difference(d_keys)
        for i in diff_keys:
            doc[i] = type_map.get(self.properties[i],None) 

        if safe:
            if self.is_valid_doc(doc):
                objid = self.collect.insert(doc,safe=True)
            else:
                s = ('%s %s ')%(self.collect,'invalid document')
                raise InvalidDocException(s)
        else:
            objid = self.collect.insert(doc,safe=False)

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

