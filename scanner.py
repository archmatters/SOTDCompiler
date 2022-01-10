#!/usr/bin/env python3

import makers
import scents
from common import strip_separators, separator_pattern

import datetime
import re


lather_pattern = re.compile('''(?:^|[\n])[^a-z0-9]*
        (?:soap/lather|lath?er|shav(?:ing|e)\\s+(?:soap|cream)|soap/cream|soa+p|cream|softw[ae]re)\\b
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|post|)
        (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:WH|ed[pt]|fragrance)|)
        (?!\\s*games)[\\W_]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
lather_alt_pattern = re.compile('''(?:^|[\n])[^a-z]*
        (?:
            (?:(?<!\\#)shave\\b)
            (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:splash|balm|(?:after|post)\\s*shave)|post|)
            (?:\\s*(?:/|&(?:amp;|)|and|\\+)\\s*(?:ed[pt]|fragrance)|)
        |
            soft\\s*goods
        |
            pre[\\- ]?shave/(?:soap|cream)/(?:balm|after[\\- ]?shave|splash)
        )[^a-z0-9]*(\\S.*)''', re.IGNORECASE | re.VERBOSE)
# applied to markdown, hence the backslash
possessive_pattern = re.compile('(?:\'|&#39;|’|)s\\s+', re.IGNORECASE)
by_pattern = re.compile('(.*?)\\s+(?:by|from)\\s*$', re.IGNORECASE)
sample_pattern = re.compile('\\s*[\\(\\[]?sample(?: size|)[\\)\\]]?\\s*$', re.IGNORECASE)
quoted_pattern = re.compile('\\s*(["\'])(.*)\\1\\s*')
non_alpha_pattern = re.compile('\W*')
unknown_scent_pattern = re.compile('shav(?:ing|e)(?:\\s*(?:soap|cream)|)\\s*$', re.IGNORECASE)
md_link_pattern = re.compile('\\]\\s*\\(')

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


def scanComment( tlc, post_date, dataFile, delimiter ):
    """ Scans the comment body and writes to the CSV output file (dataFile).
            tlc: the Reddit Comment object
            post_date: the datetime.date object for the post date (not necessarily the comment posted time)
            dateFile: the CSV output file (result of open())
            delimiter: the delimiter to use, comma ',' or tab '\\t'
    """
    details = scanBody(tlc)

    author_name = None
    if tlc.author:
        author_name = tlc.author.name

    trim_lather = details.lather
    if trim_lather is not None:
        trim_lather = trim_lather.strip()
    comment_url = 'https://old.reddit.com' + tlc.permalink
    rpos = len(comment_url) - 1
    if comment_url[rpos] == '/':
        rpos = comment_url.rfind('/', 0, rpos)
    thread_url = comment_url[0:rpos + 1]
    data = [ post_date.strftime('%Y-%m-%d'),
            datetime.datetime.fromtimestamp(tlc.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            author_name, details.maker, details.scent, details.getConfidenceText(),
            trim_lather, tlc.id, details.plaintext, thread_url ]

    if delimiter == ',':
        dataFile.write('"')
    for i in range(len(data)):
        if delimiter == "\t" and i >= 8:
            continue
        if i > 0:
            if delimiter == ',':
                dataFile.write('","')
            else:
                dataFile.write(delimiter)
        if data[i]:
            text = data[i]
            if delimiter == ',':
                text = text.replace('"', ' ')
            else:
                text = text.replace(delimiter, ' ').replace('\n', ' ').replace('\r', '')
            dataFile.write(text)
    if delimiter == ',':
        dataFile.write('"')
    dataFile.write("\n")


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
    result = md_link_pattern.search(text)
    if result and result.start() > 0:
        lpos = result.start()
        bpos = text.find('[', 0, lpos)
        if bpos > 0:
            result = non_alpha_pattern.match(text[0:bpos])
            if result and result.end() >= bpos:
                text = text[bpos+1:lpos]
            else:
                text = text[0:bpos]
        elif bpos == 0:
            text = text[1:lpos]
        else:
            text = text[0:lpos]

    text = removeMarkdown(text)
    text = strip_separators(text)

    text = text.strip()
    if text.endswith('.') or text.endswith(','):
        text = text[0:-1]

    result = sample_pattern.search(text)
    if result:
        text = text[0:result.start()]

    result = possessive_pattern.match(text)
    if result: # TODO check that the apostrophe is not preceded by a space
        text = text[result.end():]

    result = quoted_pattern.match(text)
    if result:
        text = result.group(2)
    else:
        bpos = text.find('“')
        if bpos >= 0:
            lpos = text.find('”', bpos)
            if lpos > bpos:
                text = text[bpos+1:lpos]
    text = text.strip()

    result = scents.match_scent(lather.maker, text)
    # TODO confidence boost here really should be based on the
    # proportion of text matched (including base name)
    # ALSO, note that if we match a base, but not scent, that should
    # be a smaller confidence boost, but is treated the same!
    # TODO #2 if matching fails with text after the maker,
    # try the text before... but check all code paths into
    # this function.
    if result and result['match']:
        lather.maker = result['maker']
        lather.scent = result['scent']
        lather.context += 'X'
        lather.confidence += 4
        return True
    elif result:
        # TODO need to consolidate unknown_scent_pattern
        # with type_suffix_pattern in scents.py
        if unknown_scent_pattern.match(result['scent']):
            lather.scent = 'Unknown'
        else:
            lather.scent = result['scent']
        lather.context += 'Y'
        lather.confidence += 3
    elif unknown_scent_pattern.match(text):
        lather.scent = 'Unknown'
    elif len(lather.scent) > 0:
        lather.scent = scents.title_case(text)
        lather.context += 'Y'
        lather.confidence += 3
    return False


def scanBody( tlc, silent = False ):
    """ Always returns a LatherMatch object.
    """
    lather = LatherMatch(body_html=tlc.body_html)
    # L if lather; [MNO] for maker, [B][1XYS] for scent, - for manual entry

    if not tlc.author and tlc.body == '[deleted]':
        return lather

    # TODO remove markdown but NOT links
    # some people use 'maker - scent [link to scent](http...)
    lmr = lather_pattern.search(tlc.body)
    if not lmr:
        lmr = lather_alt_pattern.search(tlc.body)
        if not lmr:
            lmr = re.search('lathe\\**r\\**\\s*[:\\-]?\\s*(.*)', tlc.body, re.IGNORECASE)
            if lmr: 
                lather.confidence -= 2
    if lmr:
        lather.lather = lmr.group(1).strip()
        lather.context = 'L'
        lather.confidence += 3
        # TODO match "N/A", "none", "nothing" ??
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
        elif lather.maker and scents.isSingleScent(lather.maker):
            lather.context += '1'
            lather.confidence += 2
            lather.scent = scents.getSingleScent(lather.maker)
        elif lather.maker:
            result = scents.match_scent(lather.maker, lather.scent)
            if result:
                lather.scent = result['scent']
            else:
                lather.confidence -= 1
        else:
            # TODO find a better place to do this
            lather.lather = lather.lather.replace('&#39;', '\'').replace('&amp;', '&')
            pos = lather.lather.find(' - ')
            if pos < 0:
                pos = lather.lather.find(' – ')
            if pos > 0:
                lather.maker = lather.lather[0:pos]
                lather.scent = lather.lather[pos+3:]
                # TODO should this use findany?
                # I don't think so... if scent can be identified by findany, then
                # how did we fail to match the maker?
                # Answer: Chatillon Lux is not a known maker, but has known scents
                cleanAndMatchScent(lather)
            else:
                result = separator_pattern.search(lather.lather)
                if result:
                    lather.maker = lather.lather[0:result.start()]
                    lather.scent = scents.title_case(lather.lather[result.end():])
                else:
                    # TODO needs to be more discriminating still?
                    result = scents.findAnyScent(lather.lather)
                    if result:
                        lather.context += 'S'
                        lather.maker = result['maker']
                        lather.scent = result['scent']
                    else:
                        lather.maker = lather.lather

        if lather.maker:
            print(f'Primary match "{lather.maker}" / "{lather.scent}" ({lather.getConfidenceText()}) in {tlc.id} by {tlc.author}')
        else:
            result = scentFirst(tlc.body, lather.lather)
            if result:
                lather.maker = result['maker']
                lather.scent = result['scent']
                lather.context += 'S'
                # TODO confidence boost based on proportion of text matched?
                lather.confidence += 2
                print(f'Scent-first match on "{lather.maker}" / "{lather.scent}" ({lather.getConfidenceText()}) in {tlc.id} by {tlc.author}')
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
            print(f'Body match "{lather.maker}" / "{lather.scent}" ({lather.getConfidenceText()}) in {tlc.id} by {tlc.author}')
        else:
            result = scentFirst(tlc.body, None)
            if result:
                lather.lather = result['lather']
                lather.maker = result['maker']
                lather.scent = result['scent']
                lather.context += 'S'
                # TODO confidence boost should be based on proportion text matched
                lather.confidence += 2
                print(f'Scent-first match on "{lather.maker}" / "{lather.scent}" ({lather.getConfidenceText()}) in {tlc.id} by {tlc.author}')
            else:
                print(f'No lather in {tlc.id} by {tlc.author}')
    if lmr:
        lather.lather = lmr.group(0).strip()
    return lather

