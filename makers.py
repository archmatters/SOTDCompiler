#!/usr/bin/env python3

import re

_apostophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'
_opt_company = '\\s*(?:company|co\\.?|)\\s*'

_maker_pats = {
    # known soapmakers
    'abbate y la mantia': 'Abbate y la Mantia',

    'acqua di parma': 'Acqua di Parma',

    'apex alchemy\\s*(?:soaps?|)': 'Apex Alchemy Soaps',

    'ariana' + _any_and + 'evans\\s*/?\\s*the club': 'Ariana & Evans',
    'ariana' + _any_and + 'evans': 'Ariana & Evans',

    'arko\\b': 'Arko',

    'archaic alchemy': 'Archaic Alchemy',

    'arran\\b': 'Arran',

    '(?:australian private|ap)\\s*(?:reserve|r\\b)\\s*[&/]\\s*story\\s*book soap\\s*works': 'Storybook Soapworks',
    '(?:australian private|ap)\\s*(?:reserve|r\\b)\\s*/\\s*noble otter': 'Noble Otter',
    '(?:australian private|ap)\\s*(?:reserve|r\\b)\\s*[&/]\\s*Southern Witchcrafts': 'Southern Witchcrafts',
    '(?:australian private|ap) reserve': 'Australian Private Reserve',

    'barbasol': 'Barbasol',

    'barbus\\b': 'Barbus',

    'barrister' + _any_and + 'mann\\s*[/x×]\\s*zingari': 'Zingari Man',
    'barrister' + _any_and + 'mann?': 'Barrister and Mann',

    'black ship\\s(?:grooming\\s*(?:co\\.?|)|)': 'Black Ship Grooming Co.',

    'the body shop': 'The Body Shop',

    'bufflehead': 'Bufflehead',

    'c\\.?\\s*o\\.?\\s*bigelow': 'C.O. Bigelow',

    'captain' + _apostophe + 's choice': 'Captain\'s Choice',

    'castle forbes': 'Castle Forbes',

    'catie' + _apostophe + 's bubbles': 'Catie\'s Bubbles',
    'sfws\\s*/\\s*catie' + _apostophe + 's bubbles': 'Catie\'s Bubbles',
    'Carnavis ' + _any_and + 'Richardson\\s*/\\s*Catie' + _apostophe + 's Bubbles': 'Catie\'s Bubbles',
    'cbl soaps': 'CBL Soaps',

    'cella': 'Cella',

    'central texas (?:soaps?|)': 'Central Texas Soaps',

    'oleo\\s*(?:soap|soapworks|)': 'Chicago Grooming Co.',
    'chicago groom\\w+' + _opt_company + '(?:\(formerly[^)]+\)|)': 'Chicago Grooming Co.',

    'chiseled face': 'Chiseled Face',
    'zoologist(?: perfumes|)\\s*/\\s*chiseled face': 'Chiseled Face',
    'chiseled face\\s*/\\s*zoologist(?: perfumes|)': 'Chiseled Face',

    'cold river\\s*(?:soap\\s*works)': 'Cold River Soap Works',

    '(?:col(?:onel|\\.|)\\s*|)conk': 'Col. Conk',

    'cooper' + _any_and + 'french': 'Cooper & French',

    'crabtree' + _any_and + 'evelyn': 'Crabtree & Evelyn',

    'cremo': 'Cremo',

    'd\\.?\\s*r\\.?\\s*harris': 'D.R. Harris',

    'd(?:ai|ia)sho\\s*(?:shaving(?:products|)|soaps?|)': 'Daisho Shaving Products',

    'dindi naturals': 'Dindi Naturals',

    'Declaration Grooming/Chatillon Lux': 'Declaration Grooming',
    'Declaration Grooming/Maggard Razors': 'Declaration Grooming',
    'Chatillon Lux/Declaration Grooming': 'Declaration Grooming',
    'l' + _any_and + 'l grooming': 'Declaration Grooming',

    'dr.? joh?n' + _apostophe + 's': 'Dr. Jon\'s',

    'edwin jagg[ea]r': 'Edwin Jagger',

    'eleven': 'Eleven Shaving',

    'esbjerg': 'Esbjerg',

    'ethos': 'ETHOS',

    'eufros': 'Eufros',

    'executive shaving': 'Executive Shaving',

    'fenom[ei]no\\s*(?:shave|)': 'Fenomeno Shave',

    'fine accoutrements': 'Fine Accoutrements',

    'first canadian\\s*(?:shave soap' + _opt_company + '|)': 'First Canadian Shave Soap Co.',

    'floris\\s*(?:(?:of|)\\s*london|)': 'Floris London',

    'fitjar\\s*(?:islands?|)': 'Fitjar Islands',

    'fuzzy\\s*face(?: soaps|)': 'Fuzzyface Soaps',

    'geo(?:rge|\\.|)\\s*f?\\.? trumper': 'Geo. F. Trumper',

    'gentlem[ae]n' + _apostophe + 's? nod': 'Gentleman\'s Nod',

    'gillette': 'Gillette',

    '(?:the|)\\s*goodfella' + _apostophe + 's' + _apostophe + '\\s*(?:smile|)': 'The Goodfellas\' Smile',

    'grooming dep[at]\\S*': 'Grooming Department',

    'haslinger': 'Haslinger',

    'henri et victoria': 'Henri et Victoria',

    'henri et victoria': 'Henri et Victoria',

    'heritage hill(?: shave' + _opt_company + '|)': 'Heritage Hill Shave Company',

    'highland springs? soap' + _opt_company: 'Highland Springs Soap Company',
    'highland springs?': 'Highland Springs Soap Company',

    'hub city\\s*(?:soap' + _opt_company + '|)': 'Hub City Soap Company',

    'imperial\\s*(?:barber (?:products|grade products?|)|)': 'Imperial Barber',

    'klar(?: seifen?| soap|\\b)': 'Klar Seifen',

    'l' + _apostophe + 'occitane': 'L\'Occitane',

    'la toja': 'La Toja',
    
    'like grandpa': 'Like Grandpa',

    'long rifle(?:soaps?' + _opt_company + '|)': 'Long Rifle Soap Company',
    
    '(?:los angeles|la) shaving soap' + _opt_company: 'Los Angeles Shaving Soap Co.',
    
    'maol\\s*(?:grooming|)': 'Maol Grooming',

    'mama bear': 'Mama Bear',

    'mammoth\\s*(?:soaps?|)' + _any_and + 'ap(?:\\s*reserve|r\\b)': 'Mammoth Soaps',
    'mammoth\\s*(?:soaps?|)': 'Mammoth Soaps',

    'martin de candre': 'Martin de Candre',

    'mei(?:ß|ss)ner tremonia': 'Meißner Tremonia',

    'micke?y lee soap\w+': 'Mickey Lee Soapworks',

    'mike' + _apostophe + 's natural(?: soaps?|)': 'Mike\'s Natural Soaps',

    'mitchell' + _apostophe + 's\\s*(?:wool fat|)': 'Mitchell\'s Wool Fat',

    'moon soaps?': 'Moon Soaps',

    'murphy' + _any_and + 'mcneil': 'Murphy and McNeil',

    'mystic water\\s*(?:soaps?|)': 'Mystic Water Soap',

    'noble otter': 'Noble Otter',
    'apr\\s*/\\s*no': 'Noble Otter',
    'no\\s*/\\s*apr': 'Noble Otter',

    'nordic shaving' + _opt_company: 'Nordic Shaving Company',

    'oaken lab': 'Oaken Lab',

    'obsessive soap(?:s|\\s+perfect\w+|)': 'Obsessive Soap Perfectionist',
    'osp(?:\\s*soaps?|\\b)': 'Obsessive Soap Perfectionist',

    'ogalalla': 'Ogalalla',

    'old spice': 'Old Spice',

    'oz shaving': 'Oz Shaving',

    'palmolive': 'Palmolive',

    'panna\\s*crema': 'PannaCrema',

    'paragon shaving': 'Paragon Shaving',

    'ph[oe]+nix' + _any_and + 'beau': 'Phoenix and Beau',

    'pr[éeè] de provence': 'Pré de Provence',

    'pro(?:raso|saro)': 'Proraso',

    'pinnacle grooming': 'Pinnacle Grooming',

    'razor emporium': 'Razor Emporium',

    'red house farms': 'Red House Farms',
    '(?:u/|)grindermonk' + _apostophe + 's?': 'Red House Farms',

    'reef point\\s*(?:soaps?)': 'Reef Point Soaps',

    'saponificio\\s*varesino': 'Saponificio Varesino',

    'seaforth!?': 'Seaforth!',

    'shannon' + _apostophe + 's soaps': 'Shannon\'s Soaps',

    's\\s*h\\s*a\\s*v\\s*e.{0,4}d\\s*a\\s*n\\s*d\\s*y': 'SHAVE DANDY',

    'siliski soaps': 'Siliski Soaps',
    'siliski': 'Siliski Soaps',

    'soap commander': 'Soap Commander',

    'some irish guy' + _apostophe + 's': 'Some Irish Guy\'s',

    'southern witchcrafts?': 'Southern Witchcrafts',
    'southern witchcrafts\\s*/\\s*apr\\b': 'Southern Witchcrafts',

    'spearhead\\s*(?:(?:shaving|soap)' + _opt_company + '|)': 'Spearhead Shaving Company',

    'sp[ei]{2}c?k': 'Speick',

    'st[ei]rl[ei]ng\s*(?:soap' + _opt_company + '|)(.*)': 'Stirling Soap Co.',

    'story\\s*book soap\\s*works\\s*[&/]\\s*ap\\s*r(?:eserve|\\b)(.*)': 'Storybook Soapworks',
    'story\\s*book soap\\s*works': 'Storybook Soapworks',

    '(?:the|)\\s*sudsy soap[ae]ry\\s*[/&]\\s*chatillon lux': 'The Sudsy Soapery',
    '(?:the|)\\s*sudsy soap[ae]ry': 'The Sudsy Soapery',

    'talbot\\s*(?:shaving|)': 'Talbot Shaving',

    'tabac\\b': 'Tabac',

    'tallow' + _any_and + 'steel': 'Tallow + Steel',

    'taylor of old bond st\S*': 'Taylor of Old Bond Street',
    'tobs\\b': 'Taylor of Old Bond Street',

    'tcheon fung sing': 'Tcheon Fung Sing',

    'the club\\b(?:/a&e|)': 'Ariana & Evans',
    'a&e[ /]the club': 'Ariana & Evans',

    'through the fire fine craft': 'Through the Fire Fine Craft',

    'uncle jon' + _apostophe + 's': 'Uncle Jon\'s',

    'valobra\\b': 'Valobra',

    'viking(?: soap|)\\b': 'Viking Soap & Cosmetic',

    'vito' + _apostophe + 's': 'Vitos',

    'west coast shaving' + _any_and + 'oleo': 'West Coast Shaving',

    'west of olympia': 'West of Olympia',

    'wholly kaw': 'Wholly Kaw',

    'wickham(?: soap co.?|)': 'Wickham Soap Co.',

    'william' + _apostophe + 's\\s(?:mug soap|)': 'William\'s Mug Soap',

    'zingari\\s*(?:man|)\\s*[/x×]\\s*b\\s*(?:&(?:amp;|)|\\+|a)\\s*m': 'Zingari Man',
    'b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\s*[/x×]\\s*zingari\\s*(?:man|)': 'Zingari Man',
    'zingari\\s*(?:mann?|)': 'Zingari Man',

    # also make hardware
    '(?:the |)art of shaving': 'Art of Shaving',
    'declaration\\s*(?:grooming|)': 'Declaration Grooming',
    'maggard\\s*(?:razors?|)': 'Maggard Razors',
    'maggard' + _apostophe: 'Maggard Razors',
    'm[üu]hle': 'Mühle',
    'phoenix artisan accoutrements': 'Phoenix Artisan Accoutrements',
    'phoenix shaving': 'Phoenix Artisan Accoutrements',
    'razorock': 'RazoRock',
    'summer break\\s*(?:soap\w+|)': 'Summer Break Soaps',
    'west coast shaving': 'West Coast Shaving',
    'wild west shaving' + _opt_company: 'Wild West Shaving Co.',

    # other
    'homemade\\s+[a-z\\s\\(\\)]*?soap\\.?': '(homemade)',
    'mug of many samples': 'Mug of many samples',

    # things that aren't really "lather," but for some reason got used anyway
    'k[ae]rosene\\.*': 'kerosene',

    # abbreviations or more common words
    'apr\\b': 'Australian Private Reserve',
    'b\\s*(?:&(?:amp;|)|\\+|a|)\\s*m\\b': 'Barrister and Mann',
    'cb\\b': 'Catie\'s Bubbles',
    'cbl\\b': 'CBL Soaps',
    'cf\\b': 'Chiseled Face',
    'crsw\\b': 'Cold River Soap Works',
    'l' + _any_and + 'l': 'Declaration Grooming',
    'hssc': 'Highland Springs Soap Company',
    'lassco': 'Los Angeles Shaving Soap Company',
    'mls\\b': 'Mickey Lee Soapworks',
    'pdp\\b': 'Pré de Provence',
    'sv\\b': 'Saponificio Varesino',
    'a' + _any_and + 'e': 'Ariana & Evans',
    'sw\\b': 'Southern Witchcrafts',
    'sbsw\\b': 'Storybook Soapworks',
    'sbs\\b': 'Summer Break Soaps',
    't' + _any_and + 's\\b': 'Tallow + Steel',
    'tfs\\b': 'Tcheon Fung Sing',
    'ttffc\\b': 'Through the Fire Fine Craft',
    'wcs\\b': 'West Coast Shaving',
    'wk\\b': 'Wholly Kaw',
    # hardware vendors
    'aos\\b': 'Art of Shaving',
    'dg\\b(?:/CL|)': 'Declaration Grooming',
    'fine\\b': 'Fine Accoutrements',
    'n\\.?\\s*o\\.?\\s+(.*)': 'Noble Otter',
    'paa\\b': 'Phoenix Artisan Accoutrements',
    'wwsc\\b': 'Wild West Shaving Co.',

    # other random patterns to try
    # someone once misabbreviated DG as DA
    # TODO this might be better done from scent-first matching
    'da\\b': 'Declaration Grooming',
}

# TODO special category for more complicated patterns,
# e.g. 'wms\\s*[_\*]*\\s*$' for William's (single scent makes misidentification more likely)

_ending = '\\s*(.*)'
_compiled_pats = None

def _compile():
    global _compiled_pats
    if _compiled_pats is None:
        _compiled_pats = { }
        for pattern in _maker_pats:
            _compiled_pats[re.compile(pattern + _ending, re.IGNORECASE)] = _maker_pats[pattern]


def matchMaker( text ):
    """ When a maker is successfully matched, a dict is returned with these elements:
            'match': the result object from Pattern.match()
            'name': the standard maker name
        Otherwise, None is returned.
    """
    _compile()
    for pattern in _compiled_pats:
        result = pattern.match(text)
        if result:
            return { 'match': result, 'name': _compiled_pats[pattern] }
    return None


def searchMaker( text ):
    """ Searches for a maker through the entire provided text. Will preferably
        return a match at the beginning of a line (less non-alphanumeric
        chars). But will also return a match in the middle of a line. Returns
        a dict with these attributes:
            'match': the result object from Pattern.match()
            'name': the standard maker name
            'first': boolean value indicating if the match is the first word on a line
            'abbreviated': boolean value indicating an abbreviation match
    """
    # TODO recognize abbreviations
    # TODO if we match a hardware vendor, keep looking for a soapmaker
    # TODO we have a real problem with Noble Otter matching sentences which start with "No"
    # this might also be a problem with other two or three letter abbreviations
    _compile()
    best_match = None
    for pattern in _compiled_pats:
        result = pattern.search(text)
        if result:
            begin_line = False
            nlpos = text.rfind("\n", 0, result.start())
            if result.start() == 0 or nlpos == result.start() - 1:
                begin_line = True
            else:
                not_word = True
                for i in range(nlpos + 1, result.start()):
                    if str.isalpha(text[i]) or str.isdigit(text[i]):
                        not_word = False
                        break
                if not_word:
                    begin_line = True
            if begin_line:
                return {
                    'match': result,
                    'name': _compiled_pats[pattern],
                    'first': True,
                    'abbreviated': False
                }
            best_match = result
    if best_match:
        return {
            'match': best_match,
            'name': _compiled_pats[best_match.re],
            'first': False,
            'abbreviated': False
        }
    return None

