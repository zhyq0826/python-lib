#-*- coding:utf-8 -*-
import sys

#except  异常类，异常类的实例
#异常类的实例作为
def main(s=0):
    try:
        int(s)
    except (TypeError,ValueError,Exception), e:
        print e
    else:
        print 'no except'
    finally:

        print 'finally '

if __name__ == '__main__':
    main(sys.argv[-1])