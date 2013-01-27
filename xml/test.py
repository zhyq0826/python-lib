#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from xml.dom import minidom

s = """
<?xml version="1.0" encoding="UTF-8" ?><root>
<item><word>警告菲律宾</word><url>http://ad2.easou.com:8080/j10ad/ea2.jsp?channel=11&amp;wver=t&amp;cid=bip1065_10491_001&amp;key=警告菲律宾</url></item><item><word>信访局长不雅照</word><url>http://ad2.easou.com:8080/j10ad/ea2.jsp?channel=11&amp;wver=t&amp;cid=bip1065_10491_001&amp;key=信访局长不雅照</url></item><item><word>抽查干部财产</word><url>http://ad2.easou.com:8080/j10ad/ea2.jsp?channel=11&amp;wver=t&amp;cid=bip1065_10491_001&amp;key=抽查干部财产</url></item><item><word>董春雨</word><url>http://ad2.easou.com:8080/j10ad/ea2.jsp?channel=11&amp;wver=t&amp;cid=bip1065_10491_001&amp;key=董春雨</url></item><item><word>黄奕老公黄毅清</word><url>http://ad2.easou.com:8080/j10ad/ea2.jsp?channel=11&amp;wver=t&amp;cid=bip1065_10491_001&amp;key=黄奕老公黄毅清</url></item>
</root>
"""
#s = s.encode('utf-8') 

def main1():
    dom = minidom.parseString(s.strip())
    items = dom.getElementsByTagName('item')
    root = dom.documentElement
    if root.hasAttribute('package'):
        packname = root.getAttribute('package')
    else:
        packname = None
        
    for i in items:
        word_node = i.firstChild.firstChild
        url_node = i.lastChild.firstChild
        word = gettext(word_node)
        url = gettext(url_node)
        print word

def gettext(node):
    if node and node.nodeType == node.TEXT_NODE:
          return node.nodeValue
    return None 

if __name__ == '__main__':
    main1()
