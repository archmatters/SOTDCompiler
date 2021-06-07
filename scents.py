#!/usr/bin/env python3

import re

_simple_cream_soap_pat = re.compile('^(?:shav(?:ing|e) |)(?:soap|cream)$')
_any_pattern = re.compile('.*')

_apostrophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'
_prefix = '\\b'
_suffix = '\\b[\\.,]?'

_unique_names = { }

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
            self.custom = None
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
                        '\\s*(?:\\(' + bpat + '\\)|(?:in |[:,\\-]\\s*)' + bpat
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
            if stripped:
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
            return { 'match': result, 'name': self.get_default_scent() }

        for pattern in self.highpatterns:
            result = pattern.match(text)
            if not result:
                result = pattern.search(text)
            if result:
                return { 'match': result, 'name': self.highpatterns[pattern] }
                
        for pattern in self.lowpatterns:
            result = pattern.match(text)
            if result:
                return { 'match': result, 'name': self.lowpatterns[pattern] }
        for pattern in self.lowpatterns:
            result = pattern.search(text)
            if result:
                return { 'match': result, 'name': self.lowpatterns[pattern] }
                
        return None
    

    # will not use low confidence patterns
    # return { 'maker': 'Maker Name', 'scent': 'Scent Name', 'lather': 'Lather text' }
    def match_unknown( self, full_text: str ):
        return None

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

    'Acqua di Parma': Sniffer(
        patterns={
            'barbiere crema soffice (?:da pen+el+o|)': 'Barbiere',
            'Collezione Barbiere': 'Barbiere',
        },
        lowpatterns={
            'barbiere': 'Barbiere',
        }
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
        },
        lowpatterns={
            'nightcrawler': 'Nostalgic Nightcrawler',
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
        # TODO how to handle Kaiz[ea]n, which is both base and soap name?
        patterns={
            'st\\.? bart' + _apostrophe + 's': 'St. Barts',
            'peach(?:es|)' + _any_and + 'cognac': 'Peach & Cognac',
            'peach(?:es|) cognac': 'Peach & Cognac',
            'which one' + _apostrophe + 's pink\\??': 'Which One\'s Pink?',
            'grecian(?: horse|)': 'Grecian Horse',
            '\\(?\\s*little fictions\\s*\\)?(?:' + _any_and + 'gr[ea]y matter|)': 'Little Fictions',
            'vanille de tabac': 'Vanille de Tabac',
            'asian plum': 'Asian Plum',
            'asian pear': 'Asian Pear',
            'cannablis+ santal': 'Cannabliss Santal',
            'barbiere sofistic[as]to': 'Barbiere Sofisticato',
            'Sofistacato Barbiere': 'Barbiere Sofisticato',
            'pedro fiasco': 'Pedro Fiasco',
            'l' + _apostrophe + 'orange verte': 'l\'Orange Verte',
            # The Club brand
            'charlatan' + _apostrophe + 's traipse': 'Charlatans Traipse',
            'warrior of (?:the |)howling fjord': 'Warrior of Howling Fjord',
            'fruits? de la passione?': 'Fruit de la Passion',
            'vanill[ea] vendetta': 'Vanille Vendetta',
        },
        lowpatterns={
            'spartacus': 'Spartacus',
            'socal hipster': 'SoCal Hipster',
            '(?:skin essentials |)shav(?:ing|e) butter': 'Shaving Butter',
            'chasing the dragon': 'Chasing the Dragon',
            'strawberry fields': 'Strawberry Fields',
            'forb+id+en fruit': 'Forbidden Fruit',
            # The Club brand
            'the kingdom': 'The Kingdom',
            'el gaucho': 'El Gaucho',
            'howling fjord': 'Warrior of Howling Fjord',
        },
        bases=[ 'kaizen', 'k2', 'vegan' ]
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

    'Arran': {},

    'Australian Private Reserve': {
        'raconteur': 'Raconteur',
        'foug[èeé]re trois': 'Fougère Trois',
        'la\\s*violet+a': 'Lavioletta',
        # TODO special rules for Carnivale and Fresca Intensa
        # which are made under the Storybook Soapworks brand
    },

    'Aveeno': {
        'positively smooth (?:shave |)gel': 'Positively Smooth',
        'ther[ae]pe?utic (?:shave |)gel': 'Therapeutic',
    },

    'Barbasol': Sniffer(
        patterns={
            'pacific rush': 'Pacific Rush',
        },
        lowpatterns={
            'original': 'Original',
            'sensitive': 'Sensitive Skin',
            'soothing aloe\\b': 'Soothing Aloe',
            'extra moisturizing': 'Extra Moisturizing',
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
            'eigengrau': 'Eigengrau',
            '[\\w\\s]*grande? chypre.*': 'Le Grand Chypre',
            'dickens,?\\s+revisited': 'Dickens, Revisited',
            'oh?' + _apostrophe + ',?\\s*delight': 'O, Delight!',
            'brew?(?:-| |)ha[\\- ]?ha': 'Brew Ha-Ha',
            'hallows?': 'Hallows',
            'paganini' + _apostrophe + 's violin': 'Paganini\'s Violin',
            'levian?than': 'Leviathan',
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
            # latha
            'osmanthus': 'Osmanthus',
            'latha taiga': 'Taiga',
            'latha original': 'Latha Original',
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
        },
        # TODO probably need to specifically identify "Latha Original" as "Latha"
        bases=[ 'latha', 'soft heart series', 'soft(?:ish|)(?:-|\\s*)hearts?', 'SH',
                'excelsior', 'glissant', 'reserve', 'pp8' ]
    ),

    'BAUME.BE': Sniffer(
        lowpatterns={
            '(?:shaving |)soap': 'Soap',
            '(?:shaving |)cream': 'Cream'
        }
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
            'cap' + _apostrophe + 'n darkside': 'Cap\'n Darkside',
            '(?:7|seven) doubloons': '7 Doubloons',
        },
        lowpatterns={
            'captain' + _apostrophe + 's choice': 'Captain\'s Choice',
            'captain' + _apostrophe + 's reserve': 'Captain\'s Reserve',
            'l[ae] concorde?': 'La Concorde',
            'siren' + _apostrophe + 's? song': 'Siren\'s Song',
        }
    ),

    'The Bluebeards Revenge': { '(?:shaving |)cream': 'Shaving Cream' },

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
            'm[éeè]nage (?:à|a|á|de) lavande': 'Ménage à Lavande',
            'Blug[èeé]re': 'Blugère',
            'vintage (?:for |)(?:serf|s\\.e\\.r\\.f\\.)': 'Vintage S.E.R.F.',
        },
        lowpatterns={
            'cool' + _any_and + 'fresh': 'Cool and Fresh',
            'June 2019 Maggard' + _apostrophe + 's? Meetup': 'Maggard Razors 2019 Meetup',
            'Maggard Meetup 2019': 'Maggard Razors 2019 Meetup',
            'Maggard Razors 2019 Meetup': 'Maggard Razors 2019 Meetup',
        },
        bases=[ 'luxury cream soap', 'luxury shaving soap' ]
    ),

    'CBL Soaps': Sniffer(
        patterns={
            'lavender' + _any_and + 'leather': 'Lavender & Leather',
            't[ao]bacaveg': 'Tabacaveg',
        },
        lowpatterns={
            'peanut butter': 'Peanut Butter',
            'outlaw': 'Outlaw',
        }
    ),

    'Cella': Sniffer(
        lowpatterns={
            '(?:cella |)crema sapone': 'Cella',
            '(?:cella |milano |)crema d[ae] barba': 'Cella',
            'aloe vera': 'Bio/Aloe Vera',
            'bio': 'Bio/Aloe Vera',
            'soap': 'Cella',
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

    'Chicago Grooming Co.': Sniffer(
        patterns={
            'montrose beach': 'Montrose Beach',
            'new city:? back of the yards': 'New City Back of the Yards',
        },
        lowpatterns={
            'ex?cursion': 'Excursion',
            'no\\. 11': 'No. 11',
            'new city': 'New City Back of the Yards',
        }
    ),

    'Chiseled Face': Sniffer(
        patterns={
            'ghost\\s*town barber': 'Ghost Town Barber',
            'midnight stag': 'Midnight Stag',
            'cryogen': 'Cryogen',
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

    'Clubman Pinaud': Sniffer(
        default_scent='Clubman Pinaud'
    ),

    'Cold River Soap Works': Sniffer(
        patterns={
            'madman' + _apostrophe + 's bouquet': 'Madman\'s Bouquet',
            'prato verde': 'Prato Verde',
            'jardin d' + _apostrophe + 'orange': 'Jardin d\'Orange',
            'lav[ae]ndula bl(?:eu|ue)': 'Lavandula Bleu',
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
            'l[ae] petite? prai?rie': 'La Petite Prairie',
            'sunrise on lasalle': 'Sunrise on LaSalle',
            'tsm foug[èeé]re': 'TSM Fougère',
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
            'darkfall': 'Darkfall',
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
        },
        bases=[ 'vol. 2', 'vol. 3' ]
    ),

    'Dr K Soap Company': Sniffer(
        lowpatterns={
            'peppermint': 'Peppermint',
            'lime': 'Lime',
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
        }
    ),

    'ETHOS': Sniffer(
        patterns={
            'melange d' + _apostrophe + 'agrumes': 'Melange d\'Agrumes',
            'succ[èeé]s+': 'Succès',
        }
    ),

    'Eufros': Sniffer(
        patterns={
            'dam[ae]s? de noche': 'Dama de Noche',
            'rosa[ \\-]oud': 'Rosa-Oud',
            'vetiver de hait[íi]': 'Vetiver de Haití',
            'Barakah Oudh': 'Barakah Oudh',
            # this is not actually under the Eufros brand... should this be split off?
            # or... should all Eufros soaps be identified as "JabonMan?"
            'mediterr[áa]no l\\.e\\. bullgoose': 'Mediterráneo',
            'mediterr[áa]ne?o': 'Mediterráneo',
        },
        lowpatterns={
            'ylang[ \\-]ylang': 'Ylang Ylang',
            'Gea': 'Gea',
            'Tobacco': 'Tobacco',
        }
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
            'motherfu?cker': 'Motherfucker',
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

    'Gentleman\'s Nod': Sniffer(
        patterns={
            'kanpai': 'Kanpai'
        },
        lowpatterns={
            'zaharoff': 'Zaharoff Signature',
            'no. 85': 'Ernest',
            'no. 01': 'George',
            'no. 42': 'Jackie',
            'no. 13': 'Johnny',
            'no. 11': 'Vincent',
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
            'tallow no?. 1': 'N. 1',
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

    'Haslinger': Sniffer(
        patterns={
            'salbei': 'Salbei',
            'sch?afmilch': 'Schafmilch',
            'sandelholt?z': 'Sandelholz',
        },
        lowpatterns={
            'aloe vera': 'Aloe Vera',
            'sensitive?': 'Sensitiv',
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
        }
    ),

    'The Holy Black': Sniffer(
        patterns={
            'jack' + _any_and + 'ginger': 'Jack & Ginger',
            'dr\\. jekyl+' + _any_and + 'mr\\. hyde': 'Dr. Jekyll & Mr. Hyde',
        }
    ),

    'House of Mammoth': Sniffer(
        patterns={
            'santal noir': 'Santal Noir',
            'mood indigo': 'Mood Indigo',
            'almond(?:' + _any_and + '|\\s*)leather': 'Almond Leather',
        },
        lowpatterns={
            'cirrus': 'Cirrus',
            'flying squirrel': 'Cirrus',
            'restore': 'Restore',
            'stones': 'Stones',
            'indigo': 'Mood Indigo',
            'marine': 'Marine',
            'z': 'Z',
            '(?:the )tob+ac+[oa]nist': 'Tobacconist'
        },
        bases=[ 'tusk' ]
    ),

    'Hub City Soap Company': Sniffer(
        patterns={
            'aegyptus': 'Aegyptus',
            'chats? with grandpa': 'Chats with Grandpa',
            'f(?:ri|ir)day night lights': 'Friday Night Lights',
        },
        lowpatterns={
            'pages': 'Pages',
        }
    ),

    'Institut Karité': Sniffer(
        default_scent='Institut Karité'
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

    'Knightsbridge': Sniffer(
        lowpatterns={
            'aloe': 'Aloe Water',
            'bay rum': 'Bay Rum',
        }
    ),

    'Lather Jack': Sniffer(
        patterns={},
        lowpatterns={
            'bourbon' + _any_and + 'oak': 'Bourbon & Oak',
            '(?:the |)woodsy man': 'The Woodsy Man',
        }
    ),

    'Lisa\'s Natural Herbal Creations': Sniffer(
        lowpatterns={
            'doc hol+iday': 'Doc Holliday',
            '(?:irish green|green irish) tweed': 'Irish Green Tweed',
            'sandalwood' + _any_and + 'patchouli': 'Sandalwood & Patchouli',
        }
    ),

    'Los Angeles Shaving Soap Co.': Sniffer(
        patterns={
            'bespoke #1': 'Bespoke #1',
            'myrkvi[ðdo]r': 'Myrkviðr',
        }
    ),

    'Lotus Eater': Sniffer(
        patterns={
            'durga' + _apostrophe + 's companion': 'Durga’s Companion',
        },
        lowpatterns={
            'j[öo]tun*': 'Jötun',
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
        },
        bases=[ 'version 3', 'V3', 'V4' ]
    ),

    'Maggard Razors': Sniffer(
        patterns={
            'london barbershop': 'London Barbershop',
            'mango sage tea': 'Mango Sage Tea',
            'northern moss': 'Northern Moss',
        },
        lowpatterns={
            'limes' + _any_and + 'bergamot': 'Limes & Bergamot',
            'tobacco' + _any_and + 'leather': 'Tobacco & Leather',
            'lilac': 'Lilac',
            'orange menthol': 'Orange Menthol',
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
        },
        lowpatterns={
            'reuniou?n': 'Réunion',
            'lu' + _apostrophe + 'au': 'Lu\'au',
            'j[ūu]rat[ėe]': 'Jūratė',
            'pant(?:ie|y) dropper': 'Pantie Dropper',
            'jefferson (?:square|street)': 'Jefferson Square',
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
            'amaretto e?speciale?': 'Amaretto Speciale',
            'union': 'Union',
        }
    ),

    'Murphy and McNeil': Sniffer(
        patterns={
            'nantahala': 'Nantahala',
            'tobac fanaile': 'Tobac Fanaile',
            'gael luc': 'Gael Luc',
            'triskele': 'Triskele',
            'magh tured': 'Magh Tured',
            'ogham stone': 'Ogham Stone',
            'cat sid+he': 'Cat Sidhe'
        },
        lowpatterns={
            'bdlm': 'Barbershop de los Muertos',
            'st\\.? james': 'St. James',
        },
        bases=[ 'sl[aá]inte', 'aon', 'kodiak' ]
    ),

    'Mystic Water Soap': Sniffer(
        lowpatterns={
            'bay rum': 'Bay Rum',
            'Brown Windsor': 'Brown Windsor',
            'irish travel+er': 'Irish Traveller',
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
        }
        # TODO No. 63 w/o maker matches like NO - 63 - Soap
        # Also "No. 1 - Zingari"
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

    'Ogallala Bay Rum': {
        'sage,?' + _any_and + 'cedar': 'Bay Rum, Sage & Cedar',
        'limes,?' + _any_and + 'peppercorn': 'Bay Rum, Limes & Peppercorn',
        _any_and + 'sweet orange': 'Bay Rum & Sweet Orange',
        _any_and + 'vanilla': 'Bay Rum & Vanilla',
        # TODO '\\s*$': 'Bay Rum',
    },

    'Old Spice': {},

    'Opus Ruri': Sniffer(
        patterns={
            'la salvia 4': 'Una Salvia 4',
            'la salvia': 'Una Salvia',
        }
    ),

    'P.160': Sniffer(
        patterns={
            'tipo morbido': 'Tipo Morbido',
            'tipo duro': 'Tipo Duro',
        }
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
            'nu[àa]via blue?': 'Nuàvia Blu',
            'nu[àa]via (?:rossa?|red)': 'Nuàvia Rossa',
            'nu[àa]via nema': 'Nuàvia Nema',
            'nu[àa]via (?:verde|green)': 'Nuàvia Verde',
        },
        lowpatterns={
            'namaste': 'Namaste',
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

    'Le Père Lucien': Sniffer(
        patterns={
            'cologne[\\-\\s]*foug[èeé]re': 'Cologne-Fougère',
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
            'doppelg[äa]nger grey': 'Doppelgänger Grey',
            'doppelg[äa]nger black': 'Doppelgänger Black',
            'doppelg[äa]nger orange': 'Doppelgänger Orange',
            'doppelg[äa]nger ox blood': 'Doppelgänger Ox Blood',
        },
        lowpatterns={
            'cad': 'CaD',
            'esp\\b': 'ESP',
            'cavendish': 'Cavendish',
            'lo[ \\-]haiku': 'Lo-Haiku',
            'spring[\\- ]heeled jack': 'Spring-Heeled Jack',
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
         # looks like only black has been made as shaving soap
         # but they have many other scents as bath soaps
         default_scent='Black'
    ),

    'Pré de Provence': Sniffer(
        patterns={
            '(?:number|no\.?|num\.?|#|)\\s*63': 'No. 63',
        },
        lowpatterns={
            'bergamot' + _any_and + 'thyme': 'Bergamot and Thyme',
            'original': 'Original',
        },
        default_scent='Original'
    ),

    'Proraso': Sniffer(
        patterns={
            '(?:white |)green tea' + _any_and + 'oat': 'Green Tea & Oatmeal',
            'red sandalwood': 'Sandalwood',
            '(?:green |)menthol' + _any_and + 'eucalyptus': 'Menthol & Eucalyptus',
            'eucalyptus(?: oil|)' + _any_and + 'menthol': 'Menthol & Eucalyptus',
            'aloe' + _any_and + 'vitamin e': 'Aloe & Vitamin E',
        },
        lowpatterns={
            'green': 'Menthol & Eucalyptus',
            'red': 'Sandalwood',
            'white': 'Green Tea & Oatmeal',
            'blue': 'Aloe & Vitamin E',
            'sandalwood': 'Sandalwood',
        }
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
            'mudder focker': 'Mudder Focker',
        },
        lowpatterns={
            'blue\\s*': 'Blue Barbershop',
            'lime': 'Essential Oil of Lime',
            'black label': 'What the Puck?! Black Label',
            # TODO inconsistent name?
            'blue label': 'Blue Barbershop',
            'p\\.?\\s*160': 'P.160',
            'xxx': 'XXX',
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
            'Frankincense, Anise' + _any_and + 'Orange': 'Pan de Muerto',
        },
        lowpatterns={
            'cedar[^\w]+lime': 'Cedar-Lime',
            '(?:1920 |)barbershop': 'Barbershop 1920',
            'sand(?:al|le)woods?' + _any_and + 'bourbon': 'Sandalwood & Bourbon',
            'bourbon(?:' + _any_and + '|\\s+)sand(?:al|le)wood': 'Sandalwood & Bourbon',
        },
    ),

    'Saponificio Varesino': Sniffer(
        patterns={
            'cub+eb+e': 'Cubebe',
            'opuntia': 'Opuntia',
            'Settantesimo Anniversario': '70th Anniversary',
        },
        lowpatterns={
            'cosmo': 'Cosmo',
            '70th anniver?sary': '70th Anniversary',
            'desert ver?tiver': 'Desert Vetiver',
            'dolomiti': 'Dolomiti',
        },
        bases=[ 'beta 4.1', 'beta 4.2', 'beta 4.3', 'beta' ]
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

    'The Soap Exchange': Sniffer(
        lowpatterns={
            'barbershop': 'Barbershop',
            'sandalwood(?:' + _any_and + '|)vanilla': 'Sandalwood Vanilla',
        }
    ),

    'Southern Witchcrafts': Sniffer(
        patterns={
            'grave\\s*fruit': 'Gravefruit',
            'desa?ia?rology': 'Desairology',
            'anthropophagy': 'Anthropophagy',
            'valley of ashes': 'Valley of Ashes',
            'ne[ck]romanti[ck]': 'Necromantic',
            'druantia': 'Druantia',
            'p[oa]mona': 'Pomona',
            'tres matres': 'Tres Matres',
            'Grey Phetiver': 'Grey Phetiver',
            'Lycanthropy': 'Lycanthropy',
            'foug[eèé]re n[ea]m[ea]ta': 'Fougere Nemeta',
            'gr[ea]y phetiver': 'Grey Phetiver',
        },
        lowpatterns={
            'cedar': 'Cedar',
            'autum[nm]? ash': 'Autumn Ash',
            'samhain': 'Samhain',
            'voa': 'Valley of Ashes',
        }
    ),

    'Spartium Natural Cosmetics': {
        # TODO Meštar
    },

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
            'Phara?oa?h?' + _apostrophe + 's Dreamsc?ick?le': 'Pharaoh\'s Dreamsicle',
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
            'vanilla sandalwood$': 'Vanilla Sandalwood'
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
        },
        bases=[ 'mutton', 'mutton tallow', 'glacial' ]
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
            'Mountain Laurel': 'Mountain Laurel',
        },
        lowpatterns={
            'roty': 'ROTY 2020', # K1986
        }
    ),

    'Tabac': Sniffer(
        default_scent='Original'
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
        },
        lowpatterns={
            'rf': 'Royal Forest',
        }
    ),

    'Tcheon Fung Sing': Sniffer(
        patterns={
            'shave' + _any_and + 'roses rosehip': 'Shave & Roses Rosehip',
            'shave' + _any_and + 'roses dracaris': 'Shave & Roses Dracaris',
            # lineo intenso
            '(?:Aroma Intenso |)arancia amaro': 'Arancia Amaro',
        },
        lowpatterns={
            'diVino': 'diVino',
            # lineo intenso
            'bergamotto neroli': 'Bergamotto Neroli',
            'crazy sandalwood': 'Crazy Sandalwood',
        }
    ),

    '345 Soap Co.': Sniffer(
        lowpatterns={
            'white buffalo': 'White Buffalo',
            'shark b(?:ite|ait)': 'Shark Bite',
        }
    ),

    'La Toja': Sniffer(
        default_scent='La Toja',
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
            'S with sandalwood oil': 'Turmeric S with Sandalwood Oil'
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
            'pear-brr+ shoppe': 'Pear-Brrr Shoppe',
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

    'Wet Shaving Products': Sniffer(
        lowpatterns={
            'gaelic tweed': 'Gaelic Tweed',
            'mahogany': 'Mahogany',
            'tobacco': 'Tobacco',
            'ol' + _apostrophe + 'kentucky': 'Ol\' Kentucky',
        },
        bases=[ 'Formula T', 'Rustic' ]
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
            'tim+erman+': 'Timmermann'
        },
        lowpatterns={
            'eroe': 'Eroe',
            'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
            'y/r/p': 'Yuzu/Rose/Patchouli',
            'bare(?: naked|)': 'Unscented',
        },
        bases=[ 'bufala', 'siero' ]
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

    'Williams Mug Soap': Sniffer(
        default_scent='Williams Mug Soap'
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
            '(?:the |)wanderer': 'The Wanderer',
            '(?:the |)nomad': 'The Nomad',
            '(?:the |)duo': 'The Duo',
            '(?:the |)explorer': 'The Explorer',
            '(?:the |)magician': 'The Magician',
            '(?:the |)essentials': 'The Essentials',
            '(?:the |)healers': 'The Healers',
            '(?:the |)merchant': 'The Merchant',
        },
        bases=[ 'sego shaving soap', 'sego' ]
    ),
}

_compiled_pats = None

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
    if isinstance(so, Sniffer):
        result = so.match_on_maker(scent)
        if result:
            return result
        nobase = so.strip_base(scent)
        if nobase == scent:
            return None
        return { 'match': None, 'name': title_case(nobase) }
    else:
        for pattern in so:
            result = pattern.match(scent)
            if result:
                return { 'match': result, 'name': _compiled_pats[maker][pattern] }
    return None


def findAnyScent( text ):
    _compile_all()
    best = None
    for maker in _compiled_pats:
        so = _compiled_pats[maker]
        if isinstance(so, Sniffer):
            result = _internal_find(text, maker, so.highpatterns, best)
        else:
            result = _internal_find(text, maker, so, best)
        if result:
            best = result

    return best


def _internal_find( text: str, maker: str, patterndict: dict, best: dict ):
    if len(patterndict) < 2:
        # don't do single scents for now
        return None
    bestlen = 0
    if best:
        bestlen = best['result'].end() - best['result'].start()
    for pattern in patterndict:
        if (pattern.match('') or pattern.match('cream') or pattern.match('soap')
                or _simple_cream_soap_pat.match(patterndict[pattern])):
            # simple cream/soap; not valid for scent-first match
            # TODO uniqueness test
            continue
        result = pattern.match(text)
        if result and (not best
                or result.start() < best['result'].start()
                or (result.end() - result.start() > bestlen)):
            best = {
                'result': result,
                'scent': patterndict[pattern],
                'maker': maker,
                'lather': text,
                'search': False
            }
        elif not best or (best and best['search']):
            is_unique = _unique_names[patterndict[pattern]] == 1
            result = pattern.search(text)
            if result and (not best
                    or (is_unique and result.start() < best['result'].start())
                    or (result.end() - result.start() > bestlen)):
                best = {
                    'result': result,
                    'scent': patterndict[pattern],
                    'maker': maker,
                    'lather': text,
                    'search': True
                }
    return best


def getSingleScent( maker ):
    """ If only one single scent is known for this maker, its name is returned.
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


not_cap_pattern = re.compile('(?:a|the|and|y|into|in|of|on|for|from|at|to|as|so|s|la|le|l|n|de|di|los)$', re.IGNORECASE)

def title_case( text: str ):
    tctext = ''
    pos = 0
    inword = len(text) > 0 and str.isalpha(text[0])
    text = text.replace('&#39;', "'")
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


