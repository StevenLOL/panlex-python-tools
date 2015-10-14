#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regex as re
from spacy.en import English
from collections import OrderedDict
parser = None

def initialize_parser():
    global parser
    if not parser:
        parser = English()

def script_char_count(str):
    import unicode
    import unicodedata
    
    str = unicodedata.normalize('NFC', str)
    out_dict = {}
    for i in str:
        script = unicode.get_property(i, 'Script')
        if script in out_dict:
            out_dict[script] += 1
        else:
            out_dict[script] = 1
    return out_dict

def most_common_script(string, ignore_Common_and_Inherited=True, ignore_Latin_in_ties=True, throw_exception_for_ties=True, ignore_Latin=False):
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
    output = re.sub(r'\s+', ' ', str.strip())
    output = re.sub(r'\s*‣+\s*', '‣', output)
    output = output.strip('‣')
    return output

def distribute(str, delim):
    output = []

    if '‣' in str:
        for i in str.split('‣'):
            output.extend(distribute(i, delim))
        return output

    rx = re.compile(r'(\S+)' + delim + r'(\S+)')
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

    output = [clean_str(without), clean_str(within)]

    return output

def move_parens_front(str):

    rx = re.compile(r'(^.*)\((.+)\)(.*$)')

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

    regex1 = re.compile(r'(^.+)\(([^a-z]{2,})\)(.*)$')
    regex2 = re.compile(r'(^[^a-z]{2,} +)\((.+?)\)(.*)$')

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

def multiple_replace(text, adict, regex=False):
    if not isinstance(adict, OrderedDict): adict = OrderedDict([(key, adict[key]) for key in sorted(adict, key=len, reverse=True)])
    if regex: rx = re.compile('(' + ')|('.join(adict.keys()) + ')')

    # rx = re.compile('|'.join(map(re.escape, adict.keys())))
    else: rx = re.compile('(' + ')|('.join(map(re.escape, adict.keys())) + ')')
    def one_xlat(match):
        for key, m in zip(adict.keys(), match.groups()):
            if m: return adict[key]
    # def one_xlat(match):
    #     return adict[match.group(0)]
    return rx.sub(one_xlat, text)

def multiple_replace_re(text, adict):
    rx = re.compile('(' + ')|('.join(adict.keys()) + ')')
    def one_xlat(match):
        for key, m in zip(adict.keys(), match.groups()):
            if m: return adict[key]
    return rx.sub(one_xlat, text)

def tabbed_output(columns, output_file, match_re_column_list=None, legacy_handling=None, match_any=False):
    if legacy_handling:
        match_re_column_list = [(match_re_column_list, legacy_handling)]
    try:
        if isinstance(match_re_column_list[0], str):
            match_re_column_list = [match_re_column_list]
    except TypeError: pass
    if isinstance(columns, dict): 
        if not isinstance(columns, OrderedDict):
            raise TypeError("dictionary argument of 'tabbed_output()' must be an OrderedDict")
        if match_re_column_list: 
            match_re_column_list = [(rx, columns[match_column]) for rx, match_column in match_re_column_list]
        columns = columns.values()
    lengths = [len(column) for column in columns]
    if len(set(lengths)) == 1:
        for i in range(lengths[0]):
            for column in columns:
                if isinstance(column[i], str):
                    column[i] = [column[i]]
                column[i] = '‣'.join(column[i])
            line = '\t'.join([clean_str(column[i]) for column in columns])
            if match_re_column_list:
                if match_any:
                    if any([re.search(rx, match_column[i]) for rx, match_column in match_re_column_list]):
                        print(line, file=output_file)
                else:
                    if all([re.search(rx, match_column[i]) for rx, match_column in match_re_column_list]):
                        print(line, file=output_file)
            else:
                print(line, file=output_file)
    else: raise IndexError("first argument of 'tabbed_output()' must be an OrderedDict or list of identical-length lists")

def assign_property(expression_list, string_to_find, property_list, property_value, remove=True, replace_property=False):
    rx = re.compile(string_to_find)
    prp = None
    prp_list = property_list[:]
    for i in range(len(expression_list)):
        if rx.search(expression_list[i]):
            prp = property_value
            if remove: 
                expression_list[i] = rx.sub('', expression_list[i])
            else: pass
    if prp: 
        if replace_property: prp_list = [prp]
        else: prp_list.append(prp)
    return prp_list
    
def new_meaning(entries, columns):
    if len(entries) == len(columns):
        for i in range(len(entries)):
            entries[i] = [clean_str(expr) for expr in entries[i]]
            columns[i].append(entries[i])
    else: raise IndexError("entries and columns must be identical-length lists")

def split_meaning(entries, split_re, columns_to_dupe=None):
    rx = re.compile(split_re)
    entries1 = {col: [] for col in entries}
    entries2 = {col: [] for col in entries}
    for col in entries:
        if columns_to_dupe:
            if col in columns_to_dupe:
                entries1[col] = entries2[col] = entries[col]
                continue
        entries1[col] = [rx.split(expr)[0] for expr in entries[col]]
        try:
            entries2[col] = [rx.split(expr)[1] for expr in entries[col]]
        except IndexError:
            entries2[col] = ['']
    return entries1, entries2

def move_to_column(from_column, to_column, re_to_match):
    rx = re.compile(re_to_match)
    if isinstance(from_column, str): from_column = [from_column]
    for i in range(len(from_column)):
        if rx.search(from_column[i]):
            for match in rx.findall(from_column[i]):
                to_column.append(match)
            from_column[i] = rx.sub('', from_column[i])

def regex_pop(from_str, re_to_match, pops=1):
    rx = re.compile(re_to_match)
    pop = rx.findall(from_str)[0:pops]
    if not pop: return None
    to_str = rx.sub('', from_str, pops)
    if pops == 1:
        return pop[0], to_str
    else:
        return pop, to_str
        
def regex_pop_all(from_str, re_to_match):
    rx = re.compile(re_to_match)
    pop = rx.findall(from_str)
    to_str = rx.sub('', from_str)
    return pop, to_str

def parts_of_speech(string):
    initialize_parser()
    output = []
    for token in parser(string):
        output.append(token.pos_)
    return output

def lemmas(string):
    initialize_parser()
    output = []
    for token in parser(string):
        output.append(token.lemma_)
    return output

def lemmatized(string, to_skip_list=None):
    initialize_parser()
    if to_skip_list:
        skip_re = re.compile('|'.join(to_skip_list))
    output = ''
    for token in parser(string):
        if to_skip_list and skip_re.search(token.text): 
            output += token.text_with_ws
            continue
        output += token.text_with_ws.replace(token.text, token.lemma_)
    return output


def sans_bracketed(string, beginning_bracket='\(', ending_bracket='\)'):
    bb = beginning_bracket
    eb = ending_bracket
    # rx = re.compile(bb + r'.*?' + eb)
    # rx = re.compile(r'{0}(?:[^{0}{1}]|(?R))*{1}'.format(beginning_bracket, ending_bracket))
    rx = re.compile(r'{0}(?:[^{0}{1}]|(?R))*{1}'.format(bb, eb))
    return rx.sub('', string)


def parenthesize(from_str, re_to_match):
    rx = re.compile(re_to_match)
    if rx.groups == 0: rx = re.compile(r'(' + re_to_match + r')')
    to_str = rx.sub(r'(\1)', from_str)
    return to_str

def get_chars(lst):
    return sorted(set(''.join(flatten(lst))))
    

