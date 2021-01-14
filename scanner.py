#!/usr/bin/env python3

import makers
import scents

import datetime
import json
import praw
import re

from pathlib import Path

lather_pattern = re.compile('''(?:^|[\n])[^a-z]*
        (?:lather|shaving\\s+(?:soap|cream)|soap/cream|soap|cream\\b)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:WH|ed[pt]|fragrance)|)[^a-z0-9]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
type_suffix_pattern = re.compile('(?: - (?:soap|cream)|\\s*shaving (?:soap|cream)|soap|cream|(?:soap|) sample)\\s*(?:\([^(]+\)|)\\s*$', re.IGNORECASE)
# applied to markdown, hence the backslash
separator_pattern = re.compile('\\s*(?:\\\\?-+|:|,|\\.|\\|)\\s*')
posessive_pattern = re.compile('(?:\'|&#39;|’|)s\\s+', re.IGNORECASE)
by_pattern = re.compile('(.*) by\\s*$', re.IGNORECASE)

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


def removeMarkdown( text ):
    """ Necessarily not correct, as this does not operate on the full body.
    """
    # blind assumption
    text = text.replace('**', '').replace('__', '')
    
    return text


def scanComment( tlc, post_date, dataFile ):
    """ Scans the comment body and writes to the CSV output file (dataFile).
            tlc: the Reddit Comment object
            post_date: the datetime.date object for the post date (not necessarily the comment posted time)
            dateFile: the CSV output file (result of open())
    """
    details = scanBody(tlc)

    author_name = None
    if tlc.author:
        author_name = tlc.author.name

    trim_lather = details['lather']
    if trim_lather is not None:
        trim_lather = trim_lather.strip()
    data = [ post_date.strftime('%Y-%m-%d'),
            datetime.datetime.fromtimestamp(tlc.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            author_name, details['maker'], details['scent'], str(details['confidence']),
            trim_lather, details['plaintext'], 'https://old.reddit.com' + tlc.permalink ]
    dataFile.write('"')
    for i in range(len(data)):
        if i > 0:
            dataFile.write('","')
        if data[i]:
            dataFile.write(data[i].replace('"','""'))
    dataFile.write("\"\n")

ppat = re.compile('<\\s*p\\s*/?>', re.IGNORECASE)
tagpat = re.compile('<[^>]*>')
mnlpat = re.compile("\n\n+")

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

        if maker:
            # some people make it possessive
            result = posessive_pattern.match(scent)
            if result and not str.isspace(maker[-1]):
                scent = scent[result.end():]
        else:
            result = makers.searchMaker(lather)
            if result:
                maker = result['name']
                scent = lather[0:result['match'].start()]
                byes = by_pattern.match(scent)
                if byes:
                    scent = byes.group(1)
                if scent:
                    lpos = len(scent)
                    while not str.isalnum(scent[lpos - 1]):
                        lpos -= 1
                    if lpos < len(scent) and separator_pattern.match(scent, lpos):
                        scent = scent[0:lpos]
            else:
                result = makers.searchMaker(tlc.body)
                if result:
                    #lather = result['match'].group(0)
                    maker = result['name']
                    scent = result['match'].group(1)
                    confidence += 1
                    if result['first']:
                        confidence += 2
                    else:
                        scent = tlc.body[lm.end() - len(lather):result['match'].start()]
            if result and not result['abbreviated']:
                confidence += 1
            # duplicate for now; not ready to merge into a single branch
            if maker and not scent:
                single = scents.getSingleScent(maker)
                if single:
                    # single known scent
                    confidence += 1
                    scent = single
                else:
                    # TODO if not result['first'], look before maker
                    confidence -= 1

        if not maker:
            lpos = lather.find(' - ')
            if lpos > 1:
                maker = lather[0:lpos]
                scent = lather[lpos + 3:]
            if makers.matchMaker(scent) and not makers.matchMaker(maker):
                swap = maker
                maker = scent
                scent = swap
        
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
                scent = removeMarkdown(scent.strip()).title()
        else:
            # TODO shouldn't this be moved up?
            # why was it moved here?
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
            scent = removeMarkdown(scent.strip())

        if not silent:
            if resolved:
                print(f"Matched on '{maker}' / '{scent}' from {tlc.author} ({confidence}; {tlc.id})")
            elif maker and scent:
                print(f"Resolved '{maker}' / '{scent}' ({confidence}; {tlc.id} by {tlc.author})")
            else:
                print(f"OTHER: {lather} ({tlc.id} by {tlc.author})")
    else:
        # duplicate of not maker above
        result = makers.searchMaker(tlc.body)
        if result:
            #lather = result['match'].group(0)
            maker = result['name']
            scent = result['match'].group(1)
            confidence += 1
            if result['first']:
                confidence += 2
            if not result['abbreviated']:
                confidence += 1
            # duplicate for now; not ready to merge into a single branch
            if maker and not scent:
                single = scents.getSingleScent(maker)
                if single:
                    # single known scent
                    confidence += 1
                    scent = single
                else:
                    # TODO if not result['first'], look before maker
                    confidence -= 1
                    if not result['first']:
                        nlpos = tlc.body.rfind("\n", 0, result['match'].start())
                        scent = tlc.body[nlpos + 1:result['match'].start()]

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
            else:
                scent = removeMarkdown(scent.strip()).title()

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
        'confidence': int(confidence * 100 / confidence_max),
        'plaintext': mnlpat.sub("\n", re.sub("^\n+", '', tagpat.sub('', ppat.sub("\n", tlc.body_html))))
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
                'body_html': tlc.body_html,
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


not_cap_pattern = re.compile('(?:a|the|and|in|of|on|for|from|at|to|as|so|into|s|y|la|le|l|n)$', re.IGNORECASE)

#TODO recognize space different from apostrophe
# do not cap after '
# TODO roman numerals??
def titleCase( text ):
    tctext = ''
    pos = 0
    inword = len(text) > 0 and str.isalpha(text[0])
    # recognize ALL CAPS STRING AS DISTINCT from distinct WORDS in all caps
    allcaps = str.isupper(text)
    for i in range(1, len(text) + 1):
        if i == len(text):
            nextword = not inword
        else:
            nextword = str.isalpha(text[i])
        if nextword != inword:
            if inword and (pos == 0 or not not_cap_pattern.match(text, pos, i)
                    ) and (allcaps or not text[pos:i].isupper()):
                tctext += text[pos].upper() + text[pos + 1:i].lower()
            else:
                tctext += text[pos:i].lower()
            pos = i
            inword = nextword
    return tctext

