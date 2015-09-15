#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regex
import os
import urllib.request
import zipfile
import io
import imp

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
    if not file_found:
        try:
            with urllib.request.urlopen(url_dir + 'Unihan.zip') as response, open(data_directory + file_name, 'wb') as out_file:
                zipf = zipfile.ZipFile(io.BytesIO(response.read()))
                data = zipf.open(file_name, 'r').read()
                out_file.write(data)
            file_found = True
        except:
            pass
    
    if not file_found: raise urllib.error.URLError('file not found in Unicode data repository')

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
    output_list = [''] * 0x110000
    property_name = ''
    for line in data_file:
        if line.startswith('# Property:'): 
            property_name = line.replace('# Property:', '').strip()
        if line.startswith('# @missing: '):
            data_line = line.replace('# @missing: ', '').strip()
            missing_cpr = _code_point_range_to_range(data_line.split(';')[0])
            missing_data = data_line.split(';')[1].strip()
            for code_point in missing_cpr:
                output_list[code_point] = missing_data
        if line.startswith('#') or not line.strip(): continue
        data = line.split(';')[1].split('#')[0].strip()
        cpr = _code_point_range_to_range(line.split(';')[0])
        for code_point in cpr:
            output_list[code_point] = data
    return {property_name: output_list}

def _extract_Unihan_data(file_name):
    data_file = open(data_directory + file_name, 'r')
    output_dict = {}
    for line in data_file:
        if line.startswith('#') or not line.strip(): continue
        data_line = line.split('\t')
        code_point = int(data_line[0].replace('U+', '').strip(), base=16)
        property_name = data_line[1].strip()
        data = data_line[2].strip()
        try:
            output_dict[property_name][code_point] = data
        except KeyError:
            output_dict[property_name] = [''] * 0x110000
            output_dict[property_name][code_point] = data
    return output_dict

def _populate_properties(file_name, property_name=None, Unihan=False, force=False):
    if force: _get_unicode_data_file(file_name)
    if os.path.exists(data_directory + file_name): pass
    else: _get_unicode_data_file(file_name)
    if Unihan: data = _extract_Unihan_data(file_name)
    else: data = _extract_data(file_name)
    if '' in data: 
        unicode_properties[property_name] = data['']
    else:
        unicode_properties.update(data)

unicode_properties = {}

#if os.path.exists(data_directory + 'UnicodeData.txt'): pass
#else: _get_unicode_data_file('UnicodeData.txt')

file_list = [
    ('Scripts.txt', {}),
    ('DerivedGeneralCategory.txt', {}),
    ('Blocks.txt', {}),
    ('Unihan_Readings.txt', {'Unihan': True}),
    ('EastAsianWidth.txt', {'property_name': 'East_Asian_Width'}),
    ('Unihan_RadicalStrokeCounts.txt', {'Unihan': True}),
    ('IndicPositionalCategory.txt', {}),
    ]
    
for i in file_list:
    _populate_properties(i[0], **i[1])
    
def force_update():
    for i in file_list:
        _populate_properties(i[0], force=True, **i[1])
        
def get_property(char, unicode_property):
    if len(char) != 1:
        raise TypeError('get_property() expected a character, but string of length 2 found')
    return unicode_properties[unicode_property][ord(char)]

def get_chars(unicode_property, value, max_chars=0, re=False):
    if re: rx = regex.compile(value)
    for i in range(len(unicode_properties[unicode_property])):
        if re:
            if rx.search(unicode_properties[unicode_property][i]):
                print('\t'.join([hex(i), chr(i), unicode_properties[unicode_property][i]]))
        else:
            if unicode_properties[unicode_property][i] == value:
                print(hex(i) + '\t' + chr(i))
        
#def get_all_chars():
#    for line in scripts_data:
#        if line.startswith('#') or not line.strip(): continue
#        
#        data_directory = os.path.dirname(__file__) + '/data'

