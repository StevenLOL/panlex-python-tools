#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regex
import unicodedata
import os
import urllib.request

data_directory = os.path.dirname(__file__) + '/data/'

try:
    os.mkdir(data_directory)
except FileExistsError: pass

def _get_unicode_data_file(file_name, version=None):
    if version:
        url_dir = 'ftp://ftp.unicode.org/Public/' + str(version) + '/ucd/'
    else:
        url_dir = 'ftp://ftp.unicode.org/Public/UCD/latest/ucd/'
    path_list = ['', 'extracted/', 'auxiliary/']
    
    file_found = False
    for path in path_list:
        try:
            with urllib.request.urlopen(url_dir + path + file_name) as response, open(data_directory + file_name, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            file_found = True
            break
        except urllib.error.URLError:
            pass
    if not file_found: raise URLError('file not found in Unicode data repository')

def _code_point_range_to_range(cprange):
    code_points = cprange.strip().split('..')
    start = int(code_points[0], base=16)
    if len(code_points) > 1:
        end = int(code_points[1], base=16)
    else:
        end = start
    return range(start, end + 1)

def _extract_data(file_name):
    data_file = open(data_directory + file_name, 'r')
    output_dict = {}
#    output_dict['missing'] = {}
    property_name = ''
    for line in data_file:
        if line.startswith('# Property:'): 
            property_name = line.replace('# Property:', '').strip()
#        if line.startswith('# @missing: '):
#            data_line = line.replace('# @missing: ', '').strip()
#            missing_cpr = _code_point_range_to_range(data_line.split(';')[0])
#            output_dict['missing'][missing_cpr] = data_line.split(';')[1].strip()
        if line.startswith('#') or not line.strip(): continue
        data = line.split(';')[1].split('#')[0].strip()
        cpr = _code_point_range_to_range(line.split(';')[0])
        output_dict[cpr] = data
    return output_dict, property_name
        
def _populate_properties(file_name, property_name=None):
    if os.path.exists(data_directory + file_name): pass
    else: _get_unicode_data_file(file_name)
    data = _extract_data(file_name)
    if data[1]: 
        unicode_properties[data[1]] = data[0]
    else:
        unicode_properties[property_name] = data[0]

unicode_properties = {}

if os.path.exists(data_directory + 'UnicodeData.txt'): pass
else: _get_unicode_data_file('UnicodeData.txt')

_populate_properties('Scripts.txt')
_populate_properties('DerivedGeneralCategory.txt')
_populate_properties('Blocks.txt')

def get_script(char):
    if len(char) != 1:
        raise TypeError('get_script() expected a character, but string of length 2 found')
    for i in unicode_properties['Script']:
        if ord(char) in i: return unicode_properties['Script'][i]
    return None

def get_property(char, unicode_property):
    if len(char) != 1:
        raise TypeError('get_script() expected a character, but string of length 2 found')
    for i in unicode_properties[unicode_property]:
        if ord(char) in i: return unicode_properties[unicode_property][i]
    for i in unicode_properties[unicode_property]['missing']:
        if ord(char) in i: return unicode_properties[unicode_property][i]
    return None
#def get_category(char):


#def get_all_chars():
#    for line in scripts_data:
#        if line.startswith('#') or not line.strip(): continue
#        
#        data_directory = os.path.dirname(__file__) + '/data'

