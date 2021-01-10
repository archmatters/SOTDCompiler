#!/usr/bin/env python3

import makers
import scents

import datetime
import json
import praw
import re

from pathlib import Path

#pre_pattern = re.compile('\\bpre\s*(?:shave|)\\s*\\W*\\s*(\\S.*)', re.IGNORECASE)
#brush_pattern = re.compile('\\bbrush\\s*\\W*\\s*(\\S.*)', re.IGNORECASE)
#lather_pattern = re.compile('\n[^a-z]*(?:lather|shaving\\s+soap|soap|cream|gel\\b)[\\s\\W]*(\\S.*)', re.IGNORECASE)
lather_pattern = re.compile('(?:^|\n)[^a-z]*(?:lather|shaving\\s+(?:soap|cream)|soap|cream|gel\\b)(?:\\s*[/&]\\s*(?:splash|balm)(?:\\s*[/&]\\s*WH|)|)[^a-z0-9]*(\\S.*)', re.IGNORECASE)
type_suffix_pattern = re.compile('(?: - (?:soap|cream)|\\s*shaving (?:soap|cream)|soap|cream)\\s*(?:\([^(]+\)|)\\s*$', re.IGNORECASE)
separator_pattern = re.compile('\\s*(?:-+|:|,|\|)\\s*')
posessive_pattern = re.compile('(?:\'|&#39;|’|)s\\s+', re.IGNORECASE)

sotd_pattern = re.compile('sotd', re.IGNORECASE)
ymd_pattern = re.compile('(\\d{4})-(\\d\\d)-(\\d\\d)', re.IGNORECASE)
mdy_pattern = re.compile('(\\d\\d)/(\\d\\d)/(\\d{2,4})', re.IGNORECASE)
wmdy_pattern = re.compile('([a-z]{2,})\s+(\\d+),?\s+(\\d{2,4})', re.IGNORECASE)
wdmy_pattern = re.compile('(\d+)[^a-z]*([a-z]{2,})[^a-z]*(\\d{2,4})', re.IGNORECASE)

month_words = [ 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec' ]

def getSOTDDate( post ):
    sotd_match = sotd_pattern.search(post.title)
    if not sotd_match:
        return None

    day = 0
    month = 0
    year = 0
    lmw = ''

    dt = wmdy_pattern.search(post.title)
    if dt:
        lmw = dt.group(1).lower()
        day = int(dt.group(2))
        year = int(dt.group(3))
    else:
        dt = wdmy_pattern.search(post.title)
        if dt:
            day = int(dt.group(1))
            lmw = dt.group(2).lower()
            year = int(dt.group(3))
        else:
            dt = ymd_pattern.search(post.title)
            if dt:
                year = int(dt.group(1))
                month = int(dt.group(2))
                day = int(dt.group(3))
            else:
                dt = mdy_pattern.search(post.title)
                if dt:
                    month = int(dt.group(1))
                    day = int(dt.group(2))
                    year = int(dt.group(3))
    if day < 1:
        print(f"Failed to match a date in '{post.title}'")
    elif month == 0 and lmw:
        for i in range(len(month_words)):
            if lmw.startswith(month_words[i]):
                month = i + 1
                break
    if year < 50:
        year += 2000
    elif year < 100 and year >= 50:
        year += 1900
    
    if day > 0:
        return datetime.date(year, month, day)
    else:
        return None


def getThreadComments( post, post_date ):
    # if saved data file exists, load comments from there instead of making a Reddit call
    Path('postdata').mkdir(exist_ok = True)
    cmtFilename = f"postdata/{post_date.strftime('%Y-%m-%d')}-{post.id}.json"
    if Path(cmtFilename).exists():
        with open(file = cmtFilename, mode = 'r', encoding = 'utf8') as cmtFile:
            jscoms = json.load(cmtFile).get("comments")
            rdcoms = [ ]
            for cmt in jscoms:
                if not cmt['author']:
                    cmt['author'] = '[deleted]'
                rdcoms.append(praw.reddit.models.Comment(reddit='Reddit', _data=cmt))
            return rdcoms

    # ensure all top level comments are loaded
    for tlc in post.comments:
        if isinstance(tlc, praw.models.MoreComments):
            post.comments.replace_more(limit=None)
            break

    # save comments so we can quickly rescan during development (see above load)
    saveCommentData(post, cmtFilename)
    
    return post.comments

def scanComment( tlc, post_date, dataFile ):
    """ Scans the comment body and writes to the CSV output file (dataFile).
    """
    details = scanBody(tlc)

    author_name = None
    if tlc.author:
        author_name = tlc.author.name

    data = [ post_date.strftime('%Y-%m-%d'),
            datetime.datetime.fromtimestamp(tlc.created_utc).strftime('%H:%M:%S'),
            author_name, details['maker'], details['scent'], str(details['confidence']),
            details['lather'], 'https://old.reddit.com' + tlc.permalink ]
    dataFile.write('"')
    for i in range(len(data)):
        if i > 0:
            dataFile.write('","')
        if data[i]:
            dataFile.write(data[i].replace('"','""'))
    dataFile.write("\"\n")


def scanBody( tlc, silent = False ):
    """ Returns a dict with the following properties:
          lather: looks like the lather line in the post
          maker: soapmaker, if found
          scent: scent name, if found
          known_maker: if the maker is known to makers.maker_pats
    """

    lather = ''
    maker = ''
    scent = ''
    resolved = False
    confidence_max = 10
    confidence = 0

    # TODO remove markdown but NOT links
    # some people use 'maker - scent [link to scent](http...)
    lm = lather_pattern.search(tlc.body)
    if lm:
        lather = lm.group(1)
        confidence += 2
        result = makers.matchMaker(lather)
        if result:
            maker = result['name']
            scent = result['match'].group(1)
            resolved = True
            confidence += 3

        # fallback case
        if maker and not scent:
            single = scents.getSingleScent(maker)
            if single:
                # single known scent
                confidence += 3
                scent = single
            else:
                confidence -= 2
                lpos = lather.find(' - ')
                if lpos > 1 and not type_suffix_pattern.match(lather, lpos):
                    maker = lather[0:lpos]
                    scent = lather[lpos + 3:]
                    confidence += 1
        elif not scent:
            lpos = lather.find(' - ')
            if lpos > 1:
                maker = lather[0:lpos]
                scent = lather[lpos + 3:]

        # some people make it possessive
        result = posessive_pattern.match(scent)
        if result and not str.isspace(maker[-1]):
            scent = scent[result.end():]

        scent = scent.strip()
        lpos = scent.find('](')
        if lpos > 0:
            bpos = scent.find('[', 0, lpos)
            if bpos > 0:
                scent = scent[0:bpos]
            elif bpos == 0:
                scent = scent[1:lpos]
            else:
                scent = scent[0:lpos]
        
        result = separator_pattern.match(scent)
        if result:
            scent = scent[result.end():]
        
        result = type_suffix_pattern.search(scent)
        if result:
            confidence += 3
            scent = scent[0:result.start()]
        
        scent = scent.strip()

        # now, finally
        if maker:
            result = scents.matchScent(maker, scent)
            if result:
                confidence += 2
                scent = result['name']
        else:
            maker = lather.strip()
            lpos = maker.find('](')
            if lpos > 0:
                bpos = maker.find('[', 0, lpos)
                if bpos > 0:
                    maker = maker[0:bpos]
                elif bpos == 0:
                    maker = maker[1:lpos]
                else:
                    maker = maker[0:lpos]

        if not silent:
            if resolved:
                print(f"Matched on '{maker}' / '{scent}' from {tlc.author} ({confidence}; {tlc.id})")
            elif maker and scent:
                print(f"Resolved '{maker}' / '{scent}' ({confidence}; {tlc.id} by {tlc.author})")
            else:
                print(f"OTHER: {lather} ({tlc.id} by {tlc.author})")
    else:
        result = makers.searchMaker(tlc.body)
        if result:
            confidence += 1
            if result['first']:
                confidence += 2
            if not result['abbreviated']:
                confidence += 1
            maker = result['name']
            scent = result['match'].group(1)
            #lather = result['match'].group(0)
            # duplicate for now; not ready to merge into a single branch
            if maker and not scent:
                single = scents.getSingleScent(maker)
                if single:
                    # single known scent
                    confidence += 1
                    scent = single
                else:
                    confidence -= 1

            # some people make it possessive
            result = posessive_pattern.match(scent)
            if result and not str.isspace(maker[-1]):
                scent = scent[result.end():]

            scent = scent.strip()
            lpos = scent.find('](')
            if lpos > 0:
                bpos = scent.find('[', 0, lpos)
                if bpos > 0:
                    scent = scent[0:bpos]
                elif bpos == 0:
                    scent = scent[1:lpos]
                else:
                    scent = scent[0:lpos]
            
            result = separator_pattern.match(scent)
            if result:
                scent = scent[result.end():]
            
            result = type_suffix_pattern.search(scent)
            if result:
                confidence += 3
                scent = scent[0:result.start()]
            
            scent = scent.strip()

            # now, finally
            result = scents.matchScent(maker, scent)
            if result:
                confidence += 2
                scent = result['name']

            if not silent:
                if resolved:
                    print(f"Matched on '{maker}' / '{scent}' from {tlc.author} ({confidence}; {tlc.id})")
                elif maker and scent:
                    print(f"Resolved '{maker}' / '{scent}' ({confidence}; {tlc.id} by {tlc.author})")
                else:
                    print(f"OTHER: {lather} ({tlc.id} by {tlc.author})")
        elif not silent:
            print(f"FAILED TO MATCH LATHER IN {tlc.id} by {tlc.author}")
    # TODO else try primary maker patterns
    # ... do we need division between primary and abbreviated?
    # or could we try to match known scent and known maker?

    full_lather = lather
    if lm:
        full_lather = lm.group(0)
    return {
        'lather': full_lather,
        'maker': maker,
        'scent': scent,
        'known_maker': resolved,
        'confidence': int(confidence * 100 / confidence_max)
    }


def saveCommentData( post, cmtFilename ):
    with open(file = cmtFilename, mode = 'w', encoding = 'utf8') as cmtFile:
        comment_count = 0
        cmtFile.write('{"comments": [\n')
        for tlc in post.comments:
            comment_count += 1
            author_name = None
            if tlc.author:
                author_name = tlc.author.name
            map = {
                'author': author_name,
                'body': tlc.body,
                'created_utc': tlc.created_utc,
                'id': tlc.id,
                'link_id': tlc.link_id,
                'parent_id': tlc.parent_id,
                'permalink': tlc.permalink,
                'saved': tlc.saved,
                'score': tlc.score,
                'subreddit_id': tlc.subreddit_id
            }
            if comment_count > 1:
                cmtFile.write(",\n")
            cmtFile.write(json.dumps(map))
        cmtFile.write("\n]}")
