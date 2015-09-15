#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regex
import unicodedata
import unicode

def script_char_count(str):
    str = unicodedata.normalize('NFC', str)
    out_dict = {}
    for i in str:
        script = unicode.get_property(i, 'Script')
        if script in out_dict:
            out_dict[script] += 1
        else:
            out_dict[script] = 1
    return out_dict

def get_most_common_script(string, ignore_Common_and_Inherited=True, ignore_Latin_in_ties=True, throw_exception_for_ties=True, ignore_Latin=False):
    if len(string.strip()) == 0: return None
    inp = script_char_count(string)
    if ignore_Common_and_Inherited:
        try: 
            del inp['Common']
        except KeyError: pass
        try:
            del inp['Inherited']
        except KeyError: pass
    if ignore_Latin:
        try: 
            del inp['Latin']
        except KeyError: pass
    output = [k for k,v in inp.items() if v == max(inp.values())]
    if ignore_Latin_in_ties:
        if len(output) > 1:
            try: output.remove('Latin')
            except ValueError: pass
    if throw_exception_for_ties:
        if len(output) > 1:
            raise ValueError('tie between ' + str(output))
    return output[0]

def str_out(obj):
    try:
        return obj.text
    except AttributeError:
        if obj == None: return ''
        else: return obj

def clean_str(str):
    output = regex.sub(r'\s+', ' ', str.strip())
    output = regex.sub(r'‣+', '‣', output)
    output = output.strip('‣')
    return output

def distribute(str, delim):
    output = []

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(distribute(i, delim))
        return output

    rx = regex.compile(r'(\S+)' + delim + r'(\S+)')
    re_match = rx.search(str)
    if re_match:
        output = [rx.sub(re_match.group(1), str, 1), rx.sub(re_match.group(2), str, 1)]
    else:
        return [str]
    
    return output

def expand_parens(str, include_spaces=False):
    output = []

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(expand_parens(i))
        return output

    if include_spaces:
        regex1 = regex.compile(r'(^.*)\((.+)\)(.*$)')
        regex2 = regex.compile(r'(^.*)\((.+)\)(.*$)')
    else:
        regex1 = regex.compile(r'(^.*[^ ])\(([^ ]+)\)(.*$)')
        regex2 = regex.compile(r'(^.*)\(([^ ]+)\)([^ ].*$)')

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

    output = [clean_str(without), clean_str(within)]

    return output

def move_parens_front(str):

    rx = regex.compile(r'(^.*)\((.+)\)(.*$)')

    re_match = rx.search(str)
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

    regex1 = regex.compile(r'(^.+)\(([^a-z]{2,})\)(.*)$')
    regex2 = regex.compile(r'(^[^a-z]{2,} +)\((.+?)\)(.*)$')

    re_match1 = regex1.search(str)
    re_match2 = regex2.search(str)
    if re_match1:
        str1 = ' '.join([re_match1.group(1).strip(), re_match1.group(3).strip()]).strip()
        str2 = ' '.join([re_match1.group(2).strip(), re_match1.group(3).strip()]).strip()
        return[str1, str2]
    elif re_match2:
        str1 = ' '.join([re_match2.group(1).strip(), re_match2.group(3).strip()]).strip()
        str2 = ' '.join([re_match2.group(2).strip(), re_match2.group(3).strip()]).strip()
        return[str1, str2]
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

def multiple_replace(text, adict):
    rx = regex.compile('|'.join(map(regex.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)

def tabbed_output(columns, output_file, match_re=None, match_column=None):
    if match_re: rx = regex.compile(match_re)
    if len(set([len(column) for column in columns])) == 1:
        for i in range(len(columns[0])):
            for column in columns:
                if isinstance(column[i], str):
                    column[i] = [column[i]]
                column[i] = '‣'.join(column[i])
            line = '\t'.join([clean_str(column[i]) for column in columns])
            if match_re:
                if match_column:
                    if rx.search(match_column[i]):
                        print(line, file=output_file)
                else:            
                    if rx.search(line):
                        print(line, file=output_file)
            else:
                print(line, file=output_file)
    else: raise IndexError("first argument of 'tabbed_output()' must be a list of identical-length lists")
    

def assign_property(expression_list, string_to_find, property_list, property_value, remove=True):
    rx = regex.compile(string_to_find)
    prp = None
    for i in range(len(expression_list)):
        if rx.search(expression_list[i]):
            prp = property_value
            if remove: 
                expression_list[i] = rx.sub('', expression_list[i])
            else: pass
    if prp: property_list.append(prp)

def new_meaning(entries, columns):
    if len(entries) == len(columns):
        for i in range(len(entries)):
            entries[i] = [clean_str(expr) for expr in entries[i]]
            columns[i].append(entries[i])
    else: raise IndexError("entries and columns must be identical-length lists")

def unicode_names(str):
    output = []
    for char in str:
        try:
            output.append(unicodedata.name(char))
        except ValueError: 
            output.append(None)
    return output
    

