#!/usr/bin/env python

def foo():
    print 'call bar here'
    bar()

def bar():
    print 'bar is called'


if __name__ == '__main__':
    foo()