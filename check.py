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


def test_lather_patterns( ):
    # logic matches scanner.scanBody() as of May 23, 2021
    # are we testing a change to the main, or alt?
    testing_alt = False
    test_pattern = re.compile('''(?:^|[\n])[^a-z0-9]*
        (?:soap/lather|lath?er|shav(?:ing|e)\\s+(?:soap|cream)|soap/cream|soap|cream|software)\\b
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|post|)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:WH|ed[pt]|fragrance)|)[^a-z0-9]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
    for name in data_dir.glob(check_glob):
        with open(file=name, mode='r', encoding='utf8') as cmt_file:
            jscoms = json.load(cmt_file).get('comments')
            for map in jscoms:
                if not map['author']:
                    map['author'] = '[deleted]'
                comment = praw.reddit.models.Comment(reddit='Reddit', _data=map)

                if not comment.author and comment.body == '[deleted]':
                    continue

                state = 0
                ltext = None
                lmr = scanner.lather_pattern.search(comment.body)
                if lmr:
                    state = 1
                else:
                    lmr = scanner.lather_alt_pattern.search(comment.body)
                    if lmr:
                        state = 2
                if lmr:
                    ltext = lmr.group(1).strip()
                
                if testing_alt and state == 1:
                    continue

                lt_test = None
                lmr = test_pattern.search(comment.body)
                if lmr:
                    lt_test = lmr.group(1).strip()
                if testing_alt:
                    if lmr:
                        # if state == 1, we don't get this far; see above
                        if state == 0:
                            print(f"{comment.id} now matches alt: '{lt_test}'")
                        elif lt_test != ltext:
                            print(f"{comment.id} yields different alt match text:\n  orig='{ltext}'\n  test={lt_test}")
                    elif state == 2:
                        print(f"{comment.id} NOW FAILS to match the alt pattern!")
                else:
                    if lmr:
                        if state == 0:
                            print(f"{comment.id} now matches: '{lt_test}'")
                        elif state == 2:
                            print(f"{comment.id} now matches first (was alt):\n  alt='{ltext}'\n  test={lt_test}'")
                        elif lt_test != ltext:
                            print(f"{comment.id} yields different match:\n  orig='{ltext}'\n  test={lt_test}'")
                    elif state == 1:
                        lmr = scanner.lather_alt_pattern.search(comment.body)
                        if lmr:
                            lt_test = lmr.group(1).strip()
                            if lt_test == ltext:
                                print(f"{comment.id} falls back to an identical alt match: '{lt_test}'")
                            else:
                                print(f"{comment.id} falls back to a different alt match:\n  orig='{ltext}'\n  alt='{lt_test}'")
                        else:
                            print(f"{comment.id} NOW FAILS to match either core or alt patterns!")


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

normalCheck( author = '', ids = [ 'gpne3px', 'gt0v5b5' ] )


