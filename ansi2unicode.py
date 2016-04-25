#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

def ansi2unicode(ansi):
    return (ansi + '\x00').encode('gb2312').decode('utf-16' , errors='replace')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'ANSI(GB2312)转Unicode(UTF-16)')
    parser.add_argument('ansi' , help = 'ANSI(GB2312)字符串')
    args = parser.parse_args()
    print(ansi2unicode(args.ansi))
