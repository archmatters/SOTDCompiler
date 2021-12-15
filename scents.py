#!/usr/bin/env python3

import re

_simple_cream_soap_pat = re.compile('^(?:shav(?:ing|e) |)(?:soap|cream)$')
_any_pattern = re.compile('.*')

_apostrophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+|)\\s*'
_prefix = '\\b'
_suffix = '\\b[\\.,]?'
# same as in scanner; need to deduplicate
_separator_pattern = re.compile('\\s*(?:\\\\?-+|–|:|,|\\.|\\|)\\s*')

_fougere = 'foug[èeé]re'
_sandalwood = 'sand(?:al|le)wood'

_unique_names = { }
_compiled_pats = None

def _default_custom( map ):
    return map

class Sniffer:
    """ A class to handle scent matching.

    + `default_scent`: if this maker has a 'default' scent, this is its name.
    + `lowpatterns`: low confidence patterns, only used after maker is known.
    + `patterns`: high confidence patterns, used whether or not maker is known.
    + `bases`: base names not part of scent name.
    + `custom`: function for custom work after a successful match.
    """

    def __init__( self, *, default_scent: str = None,
            lowpatterns: dict = None, patterns: dict = None,
            bases: list = None, custom = None ):
        # TODO this is set in _compile_all(), so we can just use the map key
        self.makername = None
        self.lowpatterns = { }
        self.highpatterns = { }
        self.bases = [ ]
        self.namecount = 0
        if default_scent:
            self.default_scent = default_scent
        else:
            self.default_scent = None
        if custom:
            self.custom = custom
        else:
            self.custom = _default_custom
        self._compile(lowpatterns, patterns, bases)


    def _compile( self, lowpatterns: dict, highpatterns: dict, bases: list ):
        allnames = [ ]
        if lowpatterns:
            for pat in lowpatterns:
                self.lowpatterns[re.compile(_prefix + pat + _suffix,
                        re.IGNORECASE)] = lowpatterns[pat]
                if lowpatterns[pat] not in allnames:
                    allnames.append(lowpatterns[pat])
        if highpatterns:
            for pat in highpatterns:
                finalpat = pat
                if pat[0] != '^':
                    finalpat = _prefix + finalpat
                if pat[-1] != '$':
                    finalpat = finalpat + _suffix
                self.highpatterns[re.compile(finalpat, re.IGNORECASE)] = highpatterns[pat]
                if highpatterns[pat] not in allnames:
                    allnames.append(highpatterns[pat])
        self.namecount = len(allnames)
        if self.namecount == 0 and self.default_scent:
            self.namecount = 1
        global _unique_names
        for name in allnames:
            if name not in _unique_names:
                _unique_names[name] = 1
            else:
                _unique_names[name] += 1
        if bases:
            for name in bases:
                bpat = '\\b' + name + '(?:\\s+(?:base|formula)\\b|\\b)'
                self.bases.append(re.compile(
                        '\\s*(?:\\(' + bpat + '\\)|(?:\\bin |[:,\\-]\\s*)' + bpat
                                + '|' + bpat + '\\s*[\\-\\:,]?)\\s*',
                        re.IGNORECASE))


    def strip_base( self, text: str ):
        if not self.bases:
            return text
        for pattern in self.bases:
            stripped = None
            pos = 0
            while pos < len(text):
                result = pattern.search(text, pos)
                if result and result.start() == 0:
                    stripped = text[result.end():].strip()
                    break
                elif result and result.end() == len(text):
                    stripped = text[0:result.start()].strip()
                    break
                elif result:
                    pos = result.end()
                else:
                    pos = len(text)
            if stripped or (stripped == '' and self.default_scent):
                result = _separator_pattern.match(stripped)
                if result:
                    stripped = stripped[result.end():].strip()
                return stripped
        return text


    def is_single_scent( self ):
        return self.namecount == 1
    

    def get_default_scent( self ):
        return self.default_scent


    # can use low confidence patterns
    # return "Definitive Scent Name"
    def match_on_maker( self, text: str ):
        text = text.strip()
        if not text and self.default_scent:
            result = _any_pattern.match(text)
            return {
                    'match': result,
                    'maker': self.makername,
                    'scent': self.get_default_scent(),
                    'lather': None,
                    'search': False
                }

        for pattern in self.highpatterns:
            result = pattern.match(text)
            if not result:
                result = pattern.search(text)
            if result:
                return {
                        'match': result,
                        'maker': self.makername,
                        'scent': self.highpatterns[pattern],
                        'lather': None,
                        'search': False
                    }
                
        for pattern in self.lowpatterns:
            result = pattern.match(text)
            if result:
                return {
                        'match': result,
                        'maker': self.makername,
                        'scent': self.lowpatterns[pattern],
                        'lather': None,
                        'search': False
                    }
        for pattern in self.lowpatterns:
            result = pattern.search(text)
            if result:
                return {
                        'match': result,
                        'maker': self.makername,
                        'scent': self.lowpatterns[pattern],
                        'lather': None,
                        'search': False
                    }
                
        return None
    

    # will not use low confidence patterns
    # return { 'maker': 'Maker Name', 'scent': 'Scent Name', 'lather': 'Lather text' }
    def match_unknown( self, full_text: str ):
        return None

# findbase() which accepts a list of patterns?
# caller can then strip, or use as confidence boost (or both, really)
#
# cleanandmatch... needs to be moved in here, I think
#
# not sure we need 'aggressive' patterns, but we do need a default indicator,
# e.g. default for Barbasol is Classic; default for Cella is Crema Sapone
#

# low-confidence patterns (not good for body matching)
# high-confidence patterns (better for body matching)
#    this could be automated?  one word = very low, two = low, three+ = higher
#    this would be words MATCHED, not words in scent
# base names, must match before or after scent, maybe parenthesized
#    only stripped if we know maker before identifying scent
# custom post-match code (e.g. need to change maker based on identified scent)
#    custom code needs to know if this is a body match or not

def custom_apr( map ):
    if map['maker'] == 'Australian Private Reserve':
        if map['scent'] == 'Carnivale' or map['scent'] == 'Fresca Intensa':
            map['maker'] = 'Storybook Soapworks'
    return map

def custom_chatillon_lux( map ):
    if map['maker'] == 'Chatillon Lux':
        so = _compiled_pats['Declaration Grooming']
        result = so.match_on_maker(map['scent'])
        if result:
            return result
    raise Exception('Chatillon Lux is NOT a soapmaker!')

def custom_summer_break( map ):
    if map['scent'] == 'Mountain Laurel':
        map['maker'] = 'London Razors'
    return map

def custom_chicago_groom( map ):
    if map['scent'] == 'Pear-Brrr Shoppe':
        map['maker'] = 'West Coast Shaving'
    if map['scent'] == 'Timeless Razor':
        map['maker'] = 'Timeless Razor'
    return map

def custom_ariana_evans( map ):
    if map['scent'] == 'Passiflora':
        map['maker'] = 'Barrister and Mann'
    return map

def custom_mammoth( map ):
    if map['scent'] == 'Cerberus':
        map['maker'] = 'Declaration Grooming'
    return map

def custom_noble_otter( map ):
    if map['scent'] == '63':
        map['maker'] = 'Pré de Provence'
        map['scent'] = 'No. 63'
    if map['scent'] == '1':
        map['maker'] = 'Zingari Man'
        map['scent'] = 'No. 1'
    return map


_scent_pats = {
    'Abbate y la Mantia': Sniffer(
        lowpatterns={
            'krokos': 'Krokos',
            'crumiro': 'Crumiro',
            'matteo': 'Matteo 9,11',
            'garibaldi': 'Garibaldi',
            'monet': 'Monet',
            'buttero': 'Buttero',
            'don jos[èe]': 'Don Josè',
        }
    ),

    'Acca Kappa': Sniffer(
        patterns={
            'muschio bianc[oa]': 'Muschio Bianco',
            'white moss': 'Muschio Bianco',
        }
    ),

    'Ach Brito': Sniffer(
        patterns={
            'lavanda': 'Lavanda',
            'mogno': 'Mogno',
        },
    ),

    'Acqua di Parma': Sniffer(
        patterns={
            'barbiere crema soffice (?:da pen+el+o|)': 'Barbiere',
            'Collezione Barbiere': 'Barbiere',
        },
        lowpatterns={
            'barbiere': 'Barbiere',
            'colonia': 'Barbiere',
        },
        default_scent='Barbiere'
    ),

    'Alphy & Becs': Sniffer(
        lowpatterns={
            'fresh cotton': 'Fresh Cotton',
            'sandalwood': 'Sandalwood',
        }
    ),

    'Apex Alchemy Soaps': Sniffer(
        patterns={
            'nostalgic nightcrawler': 'Nostalgic Nightcrawler',
            '(?:american|ameriacan) pi': 'American Pi',
            'alchemical romance': 'Alchemical Romance',
            'love' + _any_and + 'other drugs': 'Love and Other Drugs',
            'gr[ēe]n river': 'Grēn River',
        },
        lowpatterns={
            'nightcrawler': 'Nostalgic Nightcrawler',
            'gr[ēe]+n river': 'Grēn River',
        }
    ),

    'Archaic Alchemy': Sniffer(
        lowpatterns={
            'agave': 'Agave',
            'mictlan': 'Mictlan',
            'archaic': 'Archaic',
        }
    ),

    'Ariana & Evans': Sniffer(
        patterns={
            'st\\.? bart' + _apostrophe + 's': 'St. Barts',
            'peach(?:es|)' + _any_and + 'cognac': 'Peach & Cognac',
            'peach(?:es|) cognac': 'Peach & Cognac',
            'which one' + _apostrophe + 's pink\\??': 'Which One\'s Pink?',
            'grecian(?: horse|)': 'Grecian Horse',
            '\\(?\\s*little fictions\\s*\\)?(?:' + _any_and + 'gr[ea]y matter|)': 'Little Fictions',
            'vanill[ea] de tabac': 'Vanille de Tabac',
            'asian plum': 'Asian Plum',
            'asian pear': 'Asian Pear',
            'can+ablis+ santal': 'Cannabliss Santal',
            'barbiere sofistic[as]to': 'Barbiere Sofisticato',
            'Sofistacato Barbiere': 'Barbiere Sofisticato',
            'pedro fiasco': 'Pedro Fiasco',
            'l' + _apostrophe + 'orange verte': 'l\'Orange Verte',
            'skin essentials +-? *shav(?:ing|e) butter': 'Shaving Butter',
            # The Club brand
            'charlatan' + _apostrophe + 's traipse': 'Charlatans Traipse',
            'warrior of (?:the |)howling fjord': 'Warrior of Howling Fjord',
            'fruits? de la passione?': 'Fruit de la Passion',
            'vanill[ea] vendetta': 'Vanille Vendetta',
            'club bac+ar+a': 'Club Baccara',
            'vacan[zc]a romana?': 'Vacanza Romana',
            'low[\\- ]*scent skeletor': 'Low-Scent Skeletor',
            'tibetan temple': 'Tibetan Temple',
        },
        lowpatterns={
            'spartacus': 'Spartacus',
            'socal hipster': 'SoCal Hipster',
            'shav(?:ing|e) butter': 'Shaving Butter',
            'chasing the dragon': 'Chasing the Dragon',
            'strawberry fields': 'Strawberry Fields',
            'forb+id+en fruit': 'Forbidden Fruit',
            '(?:the |)dirty ginger': 'Dirty Ginger',
            # The Club brand
            'the kingdom': 'The Kingdom',
            'el gaucho': 'El Gaucho',
            'howling fjord': 'Warrior of Howling Fjord',
            'bac+ar+a': 'Club Baccara',
            'bl[av]ck': 'Black', # with an upside-down capital A, hence the interpretation of V
            'cafe au lait': 'Cafe au Lait',
            'the city(?: \\(?never sleeps\\)?|)': 'The City (Never Sleeps)',
        },
        bases=[ 'kaizen', 'k2', 'vegan' ],
        custom=custom_ariana_evans
    ),

    'Arko': Sniffer(
        lowpatterns={
            '(?:shave |)stick': 'Arko',
        },
        default_scent='Arko'
    ),

    'Art of Shaving': Sniffer(
        lowpatterns={
            'sandalwood': 'Sandalwood',
            'unscented': 'Unscented',
            'black pepper' + _any_and + 'lime': 'Black Pepper & Lime',
        }
    ),

    'Australian Private Reserve': Sniffer(
        patterns={
            'raconteur': 'Raconteur',
            'foug[èeé]re trois': 'Fougère Trois',
            'la\\s*violet+a': 'Lavioletta',
            'fenchurch': 'Fenchurch',
            'ozymandias': 'Ozymandias',
        },
        lowpatterns={
            'carnivale?': 'Carnivale', # actually Storybook Soapworks
            'fresca intensa': 'Fresca Intensa', # actually Storybook Soapworks
        },
        custom=custom_apr
    ),

    'Aveeno': Sniffer(
        patterns={
            'positively smooth (?:shave |)gel': 'Positively Smooth',
            'ther[ae]pe?utic (?:shave |)gel': 'Therapeutic',
        },
    ),

    'Barbasol': Sniffer(
        patterns={
            'pacific rush': 'Pacific Rush',
        },
        lowpatterns={
            'original': 'Original',
            'sensitive': 'Sensitive Skin',
            'soothing aloe\\b': 'Soothing Aloe',
            'extra moisturizing': 'Extra Moisturizing',
            '(?:100th anniversary|1919)': '100th Anniversary',
        },
        default_scent='Original'
    ),

    'Barbus': Sniffer(
        lowpatterns={
            'classic': 'Classic',
            'active': 'Active',
        },
        default_scent='Classic'
    ),

    'Barrister and Mann': Sniffer(
        patterns={
            'seville': 'Seville',
            '(?:eigen|ein)grau': 'Eigengrau',
            '[\\w\\s]*grande? chypre.*': 'Le Grand Chypre',
            'dickens,?\\s+revisited': 'Dickens, Revisited',
            'oh?' + _apostrophe + ',?\\s*delight': 'O, Delight!',
            'brew?(?:-| |)ha[\\- ]?ha': 'Brew Ha-Ha',
            'hallows?': 'Hallows',
            'pag[ai]?nini' + _apostrophe + 's violin': 'Paganini\'s Violin',
            'levia?n?than': 'Leviathan',
            'beaudelaire': 'Beaudelaire',
            'foug[èeé]re gothi\w+': 'Fougère Gothique',
            'foug[èeé]re angel\w+': 'Fougère Angelique',
            'behold the whatsis!?': 'Behold the Whatsis!',
            'dfs (?:2017|exclusive)': 'DFS 2017 LE',
            'le grand (?:cyphre|chyph?re)': 'Le Grand Chypre',
            '(?:motherfuckin(?:\'|g)|mf) roam': 'Roam',
            'lavanille': 'Lavanille',
            'first snow': 'First Snow',
            '(?:cologne|colonge|colnge) russe': 'Cologne Russe',
            '(?:the |the full |)measure of (?:a |)man+': 'The Full Measure of Man',
            'fi+garose': 'Figarose',
            # club release
            'passiflora': 'Passiflora',
            # latha
            'osmanthus': 'Osmanthus',
            'latha taiga': 'Taiga',
            'latha original': 'Latha Original', # specifically identify "Latha Original" as "Latha"
            'fmom': 'The Full Measure of Man',
            'm[éeè]lange': 'Mélange',
        },
        lowpatterns={
            # reserve
            'waves': 'Reserve Waves',
            'spice': 'Reserve Spice',
            'fern': 'Reserve Fern',
            'lavender': 'Reserve Lavender',
            'cool': 'Reserve Cool',
            'classic': 'Reserve Classic',
            'taiga': 'Taiga',
            'paganini': 'Paganini\'s Violin',
            'lgc': 'Le Grand Chypre',
        },
        bases=[ 'latha', 'soft heart series', 'soft(?:ish|)(?:-|\\s*)hearts?', 'SH',
                'excelsior', 'glissant', 'reserve', 'pp8', 'omnibus' ]
    ),

    'Bartigan & Stark': Sniffer(
        lowpatterns={
            'ch?ampione': 'Campione',
        }
    ),

    'BAUME.BE': Sniffer(
        lowpatterns={
            '(?:shaving |)soap': 'BAUME.BE',
            '(?:shaving |)cream': 'BAUME.BE'
        },
        default_scent='BAUME.BE'
    ),

    'Bearskin & Tunic': Sniffer(
        patterns={
            'lock lomond': 'Loch Lomond',
            'tarifa': 'Tarifa',
        },
        lowpatterns={
            'rjm': 'RJM',
        }
    ),
    
    'Black Ship Grooming Co.': Sniffer(
        patterns={
            'calypso' + _apostrophe + 's curse': 'Calypso\'s Curse',
            'cap *' + _apostrophe + 'n dark *side': 'Cap\'n Darkside',
            '(?:7|seven) doubloons': '7 Doubloons',
        },
        lowpatterns={
            'calypso' + _apostrophe + 's?': 'Calypso\'s Curse',
            'captain' + _apostrophe + 's choice': 'Captain\'s Choice',
            'captain' + _apostrophe + 's reserve': 'Captain\'s Reserve',
            'l[ae] concorde?': 'La Concorde',
            'siren' + _apostrophe + 's? song': 'Siren\'s Song',
            'grace o' + _apostrophe + 'malle?y': 'Grace O\'Malley',
            '(?:the |)black rose': 'The Black Rose',
            'peg leg (?:nichols|nickels)': 'Peg Leg Nichols',
        }
    ),

    'The Bluebeards Revenge': Sniffer(
        default_scent='Shaving Cream',
    ),

    'The Body Shop': Sniffer(
        lowpatterns={
            'maca root' + _any_and + 'aloe': 'Maca Root & Aloe',
        }
    ),

    'Boellis': Sniffer(
        patterns={
            'panama 1924': 'Panama 1924',
        }
    ),

    'Boots': Sniffer(
        lowpatterns={
            'freshwood': 'Freshwood',
            'original': 'Original',
        }
    ),

    'Brutalt Bra Barbersåpe': Sniffer(
        patterns={
            'tsn le\\s*/\\s*norwegian wood': 'Norwegian Wood',
        },
        lowpatterns={
            'original': 'Original',
            'spruce': 'Norwegian Spruce',
            'lavender/rosemary': 'Lavender/Rosemary',
        }
    ),

    'Bufflehead': Sniffer(
        patterns={
            'Islamorada': 'Islamorada',
            'Mannish Boy': 'Mannish Boy',
            'Elephant Walk': 'Elephant Walk',
            'Herbie Hancock': 'Herbie Hancock',
        },
        lowpatterns={
            'North York': 'North York',
        }
    ),

    'The Butterfly Garden': Sniffer(
        lowpatterns={
            'barber\\s*shop': 'Barber Shop',
        }
    ),

    'Bundubeard': Sniffer(
        patterns={
            'rose en bos': 'Rose en Bos',
            'rolling rooibos': 'Rolling Rooibos',
        },
        lowpatterns={
            'original': 'Original',
        }
    ),

    'Bvlgari': Sniffer(
        lowpatterns={
            'man in black': 'Man in Black',
        }
    ),

    'C.O. Bigelow': Sniffer(
        default_scent='Premium'
    ),

    'Castle Forbes': Sniffer(
        lowpatterns={
            'cedarwood' + _any_and + 'sandalwood': 'Cedarwood & Sandalwood',
        }
    ),

    'Catie\'s Bubbles': Sniffer(
        patterns={
            'mile high menthol': 'Mile High Menthol',
            'porch drinks': 'Porch Drinks',
            'a midnight dreary': 'A Midnight Dreary',
            'pine barrens': 'Pine Barrens',
            'un jour gris': 'Un Jour Gris',
            'tonsorial parlour': 'Tonsorial Parlour',
            'le march[éeè] du ras+age': 'Le Marché du Rasage',
            'm[éeè]nage (?:à|a|á|de) lav[ae]nder?': 'Ménage à Lavande',
            'Blug[èeé]re': 'Blugère',
            'vintage (?:for |)(?:serf|s\\.e\\.r\\.f\\.)': 'Vintage S.E.R.F.',
            'dirty prose': 'Dirty Prose',
        },
        lowpatterns={
            'cool' + _any_and + 'fresh': 'Cool and Fresh',
            'June 2019 Maggard' + _apostrophe + 's? Meetup': 'Maggard Razors 2019 Meetup',
            'Maggard Meet(?:up|) 2019': 'Maggard Razors 2019 Meetup',
            'Maggard Razors 2019 Meetup': 'Maggard Razors 2019 Meetup',
            'Maggard Meet(?:up|) 2017': 'Maggard Razors 2017 Meetup',
            'Maggard Razors 2017 Meetup': 'Maggard Razors 2017 Meetup',
            'la terr[ea] verte?': 'La Terre Verte',
            'lmr': 'Le Marché du Rasage',
            'gla[cd][ée] herbe?': 'Glacé Herbe',
        },
        bases=[ 'luxury cream soap', 'luxury shaving soap', 'luxury cream' ]
    ),

    'CBL Soaps': Sniffer(
        patterns={
            'lavender' + _any_and + 'leather': 'Lavender & Leather',
            't[ao]bacaveg': 'Tabacaveg',
        },
        lowpatterns={
            'peanut butter': 'Peanut Butter',
            'outlaw': 'Outlaw',
            'grape *soda *\\(chilled\\)': 'Grape Soda', # maybe doesn't matter; u/PhilosphicalZombie may be the only one to have this scent
        },
        bases=[ 'fusion', 'simplicity', 'tonsorial', 'master barber' ]
    ),

    'Cella': Sniffer(
        lowpatterns={
            '(?:cella |)crema sapone': 'Cella',
            '(?:cella |milano |)crema d[ae] barba': 'Cella',
            '(?:aloe vera|green)': 'Bio/Aloe Vera',
            'bio': 'Bio/Aloe Vera',
            'soap': 'Cella',
            '1?kg (?:brick|block)': 'Cella',
            'red': 'Cella',
        },
        default_scent='Cella',
    ),

    'Central Texas Soaps': Sniffer(
        patterns={
            'm[er]\\.? pepper': 'Mr. Pepper',
            'citrus burst': 'Citrus Burst',
            'hill countr?y dew': 'Hill Country Dew',
        },
        lowpatterns={
            'bar?bershop': 'Grandpa\'s Barbershop',
            'saw': 'The Saw',
        }
    ),

    'Chatillon Lux': Sniffer(
        lowpatterns={
            'weinstra(?:ss|ß)e': 'Weinstrasse',
        },
        custom=custom_chatillon_lux
    ),

    'Chicago Grooming Co.': Sniffer(
        patterns={
            'montrose beach': 'Montrose Beach',
            'new city:? back of the yards': 'New City Back of the Yards',
            'roug[eéè]re': 'Rougere',
            'mor[íiì]r so[ñna]+do': 'Morír Soñando',
            'seibo dominican chocolate': 'Seibo Dominican Chocolate',
        },
        lowpatterns={
            'ex?cursion': 'Excursion',
            'no\\. 11': 'No. 11',
            'new city': 'New City Back of the Yards',
            'pear-brr+ shop+e?': 'Pear-Brrr Shoppe',
            'timeless(?: razors?|)': 'Timeless Razor',
            'seibo': 'Seibo Dominican Chocolate',
        },
        bases=[ 'canard' ]
    ),

    'Chiseled Face': Sniffer(
        patterns={
            'ghost\\s*town barber': 'Ghost Town Barber',
            'midnight stag': 'Midnight Stag',
            'cryogen': 'Cryogen',
            '(?:zoologist *|)civet': 'Civet',
            '(?:zoologist *|)panda': 'Panda',
            '(?:zoologist *|)camel': 'Camel',
        },
        lowpatterns={
            'gtb\\b': 'Ghost Town Barber',
            'sherlock': 'Sherlock',
            'cedar' + _any_and + 'spice': 'Cedar & Spice',
            'cedar\\s+spice': 'Cedar & Spice',
            'pine tar': 'Pine Tar',
            'trade\\s*winds': 'Trade Winds',
            'ghost\\s*town': 'Ghost Town Barber',
        }
    ),

    'Classic Edge': Sniffer(
        lowpatterns={
            'aloe vera': 'Aloe Vera',
            'sandalwood': 'Sandalwood',
            'bay rum': 'Bay Rum',
            'charcoal': 'Charcoal',
            '(?:old |)barbershop': 'Old Barbershop',
        }
    ),

    'The Clovelly Soap Co.': Sniffer(
        lowpatterns={
            'sandalwood,? *may chang,? *' + _any_and + 'bay': 'Sandalwood, May Chang & Bay',
            'sandalwood' + _any_and + 'may chang': 'Sandalwood & May Chang',
            'tea tree' + _any_and + 'clay': 'Tea Tree & Clay'
        }
    ),

    'Clubman Pinaud': Sniffer(
        default_scent='Clubman Pinaud'
    ),

    'Cold River Soap Works': Sniffer(
        patterns={
            'madman' + _apostrophe + 's bouquet': 'Madman\'s Bouquet',
            'prato verde': 'Prato Verde',
            'jardin d' + _apostrophe + 'orange': 'Jardin d\'Orange',
            'lav[ae]ndula bl(?:eu|ue)': 'Lavandula Bleu',
            'colonia mediterranea': 'Colonia Mediterranea',
        },
        lowpatterns={
            'barbershop': 'American Barbershop',
        },
        bases=[ 'select', 'glide', 'schapenm[ei]lk', 'olivia' ]
    ),

    'Colgate': Sniffer(
        default_scent='Mug Soap'
    ),

    'Crabtree & Evelyn': Sniffer(
        lowpatterns={
            'nomad': 'Nomad',
            'lime': 'Lime',
        }
    ),

    'Czech & Speake': Sniffer(
        lowpatterns={
            'no\\.? *88': 'No. 88',
            'oxford' + _any_and + 'cambridge': 'Oxford & Cambridge',
        }
    ),

    'Dalan': Sniffer(
        lowpatterns={
            'energetic': 'Energetic',
            'cool': 'Cool',
            'sensitive': 'Sensitive'
        }
    ),

    'Dead Sea Shave': Sniffer(
        lowpatterns={
            'maelstrom': 'Maelstrom',
            'kraken': 'Kraken',
            'tempest': 'Tempest',
        }
    ),

    'Declaration Grooming': Sniffer(
        patterns={
            'cuir et [èeé]pices': 'Cuir et Épices',
            'gratiot league': 'Gratiot League Square',
            'trismegi[sa]tus': 'Trismegistus',
            'massacre of the innocents': 'Massacre of the Innocents',
            'son et lumiere': 'Son et Lumiere',
            '\\? \\(puzzle 2019\\)': '? (Puzzle 2019)',
            '\\? 2019 puzzle': '? (Puzzle 2019)',
            'big soap energy': 'Big Soap Energy',
            'fake yellow lights?': 'Fake Yellow Light',
            'lamplight pen+ance': 'Lamplight Penance',
            'weinstra(?:ss|ß)e': 'Weinstrasse',
            '88 chest?nut st(?:reet|\\.|)': '88 Chestnut Street',
            '(?:fou?rth|4th)' + _any_and + 'pine': 'Fourth and Pine',
            'l[ae] petite? prai?rie': 'La Petite Prairie',
            'sunrise on lasalle': 'Sunrise on LaSalle',
            'tsm foug[èeé]re': 'TSM Fougère',
            'darkfall': 'Darkfall',
            'scrumtrules?cent': 'Scrumtrulescent',
            '(?:cerberus|cerebrus)': 'Cerberus',
            'dirtyver': 'Dirtyver',
        },
        lowpatterns={
            'sellout': 'Sellout',
            'tribute': 'Tribute',
            'opul[ea]nce': 'Opulence',
            'cygnus x-?1': 'Cygnus X-1',
            'hindsight': 'Hindsight',
            'original': 'Original',
            'after the rain': 'After the Rain',
            'yuzu[/ ]rose[/ ]patchouli': 'Yuzu/Rose/Patchouli',
            '(?:yrp|ypr)': 'Yuzu/Rose/Patchouli',
            'y/r/p': 'Yuzu/Rose/Patchouli',
            'moti': 'Massacre of the Innocents',
            'massacre': 'Massacre of the Innocents',
            'b[\\- ?]cubed?': 'Blackberry Blossom Bay',
            '(?:b3|b³)': 'Blackberry Blossom Bay',
            '\\?$': '? (Puzzle 2019)',
            'day\\s*man': 'Dayman',
            'night\\s*man': 'Nightman',
            'bse': 'Big Soap Energy',
            'Champs de Lavande': 'Champs de Lavande',
            'sweet lemon': 'Sweet Lemon',
            'la for[êe]t de liguest': 'La Forêt de Liguest',
        },
        bases=[ 'bison', 'milksteak', 'icarus' ]
    ),

    'Dindi Naturals': Sniffer(
        default_scent='lemon myrtle, macadamia + white cypress'
    ),

    'Dr. Jon\'s': Sniffer(
        patterns={
            'flowers in the dark': 'Flowers in the Dark',
            'death or glory': 'Death or Glory',
            'victory or death': 'Victory or Death',
            'rose of ph(?:ry|yr)gia': 'Rose of Phrygia',
        },
        lowpatterns={
            'lemongrass' + _any_and + 'geranium': 'Lemongrass & Geranium',
        },
        bases=[ 'vol. 2', 'vol. 3', 'essentials', # Essentials not actually a base, but class of soap
                'v3 vegan', 'v2 vegan', 'v3', 'v2' ]
    ),

    'Dr K Soap Company': Sniffer(
        lowpatterns={
            'peppermint': 'Peppermint',
            'lime': 'Lime',
        }
    ),

    'E&S': Sniffer(
        lowpatterns={
            'l' + _apostrophe + '[ée]t[ée]': 'l\'Été'
        }
    ),

    'Edwin Jagger': Sniffer(
        lowpatterns={
            'limes?' + _any_and + 'pom[ea]gran[ai]te': 'Limes & Pomegranate',
            'aloe vera': 'Aloe Vera',
            'sandalwood': 'Sandalwood',
            'menthol': 'cooling menthol',
        }
    ),

    'Eleven Shaving': Sniffer(
        patterns={
            'olive, musk' + _any_and + 'citrus': 'Olive, Musk & Citrus',
        },
        lowpatterns={
            'barbershop': 'Barbershop',
            'clary sage' + _any_and + 'violet': 'Clary Sage & Violet',
            'clary sage': 'Clary Sage & Violet',
            'DFS (?:limited edition|le)(?: 2019|)': 'DFS LE 2019',
        }
    ),

    'Elvado': Sniffer(
        lowpatterns={
            '(?:royal |)tahitian lime': 'Royal Tahitian Lime',
            'lake of the woods': 'Lake of the Woods',
        }
    ),

    'ETHOS': Sniffer(
        patterns={
            'm[éeè]lange d' + _apostrophe + 'agrumes': 'Mélange d\'Agrumes',
            'succ[èeé]s+': 'Succès',
        }
    ),

    'Eufros': Sniffer(
        patterns={
            'dam[ae]s? de noche': 'Dama de Noche',
            'rosa[ \\-]oud': 'Rosa-Oud',
            'vetiver de hait[íi]': 'Vetiver de Haití',
            'bar+ak(?:ah|) oudh?': 'Barakah Oudh',
            # this is not actually under the Eufros brand... should this be split off?
            # or... should all Eufros soaps be identified as "JabonMan?"
            'mediterr[áa]no l\\.e\\. bullgoose': 'Mediterráneo',
            'mediterr[áa]ne?o': 'Mediterráneo',
            'tier+a humeda': 'Tiera Humeda',
        },
        lowpatterns={
            'ylang[ \\-]ylang': 'Ylang Ylang',
            'Gea': 'Gea',
            'Tobacco': 'Tobacco',
        },
        bases = [ 'vegan' ]
    ),

    'Executive Shaving': Sniffer(
        patterns={
            'Citrus Kiss': 'Citrus Kiss',
            'Fuar Ach Snog': 'Fuar Ach Snog',
        },
        lowpatterns={
           'Natural': 'Natural',
        }
    ),

    'Extrò Cosmesi': Sniffer(
        patterns={
            'egyptian ou(?:dh?|r)': 'Egyptian Oudh',
            'pirata': 'Pirata',
            'frarinik': 'Frarinik',
            'del don': 'Del Don',
            'miele': 'Miele',
            '17°? stormo': '17° Stormo',
            'Bergam[oa]tto di Calabria': 'Bergamotto di Calabria',
        },
        lowpatterns={
            't[ao]bacco': 'Tabacco',
            'freddo': 'Freddo',
            'bay rum': 'Bay Rum',
            'dandy': 'Dandy',
        }
    ),

    'Fendrihan': Sniffer(
        patterns={
           'coconut' + _any_and + 'vanilla': 'Coconut & Vanilla',
        },
        lowpatterns={
            'aloe water': 'Aloe Water',
            'bay rum': 'Bay Rum',
            'bergamot': 'Bargamot',
            'sandalwood': 'Sandalwood',
        }
    ),

    'Fine Accoutrements': Sniffer(
        patterns={
            'american blend': 'American Blend',
        },
        lowpatterns={
            'Fresh Vetiver': 'Fresh Vetiver',
            'Green Vetiver': 'Green Vetiver',
            'Platinum': 'Platinum',
            'Santal Absolut': 'Santal Absolut',
        }
    ),

    'First Canadian Shave': Sniffer(
        patterns={
            'dicken' + _apostrophe + 's? cider': 'Dicken\'s Cider',
            'bl[óo]d av dreki': 'Blód av Dreki',
            'esther' + _apostrophe + 's peppermint' + _any_and + 'grapefruit': 'Esther\'s Peppermint and Grapefruit',
        },
        lowpatterns={
            'motherf[uc]*ker': 'Motherfucker',
            'mother-?fer': 'Motherfucker',
            'm\\*{4,12}r': 'Motherfucker',
            'barber\\s*shop': 'Barbershop',
        }
    ),

    'First Line Shave': Sniffer(
        patterns={
            'delmar blvd\\.?': 'Delmar Blvd.',
            'razor ruby undead': 'Razor Ruby Undead',
            'kituwah': 'Kituwah',
        },
        lowpatterns={
            'razor ruby': 'Razor Ruby',
            'blue$': 'Blue Label',
            'green$': 'Green Label',
            '(?:star|space) odyssey': 'Star Odyssey',
        }
    ),

    'Fitjar Islands': Sniffer(
        patterns={
            'Sl[åa]tter[øo]y': 'Slåtterøy',
            'Fjellheim': 'Fjellheim',
            'Folgefonn': 'Folgefonn',
            'Melderskin': 'Melderskin',
        }
    ),

    'Floris London': Sniffer(
        lowpatterns={
            'no\\.?\\s*89': 'No. 89',
            'elite': 'Elite',
        }
    ),

    'Free Soap Collective': Sniffer(
        lowpatterns={
            'adele(?:' + _apostrophe + 's|) fat': 'Adele Fat',
            _fougere + ' des alpe?s': 'Fougère des Alpes',
            'psych[ea]+delic modern': 'Psychedelic Modern',
            'Monterey Bay': 'Monterey Bay',
        }
    ),

    'Furbo': Sniffer(
        lowpatterns={
            'blue?': 'Blu',
        },
        default_scent='Furbo'
    ),

    'Gentleman\'s Nod': Sniffer(
        patterns={
            'kanpai': 'Kanpai'
        },
        lowpatterns={
            '(?:zaharoff +|)noir': 'Zaharoff Noir',
            '(?:zaharoff +|)signature royale?': 'Zaharoff Signature Royale',
            '(?:zaharoff +|)signature': 'Zaharoff Signature',
            'no. 85': 'Ernest',
            'no. 01': 'George',
            'no. 42': 'Jackie',
            'no. 13': 'Johnny',
            'no. 11': 'Vincent',
        }
    ),

    'Geo. F. Trumper': Sniffer(
        lowpatterns={
            '(?:extract of |)limes': 'Limes',
            'rose': 'Rose',
            'spanish leather': 'Spanish Leather',
        }
    ),

    'Gillette': Sniffer(
        patterns={
            'honeyflower women' +_apostrophe + 's(?: shave|shaving) cream': 'Honeyflower Pure',
            'planet kind': 'Planet Kind',
        },
        lowpatterns={
            'honeyflower': 'Honeyflower Pure',
            'pure': 'Pure',
        }
    ),

    'Godrej': Sniffer(
        lowpatterns={
            '(?:fresh |)lime': 'Lime Fresh',
            'menthol mist': 'Menthol Mist',
        }
    ),

    'The Goodfellas\' Smile': Sniffer(
        patterns={
            'tallow no?. *1': 'N. 1',
        },
        lowpatterns={
            'abysso': 'Abysso',
            'amber foug[èeé]re': 'Amber Fougere',
            'chronos': 'Chronos',
            'inferno': 'Inferno',
            'no?\\. 1': 'N. 1',
            'patronus': 'Patronus',
            'shibusa': 'Shibusa',
            'Pino Alpestre': 'Pino Alpestre',
        }
    ),

    'Grooming Department': Sniffer(
        patterns={
            '(?:conditioning |)shave oil': 'Conditioning Shave Oil',
            'Chypre Peach': 'Chypre Peach',
            'Coattails Redux': 'Coattails Redux',
            'incense' + _any_and + 'oud': 'Incense & Oud',
            'Dapper Mallard': 'Dapper Mallard',
            'Frankenlime': 'Frankenlime',
            'l' + _apostrophe + 'Avventura': 'l\'Avventura',
            'magnolia' + _any_and + 'oud': 'Magnolia & Oud',
            'Maleki': 'Maleki',
            'Earl Grey': 'Earl Grey',
            'Earl Grey Gelato': 'Earl Grey Gelato',
            'Peach Chypre': 'Peach Chypre',
            'Sandalwood Nobile': 'Sandalwood Nobile',
            'Valencia': 'Valencia',
            'conc[ao] d' + _apostrophe + 'or[oa]': 'Conca d\'Oro',
        },
        lowpatterns={
            'Aion': 'Aion',
            'Amare': 'Amare',
            'amore?': 'Amore',
            'Angel': 'Angel',
            'Boomer': 'Boomer',
            'Chai': 'Chai',
            'Coattails': 'Coattails',
            'Etereo': 'Etereo',
            'Ingress': 'Ingress',
            'Laundry': 'Laundry',
            'Lemon Bay': 'Lemon Bay',
            'Lavender': 'Lavender',
            'Otium': 'Otium',
            'Rainforest': 'Rainforest',
            'Soap': 'Soap',
            'Spa': 'Spa',
            'Unum': 'Unum',
            'Veritas': 'Veritas',
            'Wonderland': 'Wonderland',
            'ny *chypre': 'NYChypre',
            'le v[éeè]tiver': 'Le Vétiver',
        },
        bases=[ 'Nai', 'Kairos', 'Fortis', 'Lusso', 'Mallard' ]
    ),

    'Gryphon\'s Groomatorium': Sniffer(
        patterns={
            'citrus bomb': 'Citrus Bomb',
        },
        lowpatterns={
            'cider': 'Cider',
            'licorice mint': 'Licorice Mint',
        }
    ),

    'Harry\'s': Sniffer(
        lowpatterns={
            'shav(?:ing|e) *cream': 'Shave Cream with Eucalyptus',
            'cream': 'Shave Cream with Eucalyptus',
            'shav(?:ing|e) *gel': 'Shave Gel with Aloe',
            'gel': 'Shave Gel with Aloe',
        }
    ),

    'Haslinger': Sniffer(
        patterns={
            'salbei': 'Salbei',
            's(?:ch|c|h)afs?milch': 'Schafmilch',
            'sandelholt?z': 'Sandelholz',
        },
        lowpatterns={
            'aloe vera': 'Aloe Vera',
            'sensitive?': 'Sensitiv',
            'me+re?s(?:al|la)gen': 'Meeresalgen',
        }
    ),

    'Henri et Victoria': Sniffer(
        patterns={
            'duc de santal': 'Duc de Santal',
            'cogna[cn]' + _any_and + 'cuban cigars': 'Cognac and Cuban Cigars',
            'la poire fran[çc]aise?': 'La Poire Française',
            'chestnut l' + _apostrophe + 'orange': 'Chestnut l\'Orange',
            'nautilus': 'Nautilus',
        },
        lowpatterns={
            'foug[èeé]re': 'Fougère',
            'deuce': 'Deuce',
            'absinthe': 'Absinthe',
        }
    ),

    'Highland Springs Soap Company': Sniffer(
        lowpatterns={
            'green door': 'Green Door',
            'havana v(?:ie|ei)ja': 'Havana Vieja',
            'sippin(?:' + _apostrophe + '|g) by the fire': 'Sippin\' by the Fire',
        }
    ),

    'The Holy Black': Sniffer(
        patterns={
            'jack' + _any_and + 'ginger': 'Jack & Ginger',
            'dr\\. jekyl+' + _any_and + 'mr\\. hyde': 'Dr. Jekyll & Mr. Hyde',
        },
        lowpatterns={
            'bay whiskey lime': 'Secret Stash Bay Whiskey Lime',
            'lemon ice': 'Secret Stash Lemon Ice',
            'the sauce': 'Secret Stash The Sauce',
        }
    ),

    'House of Mammoth': Sniffer(
        patterns={
            'santal noir': 'Santal Noir',
            'mood indigo': 'Mood Indigo',
            'almo[nm]d(?:' + _any_and + '|\\s*)leather': 'Almond Leather',
        },
        lowpatterns={
            'cirrus': 'Cirrus',
            'flying squirrel': 'Cirrus',
            'restore': 'Restore',
            'stones': 'Stones',
            'indigo': 'Mood Indigo',
            'marine': 'Marine',
            'z': 'Z',
            '(?:the )tob+ac+[oa]nist': 'Tobacconist',
            '(?:cerberus|cerebrus)': 'Cerberus', # actually DG
            'em?brace': 'Embrace',
        },
        bases=[ 'tusk' ],
        custom=custom_mammoth
    ),

    'Hub City Soap Company': Sniffer(
        patterns={
            'aegyptus': 'Aegyptus',
            'chats? with grandpa': 'Chats With Grandpa',
            'f(?:ri|ir)day night lights': 'Friday Night Lights',
        },
        lowpatterns={
            'pages': 'Pages',
        }
    ),

    'Institut Karité': Sniffer(
        default_scent='Institut Karité'
    ),

    'Irisch Moos': Sniffer(
        default_scent='Irisch Moos'
    ),

    'Italian Barber': Sniffer(
        lowpatterns={
            'amici': 'Amici',
        }
    ),

    'Los Jabones de Joserra': Sniffer(
        patterns={
            'brih(?:ue|eu)ga': 'Brihuega',
            'kilix': 'Kilix'
        }
    ),

    'K Shave Worx': Sniffer(
        patterns={
            'Coconut Barber \(Wolf Whiskers Exclusive\)': 'Coconut Barber',
        },
        lowpatterns={
            'tomahawk': 'Tomahawk',
        }
    ),

    'Kiss My Face': Sniffer(
        lowpatterns={
            'fragrance free': 'Unscented',
            'lavender' + _any_and + 'shea': 'Lavender & Shea',
        }
    ),

    'Knightsbridge': Sniffer(
        lowpatterns={
            'aloe': 'Aloe Water',
            'bay rum': 'Bay Rum',
        }
    ),

    'Kool': Sniffer(
        lowpatterns={
            'frosty': 'Frosty',
            '(?:monsoon|moisture)': 'Monsoon',
        },
        default_scent='Frosty'
    ),

    'Krampert\'s Finest': Sniffer(
        lowpatterns={
            'bay rum(?: ar?cadian spice|)': 'Bay Rum Acadian Spice',
            'frostbite': 'Frostbite',
        }
    ),

    'Lather Jack': Sniffer(
        patterns={},
        lowpatterns={
            'bourbon' + _any_and + 'oak': 'Bourbon & Oak',
            '(?:the |)woodsy man': 'The Woodsy Man',
        }
    ),
    
    'Laugar of Sweden': Sniffer(
        lowpatterns={
            'rimfrost': 'Rimfrost',
        }
    ),

    'Liojuny Shaving': Sniffer(
        lowpatterns={
            'Tampa': 'Tampa',
            'Unknown': 'Unknown',
        }
    ),

    'Lisa\'s Natural Herbal Creations': Sniffer(
        lowpatterns={
            'doc hol+iday': 'Doc Holliday',
            '(?:irish green|green irish) tweed': 'Irish Green Tweed',
            'sandalwood' + _any_and + 'patchouli': 'Sandalwood & Patchouli',
        }
    ),

    'London Razors': Sniffer(
        patterns={
            'mountain laurel': 'Mountain Laurel',
        },
    ),

    'Los Angeles Shaving Soap Co.': Sniffer(
        patterns={
            'bespoke #1': 'Bespoke #1',
            'myrkvi[ðdo]r': 'Myrkviðr',
            'black *fern': 'Blackfern',
        },
        lowpatterns={
            '(?:the |)black rose': 'Black Rose',
        },
    ),

    'Lotus Eater': Sniffer(
        patterns={
            'durga' + _apostrophe + 's companion': 'Durga\'s Companion',
            'kookaburra' + _apostrophe + 's laugh': 'Kookaburra\'s Laugh',
            'sun wukong': 'Sun Wukong',
        },
        lowpatterns={
            'j[öo]tun*': 'Jötun',
            'h[äa]xan*': 'Häxan',
        }
    ),

    'MacDuff\'s Soap Company': Sniffer(
        patterns={
            'lili?acs in bloom': 'Lilacs in Bloom',
            'lychee is a stone fruit': 'Lychee is a Stone Fruit',
            'tr(?:ai|ia)l tobacco': 'Trail Tobacco',
        },
        lowpatterns={
            'rose gold': 'Rose Gold',
            'royal earl gr[ea]y': 'Royal Earl Grey',
            'orange creamsick?le': 'Orange Creamsicle',
            'birch *[\\+\\-x] *root': 'Birch + Root'
        },
        bases=[ 'version 3', 'V3', 'V4' ]
    ),

    'Maggard Razors': Sniffer(
        patterns={
            'london barber(?:shop|)': 'London Barbershop',
            'mango sage tea': 'Mango Sage Tea',
            'northern moss': 'Northern Moss',
        },
        lowpatterns={
            'limes' + _any_and + 'bergamot': 'Limes & Bergamot',
            'bergamot' + _any_and + 'limes': 'Limes & Bergamot',
            'tobacco' + _any_and + 'leather': 'Tobacco & Leather',
            'lilac': 'Lilac',
            'orange' + _any_and + 'menthol': 'Orange Menthol',
        }
    ),

    'Martin de Candre': Sniffer(
        lowpatterns={
            'original': 'Original',
            'classic': 'Original',
            'foug[èeé]re': 'Fougère',
            'a(?:gr|rg)umes': 'Agrumes',
            'vet[iy]ver': 'Vetyver',
        },
        default_scent='Original'
    ),

    'Mastro Miche': Sniffer(
        patterns={
            'art?iglio': 'Artiglio',
            'zihuataneo': 'Zihuatanejo',
        },
        lowpatterns={
            'b(?:-| |)owl': 'B-Owl',
        }
    ),

    'Mickey Lee Soapworks': Sniffer(
        patterns={
            '(?:the |)kraken': 'The Kraken',
            '(?:the |)drunken goat': 'The Drunken Goat',
            'l[ae] belle d[ue] suds?': 'La Belle du Sud',
        },
        lowpatterns={
            'r[éeè]uniou?n': 'Réunion',
            'lu' + _apostrophe + 'au': 'Lu\'au',
            #'j[ūu]rat[ėe]': 'Jūratė',
            # preferring something which Excel can diplay for now
            'j[ūu]rat[ėe]': 'Jurate',
            'pant(?:ie|y) dropper': 'Pantie Dropper',
            'jefferson (?:square|street)': 'Jefferson Square',
            'colonia d[ie] agrumi': 'Colonia di Agrumi',
        }
    ),

    'Mike\'s Natural Soaps': Sniffer(
        patterns={
            'lemongrass' + _any_and + 'eucalyptus': 'Lemongrass & Eucalyptus',
            'rose,? patchouli,?(?:' + _any_and + '| )cedarwood': 'Rose, Patchouli, Cedarwood',
            'pine' + _any_and + 'cedarwood': 'Pine & Cedarwood',
            'orange,? cedarwood,? ' + _any_and + 'black pepper': 'Orange, Cedarwood, & Black Pepper',
        },
        lowpatterns={
            'lime': 'Lime',
            'barber\\s*shop': 'Barbershop',
        }
    ),

    'Mitchell\'s Wool Fat': Sniffer(
        lowpatterns={
            # for the time being, to accommodate TTS
            'n/a': 'Mitchell\'s Wool Fat'
        },
        default_scent='Mitchell\'s Wool Fat'
    ),

    'Mondial 1908': Sniffer(
        lowpatterns={
            'sandal(?:o\\b|wood)': 'Sandalo',
            'bergamot(?:to|)' + _any_and + 'neroli': 'Bergamotto Neroli',
            'bergamot(?:to|) neroli': 'Bergamotto Neroli',
            'green tobacco': 'Tobacco Verde',
        }
    ),

    'Moon Soaps': Sniffer(
        lowpatterns={
            'amaretto(?: *e?speciale?|)': 'Amaretto Speciale',
            'union': 'Union',
        }
    ),

    'Mühle': Sniffer(
        lowpatterns={
            'aloe vera': 'Aloe Vera',
            'sandelholz': 'Sandalwood',
        }
    ),

    'Murphy and McNeil': Sniffer(
        patterns={
            'nantahala': 'Nantahala',
            't[oa]bac fan[ai]+le': 'Tobac Fanaile',
            'gael luc': 'Gael Luc',
            'triskele': 'Triskele',
            'magh tured': 'Magh Tured',
            'ogham stone': 'Ogham Stone',
            'cat sid+he': 'Cat Sidhe',
            'barbershop de los muertos': 'Barbershop de los Muertos',
            'gael laoch': 'Gael Laoch',
        },
        lowpatterns={
            'bdlm': 'Barbershop de los Muertos',
            'st\\.? james': 'St. James',
        },
        bases=[ 'sl[aá]inte', 'aon', 'kodiak' ]
    ),

    'Myrsol': Sniffer(
        patterns={
            'agua bals[áa]mica': 'Agua Balsámica',
            'don carlos(?: 1972|)': 'Don Carlos 1972',
        }
    ),

    'Mystic Water Soap': Sniffer(
        lowpatterns={
            'bay rum': 'Bay Rum',
            'Brown Windsor': 'Brown Windsor',
            'irish travel+er': 'Irish Traveller',
        }
    ),

    'Nivea': Sniffer(
        lowpatterns={
            'protect' + _any_and + 'care': 'Protect & Care',
            'sensitive cooling': 'Sensitive Cooling',
            'sensitive': 'Sensitive',
        }
    ),

    'Noble Otter': Sniffer(
        patterns={
            'the night before': 'The Night Before',
            '(?:th[èeé] |)noir [es]t vanill[ea]': 'Thé Noir et Vanille',
            'tnev\\b': 'Thé Noir et Vanille',
            'northern elix[ie]r': 'Northern Elixir',
            'hama[mn]i': 'Hamami',
            'bar+\\s*bar+': 'Barrbarr',
            '(?:two|2)\\s*kings': 'Two Kings',
        },
        lowpatterns={
            'orbit': 'Orbit',
            'monarch': 'Monarch',
            'bare': 'Bare',
            'rawr\\b': 'Rawr',
            'lone\\s*star': 'Lonestar',
            'fire\\s*fighter': 'Firefighter',
            'kaboom!?': 'Kaboom!',
            '24kt?': '24kt',
        },
        custom=custom_noble_otter
    ),

    'l\'Occitane': Sniffer(
        lowpatterns={
            'cade': 'Cade',
            'cedrat(?: gel|)': 'Cedrat',
        },
        default_scent='Cade'
    ),

    'Officina Artigiana': Sniffer(
        default_scent='Sapone da Barba'
    ),

    'Officina di Santa Maria Novella': Sniffer(
        lowpatterns={
            'crema da barba': 'Crema da Barba',
            'tabacco toscano': 'Tabacco Toscano',
        },
        default_scent='Crema da Barba'
    ),

    'Ogallala Bay Rum': Sniffer(
        lowpatterns={
            '(?:bay rum|),? *sage,?' + _any_and + 'cedar': 'Bay Rum, Sage & Cedar',
            '(?:bay rum|),? *limes,?' + _any_and + 'peppercorn': 'Bay Rum, Limes & Peppercorn',
            '(?:bay rum|)' + _any_and + 'sweet orange': 'Bay Rum & Sweet Orange',
            '(?:bay rum|)' + _any_and + 'vanilla': 'Bay Rum & Vanilla',
        },
        default_scent='Bay Rum'
    ),

    'Opus Ruri': Sniffer(
        patterns={
            'la salvia 4': 'Una Salvia 4',
            'la salvia': 'Una Salvia',
        }
    ),

    'Osma': Sniffer(
        lowpatterns={
            'rasage': 'Rasage',
            'tradition(?:al|)': 'Tradition',
        }
    ),

    'P.160': Sniffer(
        patterns={
            'tipo morbido': 'Tipo Morbido',
            'tipo duro': 'Tipo Duro',
        }
    ),

    'Pacific Shaving Co.': Sniffer(
        lowpatterns={
            'clean': 'Unscented',
            'ultra slick': 'Ultra Slick',
            'natural': 'Natural',
            'caf+[ei]+nated': 'Caffeinated',
        }
    ),

    'Palmira': Sniffer(
        default_scent='Albus 1871'
    ),

    'Palmolive': Sniffer(
        patterns={
            'Rinfrescante': 'Rinfrescante', # mentholated
        },
        lowpatterns={
            'classic': 'Classic',
            'stick': 'Classic',
            'sensitive': 'Sensitive',
            'Classica Crema Da Barba': 'Classic',
        },
        default_scent='Classic'
    ),

    'PannaCrema': Sniffer(
        patterns={
            'nu[àa]via *-? *blue?': 'Nuàvia Blu',
            'nu[àa]via *-? *(?:ross[ao]?|red)': 'Nuàvia Rossa',
            'nu[àa]via *-? *nema': 'Nuàvia Nema',
            'nu[àa]via *-? *(?:verde|green)': 'Nuàvia Verde',
        },
        lowpatterns={
            'namaste': 'Namaste',
            # used for matching maker on just Nuàvia
            'blue?': 'Nuàvia Blu',
            '(?:ross[ao]?|red)': 'Nuàvia Rossa',
            'nema': 'Nuàvia Nema',
            '(?:verde|green)': 'Nuàvia Verde',
        }
    ),

    'Panee Soaps': Sniffer(
        patterns={
            'the bergamot mystery': 'The Bergamot Mystery',
            'bergamot mystery': 'The Bergamot Mystery',
        }
    ),

    'Paragon Shaving': Sniffer(
        patterns={
            'sunlit forest': 'Sunlit Forest',
        }
    ),

    'Penhaligon\'s': Sniffer(
        patterns={
            'blenheim': 'Blenheim Bouquet',
            'endymion': 'Endymion',
        }
    ),

    'Le Père Lucien': Sniffer(
        patterns={
            'cologne[\\s\\-]*foug[èeé]re': 'Cologne-Fougère',
            'oud[\\s\\-]*santal': 'Oud-Santal',
            'Assinerie de la Vioune': 'Assinerie de la Vioune', # Lainess
        },
        lowpatterns={
            'traditional': 'Traditionnel',
            'apricot': 'Abricot',
            '(?:parfum |)cerise': 'Cerise', # Lainess mare's milk
            '(?:parfum |)miel': 'Miel', # Lainess donkey milk
            'blue pearl': 'Blue Pearl', # Lainess mare's milk
        }
    ),

    'Phoenix and Beau': Sniffer(
        patterns={
            'citra royale?': 'Citra Royale',
            'albion': 'Albion',
            'achilles last stand': 'Achilles Last Stand',
        },
        lowpatterns={
            'spitfire': 'Spitfire',
            'imperial rum': 'Imperial Rum',
            'luna': 'Luna',
            'v60': 'V60',
        }
    ),

    'Phoenix Artisan Accoutrements': Sniffer(
        patterns={
            'cad ck6': 'CaD',
            '^cad$': 'CaD',
            'club\\s*guy': 'Clubguy',
            'Albion of the North': 'Albion of the North',
            'Atomic Age Bay Rum': 'Atomic Age Bay Rum',
            'lavender planet': 'Lavender Planet',
            'bailey' + _apostrophe + 's irish coffee': 'Bailey\'s Irish Coffee',
            'doppelg[äa]nger gr[ea]y(?: label|)': 'Doppelgänger Grey',
            'doppelg[äa]nger gold(?: label|)': 'Doppelgänger Gold',
            'doppelg[äa]nger black(?: label|)': 'Doppelgänger Black',
            'doppelg[äa]nger orange(?: label|)': 'Doppelgänger Orange',
            'doppelg[äa]nger ox blood(?: label|)': 'Doppelgänger Ox Blood',
            'lo[~\\-]haiku': 'Lo~Haiku',
            'will[ \\-]*o' + _apostrophe + '[ \\-]*the[ \\-]*wisp': 'Will O\' the Wisp',
        },
        lowpatterns={
            'cad': 'CaD',
            'esp\\b': 'ESP',
            'cavendish': 'Cavendish',
            'lo[ \\-~]haiku': 'Lo~Haiku',
            'spring[\\- ]heeled jack': 'Spring-Heeled Jack',
            'twee\\!?': 'Twee!',
        },
        bases=[ 'CK-?6' ]
    ),

    'Pinnacle Grooming': Sniffer(
        lowpatterns={
            'dali': 'Dali',
            'krampus': 'Krampus',
            'visionary': 'Visionary',
        }
    ),

    'Portus Cale': Sniffer(
        lowpatterns={
            'black edition': 'Black',
        },
         # looks like only black has been made as shaving soap
         # but they have many other scents as bath soaps
         default_scent='Black'
    ),

    'Pré de Provence': Sniffer(
        patterns={
            '(?:number|no\.?|num\.?|#|)\\s*63': 'No. 63',
            'PdP63': 'No. 63',
        },
        lowpatterns={
            'bergamot' + _any_and + 'thyme': 'Bergamot and Thyme',
            'original': 'Original',
        },
        default_scent='Original'
    ),

    'Prep': Sniffer(
        default_scent='The Original Formula'
    ),

    'Proraso': Sniffer(
        patterns={
            '(?:white |)green tea' + _any_and + 'oat': 'Green Tea & Oatmeal',
            'red sandalwood': 'Sandalwood',
            '(?:green |)menthol' + _any_and + 'eucalyptus': 'Menthol & Eucalyptus',
            'eucalypt[a-z]*(?: oil|)' + _any_and + 'menthol': 'Menthol & Eucalyptus',
            'aloe' + _any_and + 'vitamin e': 'Aloe & Vitamin E',
        },
        lowpatterns={
            '(?:green|verde)': 'Menthol & Eucalyptus',
            '(?:red|rosso)': 'Sandalwood',
            '(?:white|bianco|sensitive(?: *skin|))': 'Green Tea & Oatmeal',
            'blue?': 'Aloe & Vitamin E',
            'sandalwood': 'Sandalwood',
        }
    ),

    'Prosar': Sniffer(
        lowpatterns={
            'shave cream': 'Classic',
        },
        default_scent='Classic',
    ),

    'Purely Skinful': Sniffer(
        lowpatterns={
            'smooth operator': 'Smooth Operator',
            'sweet devotion': 'Sweet Devotion',
            'wonderland': 'Wonderland',
            'sweet cherry pie': 'Sweet Cherry Pie',
        }
    ),

    'RazoRock': Sniffer(
        patterns={
            'what the puck[\W]*\\s+blue': 'Blue Barbershop',
            'what the puck[\W]*\\s+lime(?: burst|)': 'What the Puck?! Lime Burst',
            'what the puck[\W]*\\s+black': 'What the Puck?! Black Label',
            'what the puck[\W]*\\s+gold': 'What the Puck?! Gold Label',
            'what the puck[\W]*\\s+green': 'What the Puck?! Green Label',
            'mudder focker': 'Mudder Focker',
            'Santa Maria del Fiore': 'Santa Maria del Fiore',
        },
        lowpatterns={
            'blue\\s*': 'Blue Barbershop',
            '(?:essential oil of |)lime': 'Essential Oil of Lime',
            'black label': 'What the Puck?! Black Label',
            '(?:essential oil of |)lavender': 'Essential Oil of Lavender',
            # TODO inconsistent name?
            'blue label': 'Blue Barbershop',
            'p\\.?\\s*160': 'P.160',
            'xxx': 'XXX',
            'green (?:label|puck)': 'What the Puck?! Green Label',
            'dead sea': 'The Dead Sea',
        }
    ),

    'Raz*War': Sniffer(
        patterns={
            'ginger belle': 'Ginger Belle',
            'atomic kim': 'Atomic Kim',
        },
        lowpatterns={
            'spice age': 'Spice Age',
        }
    ),

    'Red House Farm': Sniffer(
        patterns={
            _apostrophe + 'tis the saison': '\'Tis the Saison',
            'pan de muerto': 'Pan de Muerto',
            'Frankincense, Anise,?' + _any_and + 'Orange': 'Pan de Muerto',
        },
        lowpatterns={
            'cedar[^\w]+lime': 'Cedar-Lime',
            '(?:1920 |)barbershop': 'Barbershop 1920',
            'sand(?:al|le)woods?' + _any_and + 'bourbon': 'Sandalwood & Bourbon',
            'bourbon(?:' + _any_and + '|\\s+)sand(?:al|le)wood': 'Sandalwood & Bourbon',
            'kitchen sink': 'Kitchen Sink',
        },
    ),

    'St. James of London': Sniffer(
        lowpatterns={
            'sandalwood' + _any_and + 'bergamot': 'Sandalwood & Bergamot',
            'Tonka' + _any_and + 'Tobacco Leaf': 'Tonka and Tobacco Leaf',
            'Mandarin' + _any_and + 'Patchouli': 'Mandarin & Patchouli',
        }
    ),

    'Saponificio Varesino': Sniffer(
        patterns={
            'cub+eb+e': 'Cubebe',
            'opuntia': 'Opuntia',
            'Settantesimo Anniversario': '70th Anniversary',
        },
        lowpatterns={
            'cosmo': 'Cosmo',
            '70th(?: anniver?sary|)': '70th Anniversary',
            'desert ver?tiver': 'Desert Vetiver',
            'dolomiti': 'Dolomiti',
            'stel+a alpin[ae]': 'Stella Alpina',
        },
        bases=[ 'beta 4.1', 'beta 4.2', 'beta 4.3', 'beta' ]
    ),

    'The Savage Homestead': Sniffer(
        lowpatterns={
            'rustic': 'Rustic',
            'classic': 'Classic',
            'lavender, sage,?' + _any_and + 'rosemary': 'Classic',
            'warm woods, amber,?' + _any_and + 'vanilla': 'Rustic',
        }
    ),

    'La Savonnière du Moulin': Sniffer(
        lowpatterns={
            'unscented': 'Unscented',
            'sans parfum': 'Unscented',
            'but+er\\s*scotch': 'Butterscotch',
        }
    ),

    'Scheermonnik': Sniffer(
        patterns={
            '(?:1778 |)beau brummell': '1778 Beau Brummell',
            'Delft Donderslag': 'Delft Donderslag',
            'delfts? wit': 'Delft Wit',
        },
        lowpatterns={
            'puur': 'Puur',
            'soek': 'Soek',
        }
    ),

    'Shannon\'s Soaps': Sniffer(
        patterns={
            'bay patchouli grapefruit': 'Bay Patchouli Grapefruit',
        },
        lowpatterns={
            'barber\\s*shop': 'Barbershop',
            'pi[ñn]a colada': 'Piña Colada',
            'lit\\b': 'Lit',
            'lady luck': 'Lady Luck',
            'fig' + _any_and + 'apricot': 'Fig & Apricot',
        },
    ),

    'SHAVE DANDY': Sniffer(
        lowpatterns={
            'Pino N[ei]ro': 'Pino Nero',
            'cosmic stash': 'Cosmic Stash',
        }
    ),

    'Signature Soaps': Sniffer(
        lowpatterns={
            'britann?ia': 'Britania',
            'caledonia': 'Caledonia',
            'capra': 'Capra',
            'ebo(?:rac|cur)um': 'Eboracum',
        },
        bases=[ 'hybrid' ]
    ),

    'Siliski Soaps': Sniffer(
        patterns={
            'midnight in tunisia': 'Midnight in Tunisia',
            'apothecary cellars': 'Apothecary Cellars',
        },
        lowpatterns={
            'internal calamity': 'Internal Calamity',
        }
    ),

    'Simpsons': Sniffer(
        lowpatterns={
            'caf[ée] latte': 'Café Latte',
            'vanilla' + _any_and + 'rose': 'Vanilla & Rose',
            'peppermind' + _any_and + 'rosemary': 'Peppermint & Rosemary',
            'sandalwood': 'Sandalwood',
            'lime': 'Lime',
            'bay rum': 'Bay Rum',
        },
        bases=[ 'ultra[- ]?glide' ]
    ),

    'Smoking Monster': Sniffer(
        lowpatterns={
            'charm\\w+ orang': 'Charmed Orange',
            'unknown unknown': 'Unknown Unknown', # so it's not "single scent"
        }
    ),

    'The Soap Exchange': Sniffer(
        lowpatterns={
            'barbershop': 'Barbershop',
            'sandalwood(?:' + _any_and + '|)vanilla': 'Sandalwood Vanilla',
        }
    ),

    'Southern Witchcrafts': Sniffer(
        patterns={
            'grave\\s*fruit\\s*(?:2|ii)': 'Gravefruit II',
            'grave\\s*fruit\\s*(?:1|i|)': 'Gravefruit',
            'desa?ia?rology': 'Desairology',
            'anthropophagy': 'Anthropophagy',
            'valley of ashes': 'Valley of Ashes',
            'ne[ck]romanti[ck]': 'Necromantic',
            'd(?:ru|ur)antia': 'Druantia',
            'p[oa]mona': 'Pomona',
            'tres matres': 'Tres Matres',
            'Grey Phetiver': 'Grey Phetiver',
            'Lycanthropy': 'Lycanthropy',
            'foug[èeé]re n[ea]m[ea]ta': 'Fougère Nemeta',
            'gr[ea]y phetiver': 'Grey Phetiver',
            '(?:special edition(?:shave soap|)|)goth(?:orum|ic) ton?str?in[ae]': 'Gothorum Tonstrina',
        },
        lowpatterns={
            'cedar': 'Cedar',
            'autu?m[nm]? ash': 'Autumn Ash',
            'sa(?:mh|hm)ain': 'Samhain',
            'voa': 'Valley of Ashes',
            'n[ea]m[ea]ta': 'Fougère Nemeta',
        }
    ),

    #'Spartium Natural Cosmetics': # TODO Meštar

    'Spearhead Shaving Company': Sniffer(
        patterns={
            'seaforth!? "?heather"?': 'Seaforth! Heather',
            'seaforth!? "?spiced"?': 'Seaforth! Spiced',
            'seaforth!?\\s*-\\s*heather': 'Seaforth! Heather',
            'seaforth!?\\s*-\\s*spiced': 'Seaforth! Spiced',
            '(?:seaforth!?\\s*-\\s*|)sea spice li[mn]e': 'Seaforth! Sea Spice Lime',
            'nutmeg' + _any_and + 'heliotrope': 'Nutmeg & Heliotrope',
            'cedar,? clary\\s*sage,?' + _any_and + 'bergamot': 'Cedar, Clarysage, Bergamot',
        },
        lowpatterns={
            'heather!?': 'Seaforth! Heather',
            'spiced?!?': 'Seaforth! Spiced',
            'sea spice[ \\.]lime': 'Seaforth! Sea Spice Lime',
            'lavender' + _any_and + 'tonka': 'Lavender & Tonka',
            'lavender(?:' + _any_and + '|)vanilla': 'Lavender & Vanilla',
            'bergamot' + _any_and + 'sandalwood': 'Bergamot & Sandalwood',
            'oakmoss' + _any_and + 'sandalwood': 'Oakmoss & Sandalwood',
        },
        bases=[ '20.1' ]
    ),

    'Stirling Soap Co.': Sniffer(
        patterns={
            'st[ie]rling gentlem[ae]n': 'Stirling Gentleman',
            'rambling? man': 'Ramblin\' Man',
            'port[\\- ]au[\\- ]prince': 'Port-au-Prince',
            'phara?oa?h?' + _apostrophe + 's dreamsc?ick?le': 'Pharaoh\'s Dreamsicle',
            'ar[kc]adia': 'Arkadia',
            'sharp(?:ed|) dressed man': 'Sharp Dressed Man',
            'eskimo tuxedo': 'Eskimo Tuxedo',
            'marg(?:a|he)ritas in the arctic': 'Margaritas in the Arctic',
            'iced pineapple': 'Iced Pineapple',
            'scarn': 'Scarn',
            'executive man': 'Executive Man',
            'haverford': 'Haverford',
            'unscented (?:with |)beeswax': 'Unscented with Beeswax',
            'naked' + _any_and + 'smooth': 'Naked & Smooth',
            'vanilla bean e[sx]presso': 'Vanilla Bean Espresso',
            '(?:scot' + _apostrophe + 's|scotch) pine sheep': 'Scots Pine Sheep',
            'electric sheep': 'Electric Sheep',
            'vanilla sandalwood$': 'Vanilla Sandalwood',
            'meghalaya(?: *\\(SFWS\\)|)': 'Meghalaya',
            'unscented(?: with|) *bees *wax': 'Unscented',
        },
        lowpatterns={
            'spice': 'Stirling Spice',
            'noir': 'Stirling Noir',
            'green': 'Stirling Green',
            'blu\\b': 'Stirling Blu',
            'gentlem[ae]n': 'Stirling Gentleman',
            'con+if+erous': 'Coniferous',
            'christmas eve': 'Christmas Eve',
            'mita': 'Margaritas in the Arctic',
            'iced coffee': 'Iced Coffee',
            'gin' + _any_and + 'tonic': 'Gin & Tonic',
            'barber\\s*shop': 'Barbershop',
            'bar?bar\\s*shop': 'Barbershop',
            'frankincense' + _any_and + 'myrrh': 'Frankincense & Myrrh',
            'agar': 'Agar',
            'lime': 'Lime',
            'pumpkin spice': 'Pumpkin Spice',
            'bergamot(?:' + _any_and + '|\\s+)lavender': 'Bergamot Lavender',
            'lavender(?:' + _any_and + '|\\s+)sage': 'Lavender Sage',
            'almond (?:creme|cream)': 'Almond Creme',
            'blood on steel': 'Tsuka', # renamed
            'sa[nm]d(?:al|le)wood': 'Sandalwood',
            'one': 'Stirling One',
            'grapefruit(?:\\(?with menthol\\)?|)': 'Grapefruit',
        },
        bases=[ 'mutton tallow', 'mutton', 'glacial', 'beeswax' ]
    ),

    'Stone Cottage Soapworks': Sniffer(
        lowpatterns={
            'foug[èeé]re': 'Fougère',
            'il barbiere': 'Il Barbiere',
            'figg?' + _any_and + 'peare?': 'Figg & Peare',
        }
    ),

    'Storybook Soapworks': Sniffer(
        patterns={
            'carnivale': 'Carnivale',
            'west egg': 'West Egg',
            'coffee spoons': 'Coffee Spoons',
            'chasing sunsets': 'Chasing Sunsets',
            'elysium': 'Elysium',
            'fresca intensa': 'Fresca Intensa',
            'hallward' + _apostrophe + 's dream': 'Hallward\'s Dream',
        },
        lowpatterns={
            'la for[êe]t de liguest': 'La Forêt de Liguest',
        }
    ),

    'Strike Gold Shave': Sniffer(
        patterns={
            'l[ae] b[ea]f[ae]na': 'La Befana',
        },
        lowpatterns={
            'Kennedy': 'Kennedy',
            'Old Hickory': 'Old Hickory',
            'Rushmore': 'Rushmore',
            'Grant': 'Grant',
        }
    ),

    'Suavecito': Sniffer(
        patterns={
            'whiske?y bar': 'Whiskey Bar',
        },
        lowpatterns={
            'shaving cream': 'Shaving Cream', # "natural peppermint scent"
            'peppermint': 'Shaving Cream',
        }
    ),

    'The Sudsy Soapery': Sniffer(
        patterns={
            'top o' + _apostrophe + ' the morning': 'Top O\' the Morning',
            'white sage' + _any_and + 'lime': 'White Sage and Lime',
            'lemon rose chypre': 'Lemon Rose Chypre',
        },
        lowpatterns={
            'lavend[ea]r' + _any_and + 'peppermint': 'Lavender & Peppermint',
            'sandalwood' + _any_and + 'myrrh': 'Sandalwood & Myrrh',
            'sandalwood' + _any_and + 'citrus': 'Sandalwood & Citrus',
            'rose' + _any_and + 'black pepper': 'Rose & Black Pepper',
            'delor de treget': 'Delor de Treget',
            'yuzu[/, ]rose[/, ]patchouli': 'Yuzu/Rose/Patchouli',
            'bay' + _any_and + 'citrus': 'Bay & Citrus',
            'citrus' + _any_and + 'bay': 'Bay & Citrus',
            'pine' + _any_and + 'cedar': 'Pine & Cedar',
            'cedar' + _any_and + 'pine': 'Pine & Cedar',
        }
    ),

    'Summer Break Soaps': Sniffer(
        patterns={
            'teacher' + _apostrophe + 's pet': 'Teacher\'s Pet',
            'valedictorian': 'Valedictorian',
            'homecoming': 'Homecoming',
            'field day': 'Field Day',
            'bell\\s*ringer': 'Bell Ringer',
            'cannonball!?': 'Cannonball!',
            'mountain laurel': 'Mountain Laurel',
        },
        lowpatterns={
            'roty 2020': 'ROTY 2020', # K1986
            'roty 2021': 'ROTY 2021', # jwoods23
            'recess': 'Recess',
            'history 1\\d*': 'History 101',
        },
        custom=custom_summer_break
    ),

    'The Swedish Witch': Sniffer(
        bases=[ 'vegan' ]
    ),

    'Tabac': Sniffer(
        lowpatterns={
            'tabac': 'Original',
        },
        default_scent='Original',
        bases=[ '(?:new|old)' ]
    ),

    'Tallow + Steel': Sniffer(
        patterns={
            'morning coffee in the canadian wilderness': 'Morning Coffee in the Canadian Wilderness',
            's[àa]sq' + _apostrophe + 'ets': 'Sàsq’ets',
            'Merchandise 7x': 'Merchandise 7x',
        },
        lowpatterns={
            'kyoto': 'Kyoto',
            'boreal': 'Boreal',
            'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
            'yrp': 'Yuzu/Rose/Patchouli',
            'y/r/p': 'Yuzu/Rose/Patchouli',
            'vide poche': 'Vide Poche',
            '7x': 'Merchandise 7x',
        }
    ),

    'Taylor of Old Bond Street': Sniffer(
        patterns={
            'jermyn st(?:reet|)\\.?': 'Jermyn Street',
            'mr\\.? *taylor' + _apostrophe + 's?': 'Mr Taylors',
            'eton college': 'Eton College',
        },
        lowpatterns={
            'rf': 'Royal Forest',
            'lemon' + _any_and + 'lime': 'Lemon & Lime',
            'lime zest': 'Lime Zest',
            'grapefruit': 'Grapefruit',
            'cedarwood': 'Cedarwood',
            'organic shav(?:ing|e) cream': 'Unscented',
        }
    ),

    'Tcheon Fung Sing': Sniffer(
        patterns={
            'shave' + _any_and + 'roses rosehip': 'Shave & Roses Rosehip',
            'shave' + _any_and + 'roses dracaris': 'Shave & Roses Dracaris',
            # lineo intenso
            '(?:Aroma Intenso |)arancia amaro': 'Arancia Amaro',
            '75° witch hazel ' + _any_and + ' oak': '75° Witch Hazel & Oak',
        },
        lowpatterns={
            'diVino': 'diVino',
            '75(?:th anniversary|)': '75° Witch Hazel & Oak',
            '75 witch hazel' + _any_and + 'oak': '75° Witch Hazel & Oak',
            # lineo intenso
            'bergamotto neroli': 'Bergamotto Neroli',
            'crazy sandalwood': 'Crazy Sandalwood',
        }
    ),

    '345 Soap Co.': Sniffer(
        lowpatterns={
            'white buffalo': 'White Buffalo',
            'shark *b(?:ite|ait)': 'Shark Bite',
            'bana[no\\-]*rama': 'Bana-o-rama'
        }
    ),

    '3P': Sniffer(
        lowpatterns={
            'mandorla': 'Mandorla',
            'almond': 'Mandorla',
        },
        default_scent='Mandorla'
    ),

    'La Toja': Sniffer(
        default_scent='La Toja',
    ),

    'Turtleship Shave Co.': Sniffer(
        lowpatterns={
            'bay rum': 'Bay Rum',
            'te *java': 'Te Java',
        }
    ),

    'Valobra': Sniffer(
        lowpatterns={
            '(?:shaving |)stick': 'Stick', # one description says almond
            'almond': 'Almond',
        },
        bases=[ 'soft shaving soap', 'soft' ]
    ),

    'Van der Hagen': Sniffer(
        lowpatterns={
            'unscented': 'Unscented',
            'scented': 'Scented',
            'deluxe': 'Deluxe',
        },
    ),

    'Veleiro': Sniffer(
        default_scent='Veleiro'
    ),

    'Via Barberia': Sniffer(
        lowpatterns={
            'aquae\\s*[23]?': 'Aquae',
            'fructi\\s*[23]?': 'Fructi',
            'herbae\\s*[23]?': 'Herbae',
        }
    ),

    'Vicco': Sniffer(
        lowpatterns={
            'turmeric': 'Turmeric',
            't[ue]rmeric *(?:s? with|)sandalwood': 'Turmeric S with Sandalwood Oil',
            's with sandalwood oil': 'Turmeric S with Sandalwood Oil',
        }
    ),

    'Viking Soap & Cosmetic': Sniffer(
        lowpatterns={
            'ragn[ae]r': 'Ragnar',
            'norway': 'Norway',
            'denmark': 'Denmark',
            'sweden': 'Sweden',
            'fjord': 'Fjord',
            'old norse': 'Old Norse',
        }
    ),

    'Vitos': Sniffer(
        lowpatterns={
            'verde': 'Green',
            'rosso': 'Red',
            'Extra Super': 'Red',
            '(?:super |)red': 'Red',
            'supercrema': 'Green', # green, red, I dunno?
            'lanolin' + _any_and + 'eucalyptus': 'Lanolin & Eucalyptus'
        }
    ),

    'West Coast Shaving': Sniffer(
        patterns={
            'gl[øo]gg': 'Gløgg',
            'grapefroot': 'Grapefroot',
            'pear[\\- ]brr+ shop+e?': 'Pear-Brrr Shoppe',
            'gatsby v2': 'Gatsby V2',
        },
        lowpatterns={
            'oriental': 'Oriental',
            'chypre': 'Chypre',
            'foug[èeé]re': 'Fougère',
            'cologne': 'Cologne',
        }
    ),

    'West of Olympia': Sniffer(
        patterns={
            'PNW Wetshavers Meetup 2018': 'PNW Wetshavers Meetup 2018',
            'PNW Wetshavers Meetup 2019': 'PNW Wetshavers Meetup 2019',
        },
        lowpatterns={
            'tobacco' + _any_and + 'coffee': 'Tobacco & Coffee',
            'eucalyptus' + _any_and + 'spearmint': 'Eucalyptus & Spearmint',
        }
    ),

    'Wet Shaving Delight': Sniffer(
        patterns={
            'go ask alice': 'Go Ask Alice',
            'wet shaving delight': 'placeholder to prevent single scent logic',
        }
    ),

    'Wet Shaving Products': Sniffer(
        lowpatterns={
            'gaelic tweed': 'Gaelic Tweed',
            'mahogany': 'Mahogany',
            'tobacco': 'Tobacco',
            'ol' + _apostrophe + 'kentucky': 'Ol\' Kentucky',
        },
        bases=[ 'Formula T', 'Rustic' ]
    ),

    'Whispers from the Woods': Sniffer(
        lowpatterns={
            'hippie' + _apostrophe + 's? blend': 'Hippie Blend',
        }
    ),

    'Wholly Kaw': Sniffer(
        patterns={
            'foug[èeé]re mania': 'Fougère Mania',
            '(?:la |)foug[èeé]re parfaite': 'La Fougère Parfaite',
            'fou?gu?[èeé]re bou?qu?et': 'Fougère Bouquet',
            'pasha' + _apostrophe + 's pride': 'Pasha\'s Pride',
            'denariou?s': 'Denarius',
            'scentropy': 'Scentropy',
            'vor (?:v|5)': 'Vor V',
            'valentyn?ka': 'Valentynka',
            '(?:the |)man from mayfair': 'Man from Mayfair',
            '(?:la sup[ée]ri(?:eu|ue)re? |)dulci tobacco': 'La Supérieure Dulci Tobacco',
            'jamestow?n gent(?:le|el)m[ae]n': 'Jamestown Gentleman',
            'pasteur' + _apostrophe + 's alchemy': 'Pasteur\'s Alchemy',
            'n[oi]ce d[ie] coc[co]o': 'Noce di Cocco',
            'bare siero': 'Unscented',
            'tim+erman+': 'Timmermann',
            'king of bourbon': 'King of Bourbon',
            'fern concerto(?: \\(?mentholated\\)?|)': 'Fern Concerto',
            'king of Oud': 'King of Oud',
            'lav sublime concerto': 'Lav Sublime Concerto',
            'lav sublime': 'Lav Sublime',
        },
        lowpatterns={
            'eroe': 'Eroe',
            'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
            'y/r/p': 'Yuzu/Rose/Patchouli',
            'bare(?: naked|)': 'Unscented',
            'kob': 'King of Bourbon',
            'iced tea': 'Iced Tea',
        },
        bases=[ 'bufala', 'siero', 'vegan' ]
    ),

    'Wickham Soap Co.': Sniffer(
        patterns={
            'parma violet': 'Parma Violet',
            'ninfeo di egeria': 'Ninfeo di Egeria',
        },
        lowpatterns={
            'scottish heather': 'Scottish Heather',
            'magnum': 'Magnum',
            'english rose': 'English Rose',
            'cashmere': 'Cashmere',
            'irish fern': 'Irish Fern',
            'club cola': 'Club Cola',
            'unscented': 'Unscented',
        },
        bases=[ '1912', 'super smooth' ]
    ),

    'Wild West Shaving Co.': Sniffer(
        patterns={
            'aces' + _any_and + 'eights': 'Aces & Eights',
            'the outlaw': 'The Outlaw',
            'Yippie Ki-Yay': 'Yippie Ki-Yay',
        }
    ),

    'Wilkinson Sword': Sniffer(
        lowpatterns={
            'stick': 'Stick', # stick said to have a different scent
            '(?:blue +|in +|)bowl': 'Bowl', # I think bowls are all the same
        }
    ),

    'Williams Mug Soap': Sniffer(
        default_scent='Williams Mug Soap'
    ),

    'YRFCE': Sniffer(
        patterns={
            'yard raised fresh chicken eggs': 'Yard Raised Fresh Chicken Eggs',
        },
        lowpatterns={
            'yrfce': 'Yard Raised Fresh Chicken Eggs',
        }
    ),

    'Zingari Man': Sniffer(
        patterns={
            'nocturne': 'Nocturne',
        },
        lowpatterns={
            '(?:number|no\.?|num\.?|#|)\\s*1\\b': 'No. 1',
            '(?:the |)socialite': 'The Socialite',
            '(?:the |)watchm[ae]n': 'The Watchman',
            '(?:the |)blacksmith': 'The Blacksmith',
            '(?:the |)soloist': 'The Soloist',
            '(?:the |)wa[nm]derer': 'The Wanderer',
            '(?:the |)nomad': 'The Nomad',
            '(?:the |)duo': 'The Duo',
            '(?:the |)explorer': 'The Explorer',
            '(?:the |)magician': 'The Magician',
            '(?:the |)essentials': 'The Essentials',
            '(?:the |)healers': 'The Healers',
            '(?:the |)merchant': 'The Merchant',
        },
        bases=[ 'sego shaving soap', 'sego', 'vegan' ]
    ),
}

def _add_unique( name_dict: dict ):
    global _unique_names
    for name in name_dict:
        if name not in _unique_names:
            _unique_names[name] = 1
        else:
            _unique_names[name] += 1


def _compile_all():
    global _compiled_pats, _unique_names
    if _compiled_pats is not None:
        return
    _compiled_pats = { }
    for maker in _scent_pats:
        if isinstance(_scent_pats[maker], Sniffer):
            _compiled_pats[maker] = _scent_pats[maker]
            _compiled_pats[maker].makername = maker
        else:
            map = _scent_pats[maker]
            if len(map) == 0:
                continue
            comp = { }
            isonames = { }
            for pattern in map:
                comp[re.compile(_prefix + pattern + _suffix, re.IGNORECASE)] = map[pattern]
                isonames[map[pattern]] = 1
            _compiled_pats[maker] = comp
            _add_unique(isonames)


def _isUniqueScent( name: str ):
    if not _unique_names:
        raise Exception("_unique_names not complete!")
    return name in _unique_names and _unique_names[name] == 1


def match_scent( maker, scent ):
    """ Attempts to match a scent name.  If successful, a dict is returned with the
        following elements:
            'match': the result object from Pattern.match(), may be None
            'name': the standard scent name
        Otherwise None is returned.
    """
    _compile_all()
    if maker not in _compiled_pats:
        return None
    so = _compiled_pats[maker]
    if not isinstance(so, Sniffer):
        raise Exception(f"Maker '{maker}' not Sniffer!")
    result = so.match_on_maker(scent)
    if result:
        result = so.custom(result)
        return result
    nobase = so.strip_base(scent)
    if nobase != scent:
        result = so.match_on_maker(nobase)
        if result:
            result = so.custom(result)
            return result

    # TODO even when base not present, we eventually
    # want to run custom code, but we need to return to
    # the caller here... rethink how this works
    if nobase == scent:
        return None
    result = {
            'match': None,
            'maker': maker,
            'scent': title_case(nobase),
            'lather': None,
            'search': False
        }
    return so.custom(result)


def findAnyScent( text ):
    _compile_all()
    best = None
    for maker in _compiled_pats:
        so = _compiled_pats[maker]
        if not isinstance(so, Sniffer):
            raise Exception(f"Maker '{maker}' is not Sniffer!")
        result = _internal_find(text, maker, so.highpatterns, best)
        if result:
            best = so.custom(result)

    return best


def _internal_find( text: str, maker: str, patterndict: dict, best: dict ):
    if len(patterndict) < 2:
        # don't do single scents for now
        return None
    bestlen = 0
    if best:
        bestlen = best['match'].end() - best['match'].start()
    for pattern in patterndict:
        if (pattern.match('') or pattern.match('cream') or pattern.match('soap')
                or _simple_cream_soap_pat.match(patterndict[pattern])):
            # simple cream/soap; not valid for scent-first match
            # TODO uniqueness test
            continue
        result = pattern.match(text)
        if result and (not best
                or result.start() < best['match'].start()
                or (result.end() - result.start() > bestlen)):
            bestlen = result.end() - result.start()
            best = {
                'match': result,
                'scent': patterndict[pattern],
                'maker': maker,
                'lather': text,
                'search': False
            }
        elif not best or (best and best['search']):
            is_unique = _unique_names[patterndict[pattern]] == 1
            result = pattern.search(text)
            if result and (not best
                    or (is_unique and result.start() < best['match'].start())
                    or (result.end() - result.start() > bestlen)):
                bestlen = result.end() - result.start()
                best = {
                    'match': result,
                    'scent': patterndict[pattern],
                    'maker': maker,
                    'lather': text,
                    'search': True
                }
    return best

def isSingleScent( maker ):
    """
    Indicates if only one single scent is known for this maker.
    """
    _compile_all()
    if not maker or maker not in _compiled_pats:
        return False
    so = _compiled_pats[maker]
    if isinstance(so, Sniffer):
        return so.is_single_scent()
    return len(so) == 1

def getSingleScent( maker ):
    """
    If only one single scent is known for this maker, its name is returned.
    Otherwise None is returned.
    """
    _compile_all()
    if maker not in _compiled_pats:
        return
    so = _compiled_pats[maker]
    if isinstance(so, Sniffer):
        if so.is_single_scent():
            return so.get_default_scent()
    elif len(so) == 1:
        for x in so:
            return so[x]
    return None


not_cap_pattern = re.compile('(?:a|the|and|y|into|in|of|on|for|from|at|to|as|so|s|la|le|l|n|de|di|los|da)$', re.IGNORECASE)

def title_case( text: str ):
    tctext = ''
    pos = 0
    inword = len(text) > 0 and str.isalpha(text[0])
    text = text.replace('&#39;', "'").replace('&amp;', '&')
    # recognize ALL CAPS STRING AS DISTINCT from distinct WORDS in all caps
    # however a short single word could be an acronym
    allcaps = str.isupper(text)
    if allcaps and len(text) < 6 and text.find(' ') < 0:
        return text
    for i in range(1, len(text) + 1):
        if i == len(text):
            nextword = not inword
        else:
            nextword = str.isalpha(text[i])
        if nextword != inword:
            # TODO: pos=0, i.e. first word, makes this word a candidate,
            # but capword will be false because it is usually capitalized.
            # So why is pos==0 checked in the first branch?  After removing `and capword` from the
            # second branch, I had to add the `pos > 0` to get this to work... need to review when
            # I feel like spending more time thinking this through.
            candidate = inword and (pos == 0 or (text[pos - 1].isspace()))
            capword = allcaps or not text[pos].isupper()
            if candidate and capword and (pos == 0 or not not_cap_pattern.match(text, pos, i)):
                tctext += text[pos].upper() + text[pos + 1:i].lower()
            elif candidate and not_cap_pattern.match(text, pos, i) and pos > 0:
                tctext += text[pos:i].lower()
            else:
                tctext += text[pos:i]
            pos = i
            inword = nextword
    return tctext


