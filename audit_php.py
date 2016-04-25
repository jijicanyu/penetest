#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse

def audit_php(path):
    audits = [
        [r'''\b(include|require)(_once)?(\s+|\s*\().*\$(?!.*this->)\w+((\[["']|\[)\$?[\w\[\]"']*)?''','文件包含函数中存在变量,可能存在文件包含漏洞'],
        [r'''\bpreg_replace\(\s*.*/[is]{,2}e[is]{,2}["']\s*,(.*\$.*,|.*,.*\$)''','preg_replace的/e模式，且有可控变量，可能存在代码执行漏洞'], 
        [r'''\bphpinfo\s*\(\s*\)''','phpinfo()函数，可能存在敏感信息泄露漏洞'], 
        [r'''\bcall_user_func(_array)?\(\s*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','call_user_func函数参数包含变量，可能存在代码执行漏洞'], 
        [r'''\b(file_get_contents|fopen|readfile|fgets|fread|parse_ini_file|highlight_file|fgetss|show_source)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','读取文件函数中存在变量，可能存在任意文件读取漏洞'], 
        [r'''\b(system|passthru|pcntl_exec|shell_exec|escapeshellcmd|exec)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)*''','命令执行函数中存在变量，可能存在任意命令执行漏洞'], 
        [r'''\b(mb_)?parse_str\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','parse_str函数中存在变量,可能存在变量覆盖漏洞'], 
        [r'''\${?\$\w+((\[["']|\[)\$?[\w\[\]"']*)?\s*=\s*.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','双$$符号可能存在变量覆盖漏洞'], 
        [r'''["'](HTTP_CLIENT_IP|HTTP_X_FORWARDED_FOR|HTTP_REFERER)["']''','获取IP地址方式可伪造，HTTP_REFERER可伪造，常见引发SQL注入等漏洞'],
        [r'''\b(unlink|copy|fwrite|file_put_contents|bzopen)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','文件操作函数中存在变量，可能存在任意文件读取/删除/修改/写入等漏洞'], 
        [r'''\b(extract)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?\s*,?\s*(EXTR_OVERWRITE)?\s*\)''','extract函数中存在变量，可能存在变量覆盖漏洞'],
        [r'''\$\w+((\[["']|\[)\$?[\w\[\]"']*)?\s*\(\s*\$_(POST|GET|REQUEST|SERVER)\[.+\]''','可能存在代码执行漏洞,或者此处是后门'],
        [r'''^(?!.*\baddslashes).*\b((raw)?urldecode|stripslashes)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','urldecode绕过GPC,stripslashes会取消GPC转义字符'], 
        [r'''`\$\w+((\[["']|\[)\$?[\w\[\]"']*)?`''','``反引号中包含变量，变量可控会导致命令执行漏洞'],
        [r'''\barray_map\s*\(\s*.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?\s*.*,''','array_map参数包含变量，变量可控可能会导致代码执行漏洞'], 
        [r'''(?i)select\s+.+from.+\bwhere\s+.+=["\s\.]*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','SQL语句select中条件变量无单引号保护，可能存在SQL注入漏洞'],
        [r'''(?i)delete\s+from.+\bwhere\s+.+=["\s\.]*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','SQL语句delete中条件变量无单引号保护，可能存在SQL注入漏洞'],
        [r'''(?i)insert\s+into\s+.+\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','SQL语句insert中插入变量无单引号保护，可能存在SQL注入漏洞'],
        [r'''(?i)update\s+.+\s+set\s+.+\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','SQL语句delete中条件变量无单引号保护，可能存在SQL注入漏洞'],
        [r'''\b(eval|assert)\s*\(.*\$\w+((\[["']|\[)\$?[\w\[\]"']*)?''','eval或者assertc函数中存在变量，可能存在代码执行漏洞'],
        [r'''\b(echo|print|print_r)\s*\(?.*\$_(POST|GET|REQUEST|SERVER)''','echo等输出中存在可控变量，可能存在XSS漏洞'],
        [r'''(\bheader\s*\(.*|window.location.href\s*=\s*)\$_(POST|GET|REQUEST|SERVER)''','header函数或者js location有可控参数，存在任意跳转或http头污染漏洞'],
        [r'''\bmove_uploaded_file\s*\(''','存在文件上传，注意上传类型是否可控']]
    
    results = []
    for walk in os.walk(path):
        for filename in walk[2]:
            if os.path.splitext(filename)[1] != '.php':
                continue
            filepath = os.path.join(walk[0] , filename)
            with open(filepath , 'r' , errors='ignore') as f:
                count = 0
                while True:
                    count += 1
                    line = f.readline()
                    if not line:
                        break
                    for audit in audits:
                        if re.search(audit[0] , line):
                            results.append([audit[1] , filepath , line.strip() , count])
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'PHP代码审计工具')
    parser.add_argument('path' , help = '需要审计的文件夹路径' , nargs = '+')
    args = parser.parse_args()
    for path in args.path:
        for result in audit_php(path):
            [title , filepath , line , count] = result
            print(title , filepath , line , count)
