#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import threading
import queue
import urllib.request
import urllib.error
import socket

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_301(self , req , fp , code , msg , headers):
        pass

    def http_error_302(self , req , fp , code , msg , headers):
        pass

def dirb():
    while not urls.empty():
        url = urls.get()
        request = urllib.request.Request(url)
        request.get_method = lambda : 'HEAD'
        try:
            response = urllib.request.urlopen(request , timeout = 3)
        except urllib.error.URLError as e:
            if hasattr(e , 'code'):
                code = e.code
            else:
                continue
        except (UnicodeError , socket.timeout):
            continue
        else:
            code = response.code

        if code not in []:
            print(str(code) + ' ' + url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('多线程扫描网站工具')
    parser.add_argument('-n' , '--number' , help = '线程数' , default = 10 , type = int)
    parser.add_argument('file' , help = '包含域名的文件名')
    parser.add_argument('wordlist' , help = '字典文件')
    args = parser.parse_args()
    threads = []
    flag = True    #是否还会有新url生成标志

    opener = urllib.request.build_opener(RedirectHandler)
    urllib.request.install_opener(opener)

    urls = queue.Queue()
    with open(args.file , 'r') as f_site:
        for site in f_site:
            site = site.strip()
            with open(args.wordlist , 'r') as f_wordlist:
                for path in f_wordlist:
                    path = path.strip()
                    urls.put('http://' + site + path)

    for number in range(args.number):
        threads.append(threading.Thread(target = dirb))
        threads[number].setDaemon(True)
        threads[number].start()

    for number in range(args.number):
        threads[number].join()
