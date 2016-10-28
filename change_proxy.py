#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import socks
import socket
import urllib.request

def change_proxy(proxy = None):
    if proxy is None:
        with open('proxy.json' , 'r') as f:
            proxies = eval(f.read())
            proxy = random.choice(proxies)
    #安装代理
    if proxy['protocol'] == 'socks4':
        socks.set_default_proxy(socks.SOCKS4 ,proxy['ip'] , int(proxy['port']))
        socket.socket = socks.socksocket
    elif proxy['protocol'] == 'socks5':
        [ip , port] = host.split(':')
        socks.set_default_proxy(socks.SOCKS5 ,proxy['ip'] , int(proxy['port']))
        socket.socket = socks.socksocket
    else: 
        proxy_support = urllib.request.ProxyHandler({proxy['protocol'] : proxy['ip'] + ':' + proxy['port']})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
    return (proxy['protocol'] , proxy['ip'] + ':' + proxy['port'])
