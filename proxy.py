#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import urllib.request
import random
from agent import *

#抓取代理的正则表达式
regexp = r'''
<tr\s+?class[^>]*?>\s*?
<td>.*?</td>\s*?
<td>.*?</td>\s*?
<td>(.*?)</td>\s*?
<td>(.*?)</td>\s*?
<td>.*?</td>\s*?
<td>.*?</td>\s*?
<td>(.*?)</td>\s*?
<td>.*?</td>\s*?
<td>.*?</td>\s*?
<td>.*?</td>\s*?
</tr>'''

if os.path.exists('proxy.txt'):
    os.remove('proxy.txt')

#开始抓取代理
for path in ['wn','wt']:
    for page in range(1,2):
        url = 'http://www.xicidaili.com/' + path + '/%d' % page

        #获得页面
        req = urllib.request.Request(url , headers = {'User-Agent' : random.choice(agent())})
        html = urllib.request.urlopen(req).read().decode('utf-8')

        #匹配正则表达式
        proxies = re.compile(regexp , re.VERBOSE | re.DOTALL).findall(html)

        #保存代理
        with open('proxy.txt' , 'a') as f:
            for proxy in proxies:
                if f.tell() != 0:
                    f.write('\n')
                f.write('%s:%s@%s' % (proxy[0] , proxy[1] , proxy[2].lower()))
