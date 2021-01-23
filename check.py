#!/usr/bin/env python3

import datetime
import json
import re

import praw

import scanner
import makers
import scents

from pathlib import Path

# spot check for the given data file pattern, username, and comment ID
check_glob = '202*.json'

data_dir = Path('postdata')
if not data_dir.is_dir():
    raise Exception('No postdata directory!  I cannot find saved data.')


def normalCheck( author = None, ids = None ):
    for name in data_dir.glob(check_glob):
        with open(file=name, mode='r', encoding='utf8') as cmt_file:
            jscoms = json.load(cmt_file).get('comments')
            for map in jscoms:
                if not map['author']:
                    map['author'] = '[deleted]'
                match = not author or author.lower() == map['author'].lower()
                if match:
                    match = not ids or len(ids) == 0 or map['id'] in ids
                if match:
                    comment = praw.reddit.models.Comment(reddit='Reddit', _data=map)
                    scanner.scanBody(comment)



# TODO maybe also note if makers are missing scent patterns

normalCheck( author = '120inna55', ids = [''] )


