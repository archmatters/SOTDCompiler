#!/usr/bin/env python3

import makers
import scents

import datetime
import json
import praw
import re

from pathlib import Path

lather_pattern = re.compile('''(?:^|[\n])[^a-z]*
        (?:soap/lather|lather|shav(?:ing|e)\\s+(?:soap|cream)|soap/cream|soap|cream\\b)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|post|)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:WH|ed[pt]|fragrance)|)[^a-z0-9]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
lather_alt_pattern = re.compile('''(?:^|[\n])[^a-z]*
        (?:shave\\b)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|post|)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:ed[pt]|fragrance)|)[^a-z0-9]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
type_suffix_pattern = re.compile('(?:\\s*[\\-,]\\s*(?:soap|cream)|\\s*shav(?:ing|e) (?:soap|cream)|soap|cream|(?:soap\\s*|)sample)\\s*(?:\([^(]+\)|)\\s*$', re.IGNORECASE)
# applied to markdown, hence the backslash
separator_pattern = re.compile('\\s*(?:\\\\?-+|:|,|\\.|\\||–)\\s*')
possessive_pattern = re.compile('(?:\'|&#39;|’|)s\\s+', re.IGNORECASE)
by_pattern = re.compile('(.*?)\\s+(?:by|from)\\s*$', re.IGNORECASE)
sample_pattern = re.compile('\\s*\\(sample(?: size|)\\)\\s*$', re.IGNORECASE)
quoted_pattern = re.compile('\\s*(["\'])(.*)\\1\\s*')

sotd_pattern = re.compile('sotd', re.IGNORECASE)
ymd_pattern = re.compile('(\\d{4})-(\\d\\d)-(\\d\\d)', re.IGNORECASE)
mdy_pattern = re.compile('(\\d\\d)/(\\d\\d)/(\\d{2,4})', re.IGNORECASE)
wmdy_pattern = re.compile('([a-z]{2,})\s+(\\d+),?\s+(\\d{2,4})', re.IGNORECASE)
wdmy_pattern = re.compile('(\d+)[^a-z]*([a-z]{2,})[^a-z]*(\\d{2,4})', re.IGNORECASE)

month_words = [ 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec' ]

# strip HTML tags
ppat = re.compile('<\\s*p\\s*/?>', re.IGNORECASE)
tagpat = re.compile('<[^>]*>')
mnlpat = re.compile("\n\n+")

class LatherMatch:
    lather = ''
    maker = ''
    scent = ''
    confidence = 0
    context = ''
    plaintext = ''

    def __init__( self, body_html: str ):
        self.plaintext = mnlpat.sub("\n", re.sub("^\n+", '', tagpat.sub('', ppat.sub("\n", body_html))))

    def getConfidenceText( self ):
        return str(self.confidence) + '.' + self.context


def get_sotd_date( post ):
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


def removeMarkdown( text: str ):
    """ Necessarily not correct, as this does not operate on the full body.
    """
    clean = ''
    for i in range(len(text)):
        if text[i] == '*' or text[i] == '_' or text[i] == '\\':
            if i == 0 or (i > 0 and text[i - 1] != '\\'
                    and ((i < len(text) - 1 and (text[i - 1] != ' ' or text[i + 1] != ' '))
                    or (i == len(text) - 1 and text[i - 1] != ' '))):
                continue
        clean += text[i]
    return clean


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

    trim_lather = details.lather
    if trim_lather is not None:
        trim_lather = trim_lather.strip()
    data = [ post_date.strftime('%Y-%m-%d'),
            datetime.datetime.fromtimestamp(tlc.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            author_name, details.maker, details.scent, details.getConfidenceText(),
            trim_lather, tlc.id, 'https://old.reddit.com' + tlc.permalink ]
    dataFile.write('"')
    for i in range(len(data)):
        if i > 0:
            dataFile.write('","')
        if data[i]:
            dataFile.write(data[i].replace('"','""'))
    dataFile.write("\"\n")


def scentFirst( body: str, lather: str ):
    result = None
    if lather:
        result = scents.findAnyScent(lather.strip())
    else:
        for line in body.split("\n"):
            if line.strip():
                result = scents.findAnyScent(line.strip())
                if result:
                    break
    return result


def cleanAndMatchScent( lather: LatherMatch ):
    text = lather.scent
    lpos = text.find('](')
    if lpos > 0:
        bpos = text.find('[', 0, lpos)
        if bpos > 0:
            text = text[0:bpos]
        elif bpos == 0:
            text = text[1:lpos]
        else:
            text = text[0:lpos]

    text = removeMarkdown(text)

    lpos = 0
    while lpos < len(text):
        result = separator_pattern.search(text, lpos)
        if result:
            if result.start() == 0:
                text = text[result.end():]
            elif result.end() == len(text):
                text = text[0:result.start()]
            lpos = result.end()
        else:
            lpos = len(text)

    text = text.strip()
    if text.endswith('.') or text.endswith(','):
        text = text[0:-1]

    result = sample_pattern.search(text)
    if result:
        text = text[0:result.start()]

    result = type_suffix_pattern.search(text)
    if result:
        text = text[0:result.start()]

    result = quoted_pattern.match(text)
    if result:
        text = result.group(2)
    text = text.strip()

    result = scents.matchScent(lather.maker, text)
    if result:
        lather.scent = result['name']
        lather.context += 'X'
        lather.confidence += 4
        return True
    elif len(lather.scent) > 0:
        lather.scent = text
        lather.context += 'Y'
        lather.confidence += 3
    return False


def scanBody( tlc, silent = False ):
    """ Always returns a LatherMatch object.
    """
    lather = LatherMatch(body_html=tlc.body_html)
    # L if lather; [MNO] for maker, [B][1XYS] for scent

    if not tlc.author and tlc.body == '[deleted]':
        return lather

    # TODO remove markdown but NOT links
    # some people use 'maker - scent [link to scent](http...)
    lmr = lather_pattern.search(tlc.body)
    if not lmr:
        lmr = lather_alt_pattern.search(tlc.body)
    if lmr:
        lather.lather = lmr.group(1).strip()
        lather.context = 'L'
        lather.confidence = 3
        result = makers.matchMaker(lather.lather)
        if result:
            lather.maker = result['name']
            lather.scent = result['match'].group(1)
            lather.context += 'M'
            if result['abbreviated']:
                lather.confidence += 2
            else:
                lather.confidence += 3
        else:
            result = makers.searchMaker(lather.lather)
            if result:
                lather.maker = result['name']
                lather.scent = result['match'].group(1)
                if result['abbreviated']:
                    lather.context += 'O'
                    lather.confidence += 1
                else:
                    lather.context += 'N'
                    lather.confidence += 2
                pretext = lather.lather[0:result['match'].start()].strip()
                result = by_pattern.match(pretext)
                if result:
                    lather.scent = result.group(1)
                    lather.context += 'B'
                elif not lather.scent:
                    lather.scent = pretext
                    lather.context += 'B'

        if lather.scent:
            cleanAndMatchScent(lather)
        elif lather.maker and scents.getSingleScent(lather.maker):
            lather.context += '1'
            lather.confidence += 2
        elif lather.maker:
            lather.confidence -= 1

        if lather.maker:
            print(f'Primary match "{lather.maker}" / "{lather.scent}" in {tlc.id} by {tlc.author}')
        else:
            result = scentFirst(tlc.body, lather.lather)
            if result:
                lather.maker = result['maker']
                lather.scent = result['scent']
                lather.context += 'S'
                lather.confidence += 2
                print(f'Scent-first match on "{lather.maker}" / "{lather.scent}" in {tlc.id} by {tlc.author}')
            else:
                print(f'No match against "{lather.lather}" in {tlc.id} by {tlc.author}')
    else:
        result = makers.searchMaker(tlc.body)
        if result:
            # TODO need to better handle <scent>{-|by|from}<maker>
            lather.lather = result['match'].group(0)
            lather.maker = result['name']
            lather.scent = result['match'].group(1)
            if result['abbreviated']:
                lather.context += 'O'
                lather.confidence += 2
            else:
                lather.context += 'N'
                lather.confidence += 3
            if not result['first']:
                lather.confidence -= 2
        if lather.scent:
            cleanAndMatchScent(lather)
        if lather.maker:
            print(f'Body match "{lather.maker}" / "{lather.scent}" in {tlc.id} by {tlc.author}')
        else:
            result = scentFirst(tlc.body, None)
            if result:
                lather.lather = result['lather']
                lather.maker = result['maker']
                lather.scent = result['scent']
                lather.context += 'S'
                lather.confidence += 2
                print(f'Scent-first match on "{lather.maker}" / "{lather.scent}" in {tlc.id} by {tlc.author}')
            else:
                print(f'No lather in {tlc.id} by {tlc.author}')
    if lmr:
        lather.lather = lmr.group(0).strip()
    return lather




not_cap_pattern = re.compile('(?:a|the|and|in|of|on|for|from|at|to|as|so|into|s|y|la|le|l|n)$', re.IGNORECASE)

def titleCase( text: str ):
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
            candidate = inword and (pos == 0 or (text[pos - 1].isspace()))
            capword = allcaps or not text[pos].isupper()
            if candidate and capword and (pos == 0 or not not_cap_pattern.match(text, pos, i)):
                tctext += text[pos].upper() + text[pos + 1:i].lower()
            elif candidate and capword and not_cap_pattern.match(text, pos, i):
                tctext += text[pos:i].lower()
            else:
                tctext += text[pos:i]
            pos = i
            inword = nextword
    return tctext

