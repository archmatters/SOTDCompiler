#!/usr/bin/env python3

import re

_simple_cream_soap_pat = re.compile('^(?:shav(?:ing|e) |)(?:soap|cream)$')

_apostophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'
_ending = '[\\.,]?'

_scent_pats = {
    'Abbate y la Mantia': {
        'krokos$': 'Krokos',
        'crumiro$': 'Crumiro',
        'matteo$': 'Matteo 9,11',
        'garibaldi$': 'Garibaldi',
        'monet$': 'Monet',
        'buttero$': 'Buttero'
    },

    'Acqua di Parma': {},

    'Apex Alchemy Soaps': {
        'American Pi': 'American Pi',
        'Nightcrawler': 'Nightcrawler',
        'alchemical romance': 'Alchemical Romance',
    },

    'Archaic Alchemy': {
        '^agave$': 'Agave',
        '^mictlan$': 'Mictlan',
    },

    'Ariana & Evans': {
        # TODO how to handle Kaizen, which is both base and soap name?
        'st\\.? bart' + _apostophe + 's': 'St. Barts',
        'peach(?:es|)' + _any_and + 'cognac': 'Peach & Cognac',
        'which one' + _apostophe + 's pink\\??': 'Which One\'s Pink?',
        'grecian horse': 'Grecian Horse',
        'spartacus': 'Spartacus',
        '\\(?\\s*little fictions\\s*\\)?(?:' + _any_and + 'gr[ea]y matter|)': 'Little Fictions',
        'vanille de tabac': 'Vanille de Tabac',
        'socal hipster': 'SoCal Hipster',
        '(?:skin essentials |)shav(?:ing|e) butter': 'Shaving Butter',
        'asian plum': 'Asian Plum',
        'asian pear': 'Asian Pear',
        'cannabliss santal': 'Cannabliss Santal',
        'barbiere sofisticato': 'Barbiere Sofisticato',
        'pedro fiasco': 'Pedro Fiasco',
        'chasing the dragon': 'Chasing the Dragon',
        'l' + _apostophe + 'orange verte': 'l\'Orange Verte',
        '^strawberry fields$': 'Strawberry Fields',
        # The Club brand
        'the kingdom': 'The Kingdom',
        'charlatan' + _apostophe + 's traipse': 'Charlatans Traipse',
        'el gaucho$': 'El Gaucho',
    },

    'Arko': { '': 'Arko' },

    'Art of Shaving': {},

    'Arran': {},

    'Australian Private Reserve': {
        'raconteur': 'Raconteur',
        'foug[èeé]re trois': 'Fougère Trois',
        # TODO special rules for Carnivale and Fresca Intensa
    },

    'Barbasol': {
        '\\s$': 'Cream',
        'soothing aloe\\b': 'Soothing Aloe',
    },

    'Barbus': {
        # TODO '\\s*$': 'Classic',
        'classic': 'Classic',
        'active': 'Active',
    },

    'Barrister and Mann': {
        'seville': 'Seville',
        'eigengrau': 'Eigengrau',
        '[\\w\\s]*grande? chypre.*': 'Le Grand Chypre',
        'dickens,?\\s+revis': 'Dickens, Revisited',
        'oh?' + _apostophe + ',?\\s*delight': 'O, Delight!',
        'brew?[\\- ]ha': 'Brew Ha-Ha',
        'hallow': 'Hallows',
        'paganini': 'Paganini\'s Violin',
        'levian?than': 'Leviathan',
        'beaudelaire': 'Beaudelaire',
        'foug[èeé]re gothi': 'Fougère Gothique',
        'foug[èeé]re angel': 'Fougère Angelique',
        'behold the whatsis!?': 'Behold the Whatsis!',
        'dfs (?:2017|exclusive)': 'DFS 2017 LE',
        'le grand (?:cyphre|chypre)': 'Le Grand Chypre',
        '(?:motherfuckin(?:\'|g)|mf) roam': 'Roam',
        'lavanille': 'Lavanille',
        'first snow': 'First Snow',
        # reserve
        'waves$': 'Reserve Waves',
        'spice(?: reserve(?: base|)|)$': 'Reserve Spice',
        'fern$': 'Reserve Fern',
        'lavender$': 'Reserve Lavender',
        'cool(?: reserve(?: base|)|)$': 'Reserve Cool',
        'classic$': 'Reserve Classic',
        # latha?
        'latha osmanthus': 'Latha Osmanthus',
        'latha taiga': 'Latha Taiga',
    },

    'BAUME.BE': {
        '(?:shaving |)soap': 'Soap',
        '(?:shaving |)cream': 'Cream'
    },
    
    'Black Ship Grooming Co.': {
        'captain' + _apostophe + 's choice': 'Captain\'s Choice',
        'captain' + _apostophe + 's reserve': 'Captain\'s Reserve',
        'calypso' + _apostophe + 's curse': 'Calypso\'s Curse',
        'cap' + _apostophe + 'n darkside': 'Cap\'n Darkside',
    },

    'The Bluebeards Revenge': { '(?:shaving |)cream': 'Shaving Cream' },

    'Brutalt Bra Barbersåpe': {
        'tsn le\\s*/\\s*norwegian wood': 'Norwegian Wood',
        'original': 'Original',
        'spruce': 'Norwegian Spruce',
    },

    'Bufflehead': {
        'Islamorada': 'Islamorada',
        'Mannish Boy': 'Mannish Boy',
        'North York': 'North York',
    },

    'C.O. Bigelow': {},

    'Captain\'s Choice': {},

    'Castle Forbes': {},

    'Catie\'s Bubbles': {
        'mile high menthol': 'Mile High Menthol',
        'porch drinks': 'Porch Drinks',
        'a midnight dreary': 'A Midnight Dreary',
        'pine barrens': 'Pine Barrens',
        'un jour gris': 'Un Jour Gris',
        'tonsorial parlour': 'Tonsorial Parlour',
        'le march[ée] du rasage': 'Le Marché du Rasage',
        'm[ée]nage (?:à|a|á|de) lavande': 'Ménage à Lavande',
    },

    'CBL Soaps': {
        'peanut butter': 'Peanut Butter',
        'lavenderleather': 'Lavender & Leather',
        '^outlaw$': 'Outlaw',
    },

    'Cella': {
        '[\w ]+aloe vera': 'Aloe Vera cream',
        '(?:cella |)crema sapone': 'Cream soap',
        '(?:cella |milano |)crema d[ae] barba': 'Cream',
        'soap': 'Cream soap',
        '$': 'Cream soap',
    },

    'Central Texas Soaps': {
        'm[er]\\.? pepper': 'Mr. Pepper',
        'saw': 'The Saw',
        'citrus burst': 'Citrus Burst',
        'babershop': 'Grandpa\'s Barbershop',
    },

    'Chicago Grooming Co.': {
        'montrose beach': 'Montrose Beach',
        'ex?cursion': 'Excursion',
        'no\\. 11': 'No. 11',
    },

    'Chiseled Face': {
        'gtb\\b': 'Ghost Town Barber',
        'ghost\s*town barber': 'Ghost Town Barber',
        'midnight stag': 'Midnight Stag',
        'cryogen': 'Cryogen',
        'sherlock': 'Sherlock',
        'cedar' + _any_and + 'spice': 'Cedar & Spice',
        'cedar\\s+spice': 'Cedar & Spice',
    },

    'Classic Edge': {
        'aloe vera': 'Aloe Vera',
        'sandalwood': 'Sandalwood',
        'bay rum': 'Bay Rum',
        'charcoal': 'Charcoal',
        '(?:old |)barbershop': 'Old Barbershop',
    },

    'Clubman Pinaud': {
        'shave soap': 'Clubman Pinaud',
    },

    'Cold River Soap Works': {
        # TODO bases are "select", "glide", "schapenm[ei]lk", "olivi?a"
        # but at least one is also the soap name
        'madman' + _apostophe + 's bouquet': 'Madman\'s Bouquet',
        'prato verde': 'Prato Verde',
        'schapenm[ei]lk': 'Schapenmelk',
    },

    'Colgate': { '': 'Mug soap' },

    'Col. Conk': {},

    'Crabtree & Evelyn': {
        'nomad': 'Nomad',
        'lime': 'Lime',
    },

    'Cremo': {},

    'D.R. Harris': {},

    'Dalan': {
        'energetic': 'Energetic',
        'cool': 'Cool',
        'sensitive': 'Sensitive'
    },

    'Declaration Grooming': {
        '^sellout$': 'Sellout',
        '^tribute$': 'Tribute',
        '^opulence$': 'Opulence',
        'cuir et [èeé]pices': 'Cuir et Épices',
        'cygnus x': 'Cygnus X-1',
        '^hindsight$': 'Hindsight',
        'gratiot league': 'Gratiot League Square',
        '^original$': 'Original',
        'trismegistus': 'Trismegistus',
        'after the rain': 'After the Rain',
        'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
        'yrp\\b': 'Yuzu/Rose/Patchouli',
        'y/r/p\\b': 'Yuzu/Rose/Patchouli',
        '\\bmoti\\b': 'Massacre of the Innocents',
        '^massacre$': 'Massacre of the Innocents',
        'massacre of the inno': 'Massacre of the Innocents',
        'son et lumiere': 'Son et Lumiere',
        'b[\\- ?]cubed?': 'Blackberry Blossom Bay',
        '(?:b3|b³)\\b': 'Blackberry Blossom Bay',
        'lamplight penance': 'Lamplight Penance',
        'weinstra(?:ss|ß)e': 'Weinstrasse',
        '\\?$': '? (Puzzle 2019)',
        '\\? \\(puzzle 2019\\)': '? (Puzzle 2019)',
        '\\? 2019 puzzle': '? (Puzzle 2019)',
        '^day\\s*man$': 'Dayman',
        '^night\\s*man$': 'Nightman',
        'big soap energy': 'Big Soap Energy',
        '^bse$': 'Big Soap Energy',
        'Champs de Lavande': 'Champs de Lavande',
        '^darkfall$': 'Darkfall',
        'sweet lemon': 'sweet lemon',
    },

    'Dindi Naturals': { '': 'lemon myrtle, macadamia + white cypress' },

    'Dr. Jon\'s': {
        'flowers in the dark': 'Flowers in the Dark',
        'death or glory': 'Death or Glory',
        'victory or death': 'Victory or Death',
    },

    'Dr K Soap Company': {
        '^peppermint$': 'Peppermint',
        '^lime$': 'Lime',
    },

    'Edwin Jagger': {},

    'Eleven Shaving': {
        '^barbershop$': 'Barbershop',
        'olive, musk' + _any_and + 'citrus': 'Olive, Musk & Citrus',
    },

    'ETHOS': {},

    'Eufros': {
        'Dama de Noche': 'Dama de Noche',
        'Gea$': 'Gea',
        'Rosa-Oud': 'Rosa-Oud',
        'Mediterraneo': 'Mediterraneo',
        'Tobacco$': 'Tobacco',
        'Vetiver de Haiti$': 'Vetiver de Haiti',
        'Barakah Oudh$': 'Barakah Oudh',
    },

    'Executive Shaving': {
        'Citrus Kiss$': 'Citrus Kiss',
        'Fuar Ach Snog': 'Fuar Ach Snog',
        'Natural$': 'Natural',
    },

    'Extrò Cosmesi': {
        'egyptian oudh?': 'Egyptian Oudh',
        'pirata': 'Pirata',
        'frarinik': 'Frarinik',
        't[ao]bacco': 'Tabacco',
        'del don': 'Del Don',
        'freddo': 'Freddo',
        'miele': 'Miele',
        '17°? stormo': '17° Stormo',
        'bay rum': 'Bay Rum',
        'dandy': 'Dandy',
    },

    'Fenomeno Shave': {},

    'First Canadian Shave': {
        'motherfu?cker': 'Motherfucker',
        'mother-?fer': 'Motherfucker',
        'm\\*{4,12}r': 'Motherfucker',
        'dicken' + _apostophe + 's? cider': 'Dicken\'s Cider',
        'bl[óo]d av dreki': 'Blód av Dreki',
        'esther' + _apostophe + 's peppermint' + _any_and + 'grapefruit': 'Esther\'s Peppermint and Grapefruit',
        'barber\\s*shop': 'Barbershop',
    },

    'Floris London': {},

    'Fitjar Islands': {},

    'Geo. F. Trumper': {},

    'Gentleman\'s Nod': {
        'zaharoff': 'Zaharoff Signature',
        'no. 85': 'Ernest',
        'no. 01': 'George',
        'no. 42': 'Jackie',
        'no. 13': 'Johnny',
        'no. 11': 'Vincent',
        'kanpai': 'Kanpai'
    },

    'Gillette': {},

    'The Goodfellas\' Smile': {
        'abysso': 'Abysso',
        'amber foug[èeé]re': 'Amber Fougere',
        'chronos': 'Chronos',
        'inferno': 'Inferno',
        'no?\\. 1': 'N. 1',
        'patronus': 'Patronus',
        'shibusa': 'Shibusa',
        'Pino Alpestre': 'Pino Alpestre',
    },

    'Grooming Department': {
        # bases: Nai, Kairos, Fortis, Lusso, Mallard
        '(?:conditioning |)shave oil': 'Conditioning Shave Oil',
        'Aion$': 'Aion',
        'Amare$': 'Amare',
        'Angel$': 'Angel',
        'Boomer$': 'Boomer',
        'Chai$': 'Chai',
        'Chypre Peach$': 'Chypre Peach',
        'Coattails$': 'Coattails',
        'Coattails Redux$': 'Coattails Redux',
        'Dapper Mallard$': 'Dapper Mallard',
        'Etereo$': 'Etereo',
        'Frankenlime$': 'Frankenlime',
        'incense' + _any_and + 'oud$': 'Incense & Oud',
        'Ingress$': 'Ingress',
        'Laundry$': 'Laundry',
        'Lemon Bay$': 'Lemon Bay',
        'l\'Avventura$': 'l\'Avventura',
        'magnolia' + _any_and + 'oud$': 'Magnolia & Oud',
        'Maleki$': 'Maleki',
        '^Earl Grey$': 'Earl Grey',
        'Earl Grey Gelato': 'Earl Grey Gelato',
        '^Lavender$': 'Lavender',
        'Otium$': 'Otium',
        'Peach Chypre$': 'Peach Chypre',
        'Rainforest in Fortis Base$': 'Rainforest in Fortis Base',
        'Sandalwood Nobile$': 'Sandalwood Nobile',
        'Soap$': 'Soap',
        'Spa$': 'Spa',
        'Unum$': 'Unum',
        'Valencia$': 'Valencia',
        'Veritas$': 'Veritas',
        'Wonderland$': 'Wonderland',
    },

    'Haslinger': {},

    'Henri et Victoria': {
        'duc de santal': 'Duc de Santal',
        'cogna[cn]' + _any_and + 'cuban cigars': 'Cognac and Cuban Cigars',
        'foug[èeé]re': 'Fougère',
        'la poire fran[çc]aise?': 'La Poire Française',
        'deuce': 'Deuce',
        'chestnut l' + _apostophe + 'orange': 'Chestnut l\'Orange',
        'absinthe': 'Absinthe',
        'nautilus': 'Nautilus',
    },

    'Heritage Hill Shave Company': {},

    'Highland Springs Soap Company': {},

    'The Holy Black': {
        'jack' + _any_and + 'ginger': 'Jack & Ginger',
        'dr\\. jekyl+' + _any_and + 'mr\\. hyde': 'Dr. Jekyll & Mr. Hyde',
    },

    'House of Mammoth': {
        'restore$': 'Restore',
        'stones$': 'Stones',
        'santal noir$': 'Santal Noir',
        'mood indigo$': 'Mood Indigo',
        '^indigo$': 'Mood Indigo',
        '^marine$': 'Marine',
        '\\bz$': 'Z',
    },

    'Hub City Soap Company': {},

    'Institut Karité': { '', 'Shaving Soap' },

    'Los Jabones de Joserra': {
        'brihuega': 'Brihuega',
        'kilix': 'Kilix'
    },
    
    'Like Grandpa': {},
    
    'Maggard Razors': {
        'limes' + _any_and + 'bergamot': 'Limes & Bergamot',
        'london barbershop': 'London Barbershop',
        'tobacco' + _any_and + 'leather': 'Tobacco & Leather',
        'mango sage tea': 'Mango Sage Tea',
        'lilac$': 'Lilac',
        'orange menthol': 'Orange Menthol',
        'northern moss': 'Northern Moss',
    },

    'Maol Grooming': {},

    'Mama Bear': {},

    'Martin de Candre': {
        # TODO '\\s*$': 'Original',
        'original': 'Original',
        'classic': 'Original',
        'foug[èeé]re': 'Fougère',
        'agrumes': 'Agrumes',
        'vet[iy]ver': 'Vetyver',
    },

    'Mickey Lee Soapworks': {
        '(?:the |)kraken': 'The Kraken',
        '(?:the |)drunken goat': 'The Drunken Goat',
        'reuniou?n': 'Réunion',
        'lu' + _apostophe + 'au': 'Lu\'au',
    },

    'Mike\'s Natural Soaps': {
        'lemongrass' + _any_and + 'eucalyptus': 'Lemongrass & Eucalyptus',
        'pine' + _any_and + 'cedarwood': 'Pine & Cedarwood',
        '^lime$': 'Lime',
        'barber\\s*shop$': 'Barbershop',
    },

    'Mitchell\'s Wool Fat': { '': 'Mitchell\'s Wool Fat' },

    'Mondial 1908': {
        'sandal(?:o\\b|wood)': 'Sandalo',
        'bergamot(?:to|)' + _any_and + 'neroli': 'Bergamotto Neroli',
        'bergamot(?:to|) neroli': 'Bergamotto Neroli',
        'green tobacco': 'Tobacco Verde',
    },

    'Murphy and McNeil': {
        'nantahala': 'Nantahala',
        'tobac fanaile': 'Tobac Fanaile',
        'gael luc': 'Gael Luc',
        'triskele': 'Triskele',
        'magh tured': 'Magh Tured',
        'ogham stone': 'Ogham Stone',
    },

    'Noble Otter': {
        'the night before$': 'The Night Before',
        '(?:th[èeé] |)noir et vanill[ea]': 'Thé Noir et Vanille',
        'tnev\\b$': 'Thé Noir et Vanille',
        'northern elix[ie]r': 'Northern Elixir',
        'hama[mn]i$': 'Hamami',
        'bar+\\s*bar+$': 'Barrbarr',
        '(?:two|2)\\s*kings$': 'Two Kings',
        'orbit$': 'Orbit',
        'monarch$': 'Monarch',
        'bare$': 'Bare',
    },

    'Ogallala Bay Rum': {
        'sage,?' + _any_and + 'cedar': 'Bay Rum, Sage & Cedar',
        'limes,?' + _any_and + 'peppercorn': 'Bay Rum, Limes & Peppercorn',
        _any_and + 'sweet orange': 'Bay Rum & Sweet Orange',
        _any_and + 'vanilla': 'Bay Rum & Vanilla',
        # TODO '\\s*$': 'Bay Rum',
    },

    'Old Spice': {},

    'Oz Shaving': {},

    'P.160': {
        'tipo morbido': 'Tipo Morbido',
        'tipo duro': 'Tipo Duro'
    },

    'Palmolive': { 
        # TODO classic, stick, sensitive, "Rinfrescante"???
    },

    'PannaCrema': {
        'nu[àa]via blue?': 'Nuàvia Blu',
        'nu[àa]via (?:rossa?|red)': 'Nuàvia Rossa',
        'nu[àa]via nema': 'Nuàvia Nema',
        'nu[àa]via (?:verde|green)': 'Nuàvia Verde',
        'namaste': 'Namaste',
    },

    'Panee Soaps': {
        'the bergamot mystery': 'The Bergamot Mystery',
        'bergamot mystery': 'The Bergamot Mystery',
    },

    'Le Père Lucien': {
        'cologne[\\-\\s]*foug[èeé]re': 'Cologne-Fougère',
        'traditional': 'Traditionnel',
        'apricot': 'Abricot',
        'oud[\\s\\-]*santal': 'Oud-Santal',
    },

    'Phoenix and Beau': {
        'citra royale?': 'Citra Royale',
        '^spitfire$': 'Spitfire',
        '^albion$': 'Albion',
        'imperial rum': 'Imperial Rum',
        '^luna$': "Luna",
        '^v60$': 'V60',
    },

    'Phoenix Artisan Accoutrements': {
        'cad\\b': 'CaD',
        'club\\s*guy': 'Clubguy',
        'esp\\b': 'ESP',
        'Albion of the North': 'Albion of the North',
        'Atomic Age Bay Rum': 'Atomic Age Bay Rum',
        'lavender planet': 'Lavender Planet',
        '^cavendish$': 'Cavendish',
    },

    'Portus Cale': {
         # looks like only black has been made as shaving soap,
         # but two patterns to avoid the assumption
         # TODO '\\s*$': 'Black',
         # TODO remove once we can put the blank pattern back in
         'blank': 'Black',
         'black': 'Black'
    },

    'Pré de Provence': { 
        '(?:number|no\.?|num\.?|#|)\\s*63': 'No. 63',
        'bergamot' + _any_and + 'thyme': 'Bergamot and Thyme'
    },

    'Proraso': {
        '(?:white |)green tea' + _any_and + 'oat': 'Green Tea & Oatmeal',
        '(?:red |)sandalwood': 'Sandalwood',
        '(?:green |)menthol' + _any_and + 'eucalyptus': 'Menthol & Eucalyptus',
        'aloe' + _any_and + 'vitamin e': 'Aloe & Vitamin E',
        'green\\s*$': 'Menthol & Eucalyptus',
        'red\\s*$': 'Sandalwood',
        'white\\s*$': 'Green Tea & Oatmeal',
        'blue\\s*$': 'Aloe & Vitamin E',
    },

    'Pinnacle Grooming': {},

    'RazoRock': {
        'blue\\s*$': 'Blue Barbershop',
        'what the puck[\W]*\\s+blue': 'Blue Barbershop',
    },

    'Red House Farm': { 
        'cedar[^\w]+lime': 'Cedar-Lime',
        '(?:1920 |)barbershop': 'Barbershop 1920',
        _apostophe + 'tis the saison': '\'Tis the Saison',
        'pan de muerto': 'Pan de Muerto',
    },

    'Reef Point Soaps': {},

    'Saponificio Varesino': {
        'Cosmo[^a-z0-9]+beta 4.2': 'Cosmo',
        'Cubebe[^a-z0-9]+beta 4.3': 'Cubebe',
        'Opuntia[^a-z0-9]+beta 4.3': 'Opuntia',
        '70th Anniversary[^a-z0-9]+beta 4.1': '70th Anniversary',
        'Settantesimo Anniversario': '70th Anniversary',
        'desert ver?tiver': 'Desert Vetiver',
        'dolomiti$': 'Dolomiti',
    },

    'Seaforth!': {},

    'Shannon\'s Soaps': {
        'barber\\s*shop': 'Barbershop',
        'pina colada': 'Piña Colada',
        'lit\\b': 'Lit',
        'lady luck': 'Lady Luck',
        'bay patchouli grapefruit': 'Bay Patchouli Grapefruit',
    },

    'Siliski Soaps': {},

    'Soap Commander': {},

    'Southern Witchcrafts': {
        'grave\\s*fruit': 'Gravefruit',
        'desa?ia?rology': 'Desairology',
        'cedar': 'Cedar',
        'anthropophagy': 'Anthropophagy',
        'valley of ashes': 'Valley of Ashes',
        'autum[nm] ash': 'Autumn Ash',
        'ne[ck]romanti[ck]': 'Necromantic',
        '^druantia$': 'Druantia',
        '^pomona$': 'Pomona',
        'tres matres': 'Tres Matres',
        '^samhain$': 'Samhain',
        'Grey Phetiver': 'Grey Phetiver',
        'Lycanthropy': 'Lycanthropy',
    },

    'Spearhead Shaving Company': {
        'seaforth!? "?heather"?': 'Seaforth! Heather',
        'seaforth!? "?spiced"?': 'Seaforth! Spiced',
    },

    'Stirling Soap Co.': {
        '^spice$': 'Stirling Spice',
        '^noir$': 'Stirling Noir',
        '^green$': 'Stirling Green',
        '^(?:st[ie]rling |)gentleman': 'Stirling Gentleman',
        'rambling man': 'Ramblin Man',
        'port[\\- ]au[\\- ]prince': 'Port-au-Prince',
        'Phara?oh' + _apostophe + 's Dreamsicle': 'Pharaoh\'s Dreamsicle',
        'con+if+erous': 'Coniferous',
        'ar[kc]adia': 'Arkadia',
        'sharp dressed man': 'Sharp Dressed Man',
        'eskimo tuxedo': 'Eskimo Tuxedo',
        'christmas eve': 'Christmas Eve',
        'margaritas in the arctic': 'Margaritas in the Arctic',
        'scarn': 'Scarn',
        'gin' + _any_and + 'tonic': 'Gin & Tonic',
        'executive man': 'Executive Man',
        'barber\\s*shop': 'Barbershop',
        'frankincense' + _any_and + 'myrrh': 'Frankincense & Myrrh',
        'haverford': 'Haverford',
        'unscented (?:with |)beeswax': 'Unscented with Beeswax',
    },

    'Storybook Soapworks': {
        'carnivale': 'Carnivale',
        'west egg': 'West Egg',
        'coffee spoons': 'Coffee Spoons',
        'chasing sunsets': 'Chasing Sunsets',
        'elysium': 'Elysium',
        'fresca intensa': 'Fresca Intensa',
        'hallward' + _apostophe + 's dream': 'Hallward\'s Dream',
    },

    'Suavecito': {
        'shaving cream': 'Shaving Cream', # "natural peppermint scent"
        'peppermint': 'Shaving Cream',
        'whiske?y bar$': 'Whiskey Bar',
    },

    'The Sudsy Soapery': {
        'top o' + _apostophe + ' the morning': 'Top O\' the Morning',
        'lavend[ea]r' + _any_and + 'peppermint': 'Lavender & Peppermint',
        'sandalwood' + _any_and + 'myrrh': 'Sandalwood & Myrrh',
        'sandalwood' + _any_and + 'citrus': 'Sandalwood & Citrus',
        'rose' + _any_and + 'black pepper': 'Rose & Black Pepper',
        'white sage' + _any_and + 'lime': 'White Sage and Lime',
        'lemon rose chypre': 'Lemon Rose Chypre',
        'delor de treget': 'Delor de Treget',
    },

    'Summer Break Soaps': {
        'teacher' + _apostophe + 's pet$': 'Teacher\'s Pet',
        'valedictorian$': 'Valedictorian',
        'homecoming$': 'Homecoming',
        'field day$': 'Field Day',
        'bell\\s*ringer': 'Bell Ringer',
        'cannonball!?': 'Cannonball!',
    },

    'Tabac': {
        'original': 'Original'
    },
    
    'Talbot Shaving': {},

    'Tallow + Steel': {
        'morning coffee in the canadian wilderness': 'Morning Coffee in the Canadian Wilderness',
        'kyoto': 'Kyoto',
        'boreal': 'Boreal',
        'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
        'yrp\\b': 'Yuzu/Rose/Patchouli',
        'y/r/p\\b': 'Yuzu/Rose/Patchouli',
        'vide poche': 'Vide Poche',
    },

    'Taylor of Old Bond Street': {},

    'Tcheon Fung Sing': {
        'diVino$': 'diVino',
        'shave' + _any_and + 'roses rosehip': 'Shave & Roses Rosehip',
        'shave' + _any_and + 'roses dracaris': 'Shave & Roses Dracaris',
        # lineo intenso
        'bergamotto neroli': 'Bergamotto Neroli',
        'crazy sandalwood': 'Crazy Sandalwood',
        '(?:Aroma Intenso |)arancia amaro': 'Arancia Amaro',
    },

    'La Toja': { '': 'La Toja' },

    'Via Barberia': {
        'aquae\\s*[23]?$': 'Aquae',
        'fructi\\s*[23]?$': 'Fructi',
        'herbae\\s*[23]?$': 'Herbae',
    },

    'Vitos': {
        'verde': 'Green',
        'rosso': 'Red',
        'Extra Super': 'Red',
        '(?:super |)red': 'Red',
        'lanolin' + _any_and + 'eucalyptus': 'Lanolin & Eucalyptus'
    },

    'West Coast Shaving': {
        'gl[øo]gg': 'Gløgg',
        'oriental': 'Oriental',
        'chypre': 'Chypre',
        'foug[èeé]re': 'Fougère',
        'cologne': 'Cologne',
        'grapefroot': 'Grapefroot',
        'pear-brr+ shoppe': 'Pear-Brrr Shoppe',
        'gatsby v2': 'Gatsby V2',
    },

    'West of Olympia': {
        'tobacco' + _any_and + 'coffee': 'Tobacco & Coffee',
        'eucalyptus' + _any_and + 'spearmint': 'Eucalyptus & Spearmint',
        'PNW Wetshavers Meetup 2018': 'PNW Wetshavers Meetup 2018',
        'PNW Wetshavers Meetup 2019': 'PNW Wetshavers Meetup 2019',
    },

    'Wholly Kaw': {
        'eroe': 'Eroe',
        'foug[èeé]re mania': 'Fougère Mania',
        '(?:la |)foug[èeé]re parfaite': 'La Fougère Parfaite',
        'fou?gu?[èeé]re bou?quet': 'Fougère Bouquet',
        'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
        'y/r/p': 'Yuzu/Rose/Patchouli',
        'pasha' + _apostophe + 's pride': 'Pasha\'s Pride',
        'denariou?s': 'Denarius',
        'scentropy': 'Scentropy',
        'bare naked': 'Bare Naked',
    },

    'Wickham Soap Co.': {},

    'Wild West Shaving Co.': {
        'aces' + _any_and + 'eights': 'Aces & Eights',
        'the outlaw': 'The Outlaw',
        'Yippie Ki-Yay': 'Yippie Ki-Yay',
    },

    'Williams Mug Soap': { '': 'Williams Mug Soap' },

    'Zingari Man': {
        'nocturne': 'Nocturne',
        '(?:number|no\.?|num\.?|#|)\\s*1\\b': 'No. 1',
        '(?:the |)socialite': 'The Socialite',
        '(?:the |)watchm[ae]n': 'The Watchman',
        '(?:the |)blacksmith': 'The Blacksmith',
        '(?:the |)soloist': 'The Soloist',
        '(?:the |)wanderer': 'The Wanderer',
        '(?:the |)nomad$': 'The Nomad',
        '(?:the |)duo$': 'The Duo',
        '(?:the |)explorer$': 'The Explorer',
        '(?:the |)magician$': 'The Magician',
        '(?:the |)essentials$': 'The Essentials',
        '(?:the |)healers$': 'The Healers',
    },
}

_compiled_pats = None
_unique_names = None

def _add_unique( name_dict: dict ):
    global _unique_names
    if not _unique_names:
        _unique_names = { }
    for name in name_dict:
        if name not in _unique_names:
            _unique_names[name] = 1
        else:
            _unique_names[name] += 1


def _compile( name ):
    global _compiled_pats
    if _compiled_pats is None:
        _compiled_pats = { }
    if name:
        if name in _compiled_pats:
            return True
        if name in _scent_pats:
            map = _scent_pats[name]
            comp = { }
            isonames = { }
            for pattern in map:
                comp[re.compile(pattern + _ending, re.IGNORECASE)] = map[pattern]
                isonames[map[pattern]] = 1
            _compiled_pats[name] = comp
            _add_unique(isonames)
            return True
    else:
        for mkr in _scent_pats:
            if mkr not in _compiled_pats:
                map = _scent_pats[mkr]
                comp = { }
                isonames = { }
                for pattern in map:
                    comp[re.compile(pattern + _ending, re.IGNORECASE)] = map[pattern]
                    isonames[map[pattern]] = 1
                _compiled_pats[mkr] = comp
                _add_unique(isonames)
    return False


def _isUniqueScent( name: str ):
    if not _unique_names:
        raise Exception("_unique_names not built!")
    return name in _unique_names and _unique_names[name] == 1


def matchScent( maker, scent ):
    """ Attempts to match a scent name.  If successful, a dict is returned with the
        following elements:
            'result': the result object from Pattern.match()
            'name': the standard scent name
        Otherwise None is returned.
    """
    if not _compile(maker):
        return None
    for pattern in _compiled_pats[maker]:
        result = pattern.match(scent)
        if result:
            return { 'result': result, 'name': _compiled_pats[maker][pattern] }
    return None


def findAnyScent( text ):
    _compile(None)
    best = None
    issearch = False
    for maker in _compiled_pats:
        if len(_compiled_pats[maker]) < 2:
            # don't do single scents for now
            continue
        for pattern in _compiled_pats[maker]:
            if (pattern.match('') or pattern.match('cream') or pattern.match('soap')
                    or _simple_cream_soap_pat.match(_compiled_pats[maker][pattern])):
                # simple cream/soap; not valid for scent-first match
                # TODO uniqueness test
                continue
            result = pattern.match(text)
            if result and (not best
                    or result.start() < best['result'].start()
                    or (result.end() - result.start() > best['result'].end() - best['result'].start())):
                best = {
                    'result': result,
                    'scent': _compiled_pats[maker][pattern],
                    'maker': maker,
                    'lather': text
                }
            elif not best or issearch:
                result = pattern.search(text)
                if result and (not best
                        or result.start() < best['result'].start()
                        or (result.end() - result.start() > best['result'].end() - best['result'].start())):
                    issearch = True
                    best = {
                        'result': result,
                        'scent': _compiled_pats[maker][pattern],
                        'maker': maker,
                        'lather': text
                    }

    return best


def getSingleScent( maker ):
    """ If only one single scent is known for this maker, its name is returned.
        Otherwise None is returned.
    """
    if not _compile(maker):
        return None
    if len(_compiled_pats[maker]) == 1:
        for x in _compiled_pats[maker]:
            return _compiled_pats[maker][x]
    return None

