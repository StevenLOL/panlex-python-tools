#!/usr/bin/python3
# -*- coding: utf-8 -*-

import regex

def ngram_set(input, n):
    return set(zip(*[input[i:] for i in range(n)]))

def list_ngram_set(list, n, regexs=(), match_all=True):
    if len(regexs) != n and len(regexs) != 0:
        raise TypeError('number of regexs must match n or be 0')
    output = set()
    for expr in list:
        for ngram in ngram_set(' ' + expr + ' ', n):
        # Expressions are padded to allow for ngrams matching beginnings and endings of words
            if regexs:
                if ngram_matches_regexs(ngram, regexs, match_all): output.add(ngram)
            else:
                output.add(ngram)
    return output

def ngram_matches_regexs(ngram, regexs, match_all=True):
    regexs = [regex.compile(rx) for rx in regexs]
    if len(regexs) != len(ngram):
        raise TypeError('number of regexs must match n')
    if match_all:
        for char, rx in zip(ngram, regexs):
            if not rx.match(char): return False
        return True
    else:
        for char, rx in zip(ngram, regexs):
            if rx.match(char): return True
        return False

def ngram_subset(NgramSet, regexs, match_all=True):
    regexs = [regex.compile(rx) for rx in regexs]
    if len(regexs) != len(list(NgramSet)[0]):
        raise TypeError('number of regexs must match n')
    return {ngram for ngram in NgramSet if ngram_matches_regexs(ngram, regexs, match_all)}

def not_in_ngram_set(string, lang_ngram_set):
    n = len(list(lang_ngram_set)[0])
    return ngram_set(string, n) - lang_ngram_set
