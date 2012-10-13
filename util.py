#-*- coding:utf-8 -*-
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


##################################################################################
#截取字符工具,不保留html
##################################################################################
def truncatewords(s,num,end_text='...'):

    re_tag= re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    re_words = re.compile(u'(&.*?;)|[\u4e00-\u9fa5]{1}|[^\u4e00-\u9fa5]{1}',re.UNICODE)
    
    s = force_unicode(s)

    length=int(num)

    if length<=0:
        return u''
    
    pos = 0
    words=0
    data=[]
    out=''
    current_word = ''
    while words <= length:
        if words==length:
            break

        #查找第一个标签结束的>
        m= re_tag.search(s,pos)
        if not m:
            break
        pos = m.end()

        #开始从这个位置向后搜索字符,匹配到第一个字符，停止，检查,如果字符是<,说明匹配到了html标签了,则跳出去,否则开始检查下一个标签的>
        while words <= length:
            if words==length:
                break
            m = re_words.search(s,pos)   
            if not m:
                break
            current_word = m.group()
            if current_word=='<':
                break
            else:
                if not m.group(1):
                    words+=1
                    data.append(str(m.group()))
                    pos+=1
                else:
                    words+=1
                    data.append(str(m.group()))
                    pos=m.end()

    out = ''.join(data)

    out+=end_text
    return out



##################################################################################
#截取字符工具，保留html
##################################################################################
def truncatewords_html(s,num,end_text='...'):
    
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
    re_tag= re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    re_words = re.compile(u'(&.*?;)|[\u4e00-\u9fa5]{1}|[^\u4e00-\u9fa5]{1}',re.UNICODE)
    
    s = force_unicode(s)
    
    
    length=int(num)
    
    if length<=0:
        return u''
    
    pos = 0
    words=0
    current_word = ''
    open_tags=[]
    while words <= length:
        if words==length:
            break

        #查找第一个标签结束的>
        m= re_tag.search(s,pos)
        if not m:
            break
        pos = m.end()
        closing_tag,tagname,self_closing=m.groups()
        
        #自关闭标签不处理,或者是单标签
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                #移除该标签，说明该标签已经闭合
                open_tags.remove(tagname)
        else:
            #把标签加入到仍然打开的标签中
            open_tags.insert(0, tagname)
            
        #开始从这个位置向后搜索字符,匹配到第一个字符，停止，检查,如果字符是<则跳出去,否则开始检查下一个标签的>
        while words <= length:
            
            if words==length:
                break
            m = re_words.search(s,pos)
            if not m:
                break
            current_word = m.group()
            if current_word=='<':
                break
            else:
                if not m.group(1):
                    words+=1
                    pos+=1
                else:
                    words+=1
                    pos=m.end()
    #如果本身的大小就不够，则不加结尾
    if pos==len(s):
        return s
    out = s[:pos]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag

    # Return string
    return out


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode. This function gets called often in that
    # setting.
    if isinstance(s, unicode):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = ' '.join([force_unicode(arg, encoding, strings_only,
                            errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise DjangoUnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join([force_unicode(arg, encoding, strings_only,
                    errors) for arg in s])
    return s

if __name__ == '__main__':
    s = ''
    paginator = Paginator()
    page = Page()
    truncatewords(s,3)
    truncatewords_html(s,3)

