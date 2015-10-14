#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import requests
import zipfile
import time
from email.utils import parsedate
from progressbar import ProgressBar
import sqlite3
from ngram import *
import pickle

data_directory = os.path.dirname(__file__) + '/data/'
panlex_database = "http://dev.panlex.org/db/"
panlex_lite_zip = "panlex-lite-latest.zip"
panlex_lite_dir = data_directory + "panlex-lite/"
panlex_lite_db = "db.sqlite"

def get_panlex_lite_zip(force=False):
    try:
        local_mod_time = modified_time(data_directory + panlex_lite_zip)
    except OSError:
        local_mod_time = 0
    remote_mod_time = modified_time(panlex_database + panlex_lite_zip)
    if remote_mod_time - local_mod_time > 43200 or force:
        r = requests.get(panlex_database + panlex_lite_zip, stream=True)
        with open(data_directory + panlex_lite_zip, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            progress = ProgressBar(maxval=(total_length/1024) + 1)
            for chunk in progress(r.iter_content(chunk_size=1024)): 
                if chunk:
                    f.write(chunk)
                    f.flush()

def extract_panlex_lite_db(force=False):
    try:
        db_mod_time = modified_time(panlex_lite_dir + panlex_lite_db)
    except OSError:
        db_mod_time = 0
    zip_mod_time = modified_time(data_directory + panlex_lite_zip)
    if zip_mod_time - db_mod_time > 43200 or force:
        try:
            with zipfile.ZipFile(data_directory + panlex_lite_zip) as zip_file:
                zip_file.extract(panlex_lite_dir + panlex_lite_db)
        except zipfile.BadZipFile:
            get_panlex_lite_zip(force=force)
            with zipfile.ZipFile(data_directory + panlex_lite_zip) as zip_file:
                zip_file.extract(panlex_lite_dir + panlex_lite_db)

def modified_time(file):
    try:
        r = requests.head(file)
        return time.mktime(parsedate(r.headers['last-modified']))
    except requests.models.MissingSchema:
        return os.path.getmtime(file)

try:
    os.mkdir(data_directory)
except FileExistsError: pass

def update_files(force=False):
    get_panlex_lite_zip(force=force)
    extract_panlex_lite_db(force=force)

conn = sqlite3.connect(panlex_lite_dir + panlex_lite_db)
c = conn.cursor()

def language_variety(uid):
    c.execute('SELECT lv.lv FROM lv WHERE lv.uid = ?', (uid,))
    try:
        return c.fetchone()[0]
    except TypeError: 
        raise KeyError("uid not found")

def language_uid(lv):
    c.execute('SELECT lv.uid FROM lv WHERE lv.lv = ?', (lv,))
    try:
        return c.fetchone()[0]
    except TypeError: 
        raise KeyError("lv not found")

def expression_list_from_db(lv, with_score=False, progress_bar=False):
    try:
        lv = language_variety(lv)
    except KeyError:
        pass
    c.execute('SELECT ex.tt FROM ex WHERE ex.lv = ?', (lv,))
    ex_list = [record[0] for record in c.fetchall()]
    if with_score:
        if progress_bar:
            progress = ProgressBar()
            score_list = [expression_score_from_db(expr, lv) for expr in progress(ex_list)]
        else:
            score_list = [expression_score_from_db(expr, lv) for expr in ex_list]
        if ex_list and score_list: return zip(ex_list, score_list)
        else: raise KeyError("lv not found")
    else:
        if ex_list: return ex_list
        else: raise KeyError("lv not found")

def save_expression_list(uid, force=False, progress_bar=False):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    pickle_file = panlex_lite_dir + uid + '_ex.tt.pickle'
    try:
        pickle_file_mod_time = modified_time(pickle_file)
    except OSError:
        pickle_file_mod_time = 0
    db_mod_time = modified_time(panlex_lite_dir + panlex_lite_db)
    if db_mod_time - pickle_file_mod_time > 43200 or force:
        with open(pickle_file, 'wb') as file:
            pickle.dump(expression_list_from_db(uid, with_score=True, progress_bar=progress_bar), file, protocol=-1)

def expression_score_from_db(expr, lv):
    try:
        lv = language_variety(lv)
    except KeyError:
        pass
    c.execute('''
        SELECT sum(uq) FROM ( 
            SELECT max(uq) AS uq FROM ( 
                SELECT dnx.ui, dnx.uq FROM ex JOIN dnx ON (dnx.ex = ex.ex) WHERE ex.lv = ? AND ex.tt = ?
                ) a GROUP BY ui) b
            ''', (lv, expr))
    try:
        return c.fetchone()[0]
    except TypeError: 
        raise KeyError("expression not found")

def expression_list_from_disk(uid, with_score=False):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    pickle_file = panlex_lite_dir + uid + '_ex.tt.pickle'
    try:
        with open(pickle_file, 'rb') as file:
            if with_score:
                return list(pickle.load(file))
            else:
                return [expr[0] for expr in pickle.load(file)]
    except FileNotFoundError:
        save_expression_list(uid, force=True)
        with open(pickle_file, 'rb') as file:
            if with_score:
                return list(pickle.load(file))
            else:
                return [expr[0] for expr in pickle.load(file)]

_expression_lists = {}
def _initialize_expression_list(uid):
    global _expression_lists
    if uid not in _expression_lists:
        _expression_lists[uid] = dict(expression_list_from_disk(uid, with_score=True))

def expression_score(expr, uid):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    _initialize_expression_list(uid)
    try:
        return _expression_lists[uid][expr]
    except KeyError:
        return 0

def expression_list(uid):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    _initialize_expression_list(uid)
    return list(_expression_lists[uid].keys())

def expression_set(uid):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    _initialize_expression_list(uid)
    return set(_expression_lists[uid].keys())

def save_ngram_set(uid, n, force=False):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    pickle_file = panlex_lite_dir + uid + '_' + str(n) + '-grams.pickle'
    try:
        pickle_file_mod_time = modified_time(pickle_file)
    except OSError:
        pickle_file_mod_time = 0
    db_mod_time = modified_time(panlex_lite_dir + panlex_lite_db)
    if db_mod_time - pickle_file_mod_time > 43200 or force:
        ngram_set = list_ngram_set(expression_list_from_disk(uid), n)
        with open(pickle_file, 'wb') as file:
            pickle.dump(ngram_set, file, protocol=-1)

def ngram_set_from_disk(uid, n):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    pickle_file = panlex_lite_dir + uid + '_' + str(n) + '-grams.pickle'
    try:
        with open(pickle_file, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        save_ngram_set(uid, n, force=True)
        with open(pickle_file, 'rb') as file:
            return pickle.load(file)

_ngram_sets = {}
def _initialize_ngram_set(uid, n):
    global _ngram_sets
    if uid not in _ngram_sets:
        _ngram_sets[uid] = {}
    if n not in _ngram_sets[uid]:
        _ngram_sets[uid][n] = ngram_set_from_disk(uid, n)

def ngram_set(uid, n):
    try:
        uid = language_uid(uid)
    except KeyError:
        pass
    _initialize_ngram_set(uid, n)
    return _ngram_sets[uid][n]



