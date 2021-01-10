#!/usr/bin/env python3

import re

_apostophe = '(?:\'|&#39;|’|)'
_ending = '\\s*(.*)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'

_maker_pats = {
    # known soapmakers
    'abbate y la mantia': 'Abbate y la Mantia',

    'acqua di parma': 'Acqua di Parma',

    'apex alchemy\\s*(?:soaps?|)': 'Apex Alchemy Soaps',

    'ariana' + _any_and + 'evans': 'Ariana & Evans',

    'arko': 'Arko',

    'art of shaving': 'Art of Shaving',

    'archaic alchemy': 'Archaic Alchemy',

    'arran': 'Arran',

    'australian private reserve': 'Australian Private Reserve',

    'barbus': 'Barbus',

    'barrister' + _any_and + 'mann\\s*[/x×]\\s*zingari': 'Zingari Man',
    'barrister' + _any_and + 'mann?': 'Barrister and Mann',

    'black ship\\s(?:grooming\\s*(?:co\\.?|)|)': 'Black Ship Grooming Co.',

    'bufflehead': 'Bufflehead',

    'c\\.?\\s*o\\.?\\s*bigelow': 'C.O. Bigelow',

    'captain' + _apostophe + 's choice': 'Captain\'s Choice',

    'castle forbes': 'Castle Forbes',

    'catie' + _apostophe + 's bubbles': 'Catie\'s Bubbles',
    'sfws\\s*/\\s*catie' + _apostophe + 's bubbles': 'Catie\'s Bubbles',

    'cbl\\b\\s+(?:soaps?|)': 'CBL Soaps',

    'cella': 'Cella',

    'central texas (?:soaps?|)': 'Central Texas Soaps',

    'oleo\\s*(?:soap|soapworks|)': 'Chicago Grooming Co.',
    'chicago groom\\w+\\s*(?:company|co\\.?)\\s*(?:\(formerly[^)]+\)|)': 'Chicago Grooming Co.',

    'chiseled face': 'Chiseled Face',
    'zoologist(?: perfumes|)\\s*/\\s*chiseled face': 'Chiseled Face',
    'chiseled face\\s*/\\s*zoologist(?: perfumes|)': 'Chiseled Face',

    'cold river\\s*(?:soap\\s*works)': 'Cold River Soap Works',

    '(?:col(?:onel|\\.|)\\s*|)conk': 'Col. Conk',

    'crabtree' + _any_and + 'evelyn': 'Crabtree & Evelyn',

    'cremo': 'Cremo',

    'd\\.?\\s*r\\.?\\s*harris': 'D.R. Harris',

    'dindi naturals': 'Dindi Naturals',

    'Declaration Grooming/Chatillon Lux': 'Declaration Grooming',
    'Declaration Grooming/Maggard Razors': 'Declaration Grooming',
    'declaration\\s*(?:grooming|)': 'Declaration Grooming',
    'Chatillon Lux/Declaration Grooming': 'Declaration Grooming',

    'dr.? joh?n' + _apostophe + 's': 'Dr. Jon\'s',

    'edwin jagg[ea]r': 'Edwin Jagger',

    'eleven': 'Eleven Shaving',

    'ethos': 'ETHOS',

    'eufros': 'Eufros',

    'executive shaving': 'Executive Shaving',

    'fenom[ei]no\\s*(?:shave|)': 'Fenomeno Shave',

    'fine\\s*(?:accoutrements|)': 'Eleven',

    'first canadian\\s*(?:shave soap\\s*(?:company|co.?|)|)': 'First Canadian Shave Soap Co.',

    'floris\\s*(?:(?:of|)\\s*london|)': 'Floris London',

    'fitjar\\s*(?:islands?|)': 'Fitjar Islands',

    'fuzzy\\s*face(?: soaps|)': 'Fuzzyface Soaps',

    'geo\\.?\\s*f\\.?\\s*trumper': 'Geo. F. Trumper',

    'gentlem[ae]n' + _apostophe + 's? nod': 'Gentleman\'s Nod',

    'gillette': 'Gillette',

    '(?:the|)\\s*goodfella' + _apostophe + 's' + _apostophe + '\\s*(?:smile|)': 'The Goodfellas\' Smile',

    'grooming dep[at]\\S*': 'Grooming Department',

    'haslinger': 'Haslinger',

    'henri et victoria': 'Henri et Victoria',

    'henri et victoria': 'Henri et Victoria',

    'heritage hill(?: shave\\s*(?:company|co\\.?)|)': 'Heritage Hill Shave Company',

    'highland spring soap\\s*(?:company|co\\.?)': 'Highland Springs Soap Company',
    'highland spring': 'Highland Springs Soap Company',

    'hub city\\s*(?:soap (?:company|co\\.?))': 'Hub City Soap Company',

    'imperial\\s*(?:barber (?:products|grade products?|)|)': 'Imperial Barber',
    
    'l' + _apostophe + 'occitane': 'L\'Occitane',

    'la toja': 'La Toja',
    
    'like grandpa': 'Like Grandpa',
    
    '(?:los angeles|la) shaving soap (?:company|co\\.?)': 'Los Angeles Shaving Soap Company',
    
    'maggard\\s*(?:razors?|)': 'Maggard Razors',
    'maggard' + _apostophe: 'Maggard Razors',

    'maol\\s*(?:grooming|)': 'Maol Grooming',

    'mama bear': 'Mama Bear',

    'mammoth\\s*(?:soaps?|)': 'Mammoth Soaps',

    'martin de candre': 'Martin de Candre',

    'micke?y lee soap\w+': 'Mickey Lee Soapworks',

    'mike(?:\'|&#39;|’|)s natural soaps?': 'Mike\'s Natural Soaps',

    'mitchell(?:\'|&#39;|’|)s\\s*(?:wool fat|)': 'Mitchell\'s Wool Fat',

    'm[üu]hle': 'Mühle',

    'murphy' + _any_and + 'mcneil': 'Murphy and McNeil',

    'mystic water\\s*(?:soaps?|)': 'Mystic Water Soap',

    'noble otter': 'Noble Otter',
    'australian private reserve\\s*/\\s*noble otter': 'Noble Otter',
    'apr\\s*/\\s*no': 'Noble Otter',
    'no\\s*/\\s*apr': 'Noble Otter',

    'obsessive soap(?:s|\\s+perfect\w+|)': 'Obsessive Soap Perfectionist',
    'osp(?:\\s*soaps?|\\b)': 'Obsessive Soap Perfectionist',

    'ogalalla': 'Ogalalla',

    'old spice': 'Old Spice',

    'oz shaving': 'Oz Shaving',

    'palmolive': 'Palmolive',

    'panna\\s*crema': 'PannaCrema',

    'paragon shaving': 'Paragon Shaving',

    'ph[oe]+nix' + _any_and + 'beau': 'Phoenix and Beau',

    'phoenix artisan accoutrements': 'Phoenix Artisan Accoutrements',

    'pr[ée] de provence': 'Pré de Provence',

    'pro(?:raso|saro)': 'Proraso',

    'pinnacle grooming': 'Pinnacle Grooming',

    'razorock': 'RazoRock',

    'red house farms': 'Red House Farms',
    '(?:u/|)grindermonk' + _apostophe + 's?': 'Red House Farms',

    'reef point\\s*(?:soaps?)': 'Reef Point Soaps',

    'saponificio\\s*varesino': 'Saponificio Varesino',

    'seaforth!?': 'Seaforth!',

    'shannon' + _apostophe + 's soaps': 'Shannon\'s Soaps',

    's\\s*h\\s*a\\s*v\\s*e.{0,4}d\\s*a\\s*n\\s*d\\s*y': 'SHAVE DANDY',

    'siliski soaps': 'Siliski Soaps',

    'soap commander': 'Soap Commander',

    'some irish guy' + _apostophe + 's': 'Some Irish Guy\'s',

    'southern witchcrafts?': 'Southern Witchcrafts',
    'Australian Private Reserve/Southern Witchcrafts': 'Southern Witchcrafts',
    'southern witchcrafts\\s*/\\s*apr\\b': 'Southern Witchcrafts',

    'spearhead\\s*(?:(?:shaving|soap)\\s*(?:company|co.?|)|)': 'Spearhead Shaving Company',

    'sp[ei]{2}c?k': 'Speick',

    'st[ei]rl[ei]ng\s*(?:soap\s*(?:company|co\\.?|)|)(.*)': 'Stirling Soap Co.',

    'story\\s*book soap\\s*works': 'Storybook Soapworks',
    'story\\s*book soap\\s*works\\s*[&/]\\s*ap\\s*r(?:eserve|\\b)(.*)': 'Storybook Soapworks',

    '(?:the|)\\s*sudsy soapery': 'The Sudsy Soapery',

    'summer break\\s*(?:soap\w+|)': 'Summer Break Soaps',

    'talbot\\s*(?:shaving|)': 'Talbot Shaving',

    'tallow' + _any_and + 'steel': 'Tallow + Steel',

    'taylor of old bond st\S*': 'Taylor of Old Bond Street',
    'tobs\\b': 'Taylor of Old Bond Street',

    'tcheon fung sing': 'Tcheon Fung Sing',

    'valobra\\b': 'Valobra',

    'viking(?: soap|)\\b': 'Viking Soap & Cosmetic',

    'vito' + _apostophe + 's': 'Vitos',

    'west coast shaving': 'West Coast Shaving',

    'west of olympia': 'West of Olympia',

    'wholly kaw': 'Wholly Kaw',

    'wickham(?: soap co.?|)': 'Wickham Soap Co.',

    'william' + _apostophe + 's\\s(?:mug soap|)': 'William\'s Mug Soap',

    'zingari\\s*(?:mann?|)': 'Zingari Man',
    'zingari\\s*(?:man|)\\s*[/x×]\\s*b\\s*(?:&(?:amp;|)|\\+|a)\\s*m': 'Zingari Man',
    'b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\s*[/x×]\\s*zingari\\s*(?:man|)': 'Zingari Man',

    # other
    'homemade\\s+[a-z\\s\\(\\)]*?soap': '(homemade)',
    'mug of many samples': 'Mug of many samples',

    # things that aren't really "lather," but for some reason got used anyway
    'k[ae]rosene\\.*': 'kerosene',

    # abbreviations
    'aos\\b': 'Art of Shaving',
    'apr\\b': 'Australian Private Reserve',
    'b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\b': 'Barrister and Mann',
    'dg\\b(?:/CL|)': 'Declaration Grooming',
    'hssc': 'Highland Springs Soap Company',
    'lassco': 'Los Angeles Shaving Soap Company',
    'mls\\b': 'Mickey Lee Soapworks',
    'n\\.?\\s*o\\.?\\s+(.*)': 'Noble Otter',
    'paa\\b': 'Phoenix Artisan Accoutrements',
    'sv\\b': 'Saponificio Varesino',
    'a' + _any_and + 'e': 'Ariana & Evans',
    'sw\\b': 'Southern Witchcrafts',
    'sbsw\\b': 'Storybook Soapworks',
    'sbs\\b': 'Summer Break Soaps',
    't' + _any_and + 's\\b': 'Tallow + Steel',
    'tfs\\b': 'Tcheon Fung Sing',
    'wcs\\b': 'West Coast Shaving',
    'wk\\b': 'Wholly Kaw',

    # other random patterns to try
    # someone once misabbreviated DG as DA
    # TODO this might be better done from scent-first matching
    'da\\b': 'Declaration Grooming',
}

_compiled_pats = None

def _compile():
    global _compiled_pats
    if _compiled_pats is None:
        _compiled_pats = { }
        for pattern in _maker_pats:
            _compiled_pats[re.compile(pattern + _ending, re.IGNORECASE)] = _maker_pats[pattern]


def matchMaker( str ):
    """ When a maker is successfully matched, a dict is returned with these elements:
            'match': the result object from re.match()
            'name': the standard maker name
        Otherwise, None is returned.
    """
    _compile()
    for pattern in _compiled_pats:
        result = pattern.match(str)
        if result:
            return { 'match': result, 'name': _compiled_pats[pattern] }
    return None
