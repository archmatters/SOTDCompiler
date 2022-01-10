import re

separator_pattern = re.compile('\\s*(?:\\\\?-+|–|:|,|\\.|\\|)\\s*')

def strip_separators( text: str ):
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
    return text

