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
check_glob = '2020-*.json'

data_dir = Path('postdata')
if not data_dir.is_dir():
    raise Exception('No postdata directory!  I cannot find saved data.')


def normalCheck( author, id ):
    for name in data_dir.glob(check_glob):
        with open(file=name, mode='r', encoding='utf8') as cmt_file:
            jscoms = json.load(cmt_file).get('comments')
            for map in jscoms:
                if id and not id == map['id'] and not id == map['permalink']:
                    continue
                if not map['author']:
                    map['author'] = '[deleted]'
                if author and not author.lower() == map['author'].lower():
                    continue
                comment = praw.reddit.models.Comment(reddit='Reddit', _data=map)
                scanner.scanBody(comment)



# TODO maybe also note if makers are missing scent patterns

normalCheck( author = '', id = 'g7imia1' )

