#!/usr/bin/env python3

import datetime
import json

import praw

import scanner
import makers
import scents

from pathlib import Path

# spot check for the given data file pattern, username, and comment ID
check_glob = '2020-12-*.json'
check_name = ''
check_id = ''

data_dir = Path('postdata')
if not data_dir.is_dir():
    raise Exception('No postdata directory!  I cannot find saved data.')

for name in data_dir.glob(check_glob):
    with open(file=name, mode='r', encoding='utf8') as cmt_file:
        jscoms = json.load(cmt_file).get('comments')
        for map in jscoms:
            if check_id and not check_id == map['id'] and not check_id == map['permalink']:
                continue
            if not map['author']:
                map['author'] = '[deleted]'
            if check_name and not check_name.lower() == map['author'].lower():
                continue
            comment = praw.reddit.models.Comment(reddit='Reddit', _data=map)
            scanner.scanBody(comment)
    
# TODO maybe also note if makers are missing scent patterns
