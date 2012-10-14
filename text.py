#-*- coding:utf-8 -*-

from math import ceil,floor
import re

import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 


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
    truncatewords(s,3)
    truncatewords_html(s,3)

