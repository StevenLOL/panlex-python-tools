#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

def str_out(obj):
    try:
        return obj.text
    except AttributeError:
        if obj == None: return ''
        else: return obj

def distribute(str, delim):
    output = []

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(distribute(i, delim))
        return output

    regex = re.compile(r'(\S+)' + delim + r'(\S+)')
    re_match = regex.search(str)
    if re_match:
        output = [regex.sub(re_match.group(1), str, 1), regex.sub(re_match.group(2), str, 1)]
    else:
        return [str]
    
    return output

def expand_parens(str, include_spaces = False):
    output = []

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(expand_parens(i))
        return output

    if include_spaces:
        regex1 = re.compile(r'(^.*)\((.+)\)(.*$)')
        regex2 = re.compile(r'(^.*)\((.+)\)(.*$)')
    else:
        regex1 = re.compile(r'(^.*[^ ])\(([^ ]+)\)(.*$)')
        regex2 = re.compile(r'(^.*)\(([^ ]+)\)([^ ].*$)')

    re_match1 = regex1.search(str)
    re_match2 = regex2.search(str)
    if re_match1:
        within = re_match1.group(1) + re_match1.group(2) + re_match1.group(3)
        without = re_match1.group(1) + re_match1.group(3)
    elif re_match2:
        within = re_match2.group(1) + re_match2.group(2) + re_match2.group(3)
        without = re_match2.group(1) + re_match2.group(3)
    else:
        return [str]
 
    output = [within, without]

    return output

def move_parens_front(str):

    regex = re.compile(r'(^.+)\((.+)\)(.*$)')

    re_match = regex.search(str)
    if re_match:
        beginning = re_match.group(1).strip() 
        middle = re_match.group(2).strip()
        end = re_match.group(3).strip()
        return middle + ' ' + ' '.join([beginning, end]).strip()
    else:
        return str

def handle_initialism(str):

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(handle_initialism(i))
        return output

    regex = re.compile(r'(^.+)\(([^a-z]{2,})\)')

    re_match = regex.search(str)
    if re_match:
        return[re_match.group(1).strip(), re_match.group(2).strip()]
    else:
        return [str]

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
