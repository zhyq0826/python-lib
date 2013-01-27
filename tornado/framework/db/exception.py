#!/usr/bin/env python
#-*- coding: utf-8 -*-

class AdeskException(Exception):
    def __init__(self, msg, code=-1):
        self.args = (code, msg)
        self.code = code
        self.err = msg
        
class InvalidDocException(AdeskException):
    pass

class ObjectidException(AdeskException):
    pass
 
