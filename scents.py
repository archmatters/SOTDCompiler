#!/usr/bin/env python3

import re

_apostophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'
_ending = '[\\.,]?'

_scent_pats = {
    'Abbate y la Mantia': {
        'krokos': 'Krokos',
        'crumiro': 'Crumiro',
        'matteo': 'Matteo 9,11',
        'garibaldi': 'Garibaldi',
        'monet': 'Monet',
        'buttero': 'Buttero'
     },

    'Acqua di Parma': { },

    'Apex Alchemy Soaps': {
        'American Pi': 'American Pi',
        'Nightcrawler': 'Nightcrawler'
     },

    'Archaic Alchemy': { },

    'Ariana & Evans': { },

    'Arko': { '': 'Arko' },

    'Art of Shaving': { },

    'Arran': { },

    'Australian Private Reserve': { },

    'Barbasol': {
        '\\s$': 'Cream',
        'soothing aloe\\b': 'Soothing Aloe',
     },

    'Barbus': {
        '\\s*$': 'Classic',
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
        'behold the whatsis': 'Behold the Whatsis!',
        'dfs (?:2017|exclusive)': 'DFS 2017 LE',
        'waves$': 'Reserve Waves',
        'spice$': 'Reserve Spice',
        'fern$': 'Reserve Fern',
        'lavender$': 'Reserve Lavender',
        'cool$': 'Reserve Cool',
        'classic$': 'Reserve Classic',
        'le grand (?:cyphre|chypre)': 'Le Grand Chypre',
        '(?:motherfuckin(?:\'|g)|mf) roam': 'Roam',
     },

    'BAUME.BE': {
        '(?:shaving |)soap': 'Soap',
        '(?:shaving |)cream': 'Cream'
    },
    
    'Black Ship Grooming Co.': {
        'captain' + _apostophe + 's choice': 'Captain\'s Choice',
        'calypso' + _apostophe + 's curse': 'Calypso\'s Curse',
     },

    'The Bluebeards Revenge': { '': 'Shaving Cream' },

    'Bufflehead': { },

    'C.O. Bigelow': { },

    'Captain\'s Choice': { },

    'Castle Forbes': { },

    'Catie\'s Bubbles': { },

    'CBL Soaps': { },

    'Cella': {
        '[\w ]+aloe vera': 'Aloe Vera cream',
        '(?:cella |)crema sapone': 'Cream soap',
        '(?:cella |)crema d[ae] barba': 'Cream',
        'soap': 'Cream soap',
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
     },

    'Chiseled Face': {
        'gtb': 'Ghost Town Barber',
        'ghosttown barber': 'Ghost Town Barber',
     },

    'Cold River Soap Works': { },

    'Colgate': { '': 'Mug soap' },

    'Col. Conk': { },

    'Crabtree & Evelyn': { },

    'Cremo': { },

    'D.R. Harris': { },

    'Dalan': {
        'energetic': 'Energetic',
        'cool': 'Cool',
        'sensitive': 'Sensitive'
    },

    'Declaration Grooming': {
        'sellout': 'Sellout',
        'tribute': 'Tribute',
        'opulence': 'Opulence',
        'cuir et [èeé]pices': 'Cuir et Épices',
        'cygnus x': 'Cygnus X-1',
        'hindsight': 'Hindsight',
        'gratiot league': 'Gratiot League Square',
        'original': 'Original',
        'trismegistus': 'Trismegistus',
        'after the rain': 'After the Rain',
        'yrp\\b': 'Yuzu/Rose/Patchouli',
        'y/r/p\\b': 'Yuzu/Rose/Patchouli',
        'moti\\b': 'Massacre of the Innocents',
        'massacre$': 'Massacre of the Innocents',
        'son et lumiere': 'Son et Lumiere',
        'b[\\- ?]cubed?': 'Blackberry Blossom Bay',
        'b3\\b': 'Blackberry Blossom Bay',
     },

    'Dindi Naturals': { '': 'lemon myrtle, macadamia + white cypress' },

    'Dr. Jon\'s': { },

    'Edwin Jagger': { },

    'Eleven Shaving': { },

    'ETHOS': { },

    'Executive Shaving': { },

    'Eufros': { },

    'Fenomeno Shave': { },

    'Eleven': { },

    'First Canadian Shave': {
        'motherfucker': 'Motherfucker',
        'mother-?fer': 'Motherfucker',
        'm\\*{4,12}r': 'Motherfucker',
        'dicken' + _apostophe + 's? cider': 'Dicken\'s Cider',
        'bl[óo]d av dreki': 'Blód av Dreki',
        'esther' + _apostophe + 's peppermint' + _any_and + 'grapefruit': 'Esther\'s Peppermint and Grapefruit',
        'barber\\s*shop': 'Barbershop',
    },

    'Floris London': { },

    'Fitjar Islands': { },

    'Geo. F. Trumper': { },

    'Gentleman\'s Nod': {
        'zaharoff': 'Zaharoff Signature',
        'no. 85': 'Ernest',
        'no. 01': 'George',
        'no. 42': 'Jackie',
        'no. 13': 'Johnny',
        'no. 11': 'Vincent',
        'kanpai': 'Kanpai'
     },

    'Gillette': { },

    'The Goodfellas\' Smile': { },

    'Grooming Department': { },

    'Haslinger': { },

    'Henri et Victoria': {
        'duc de santal': 'Duc de Santal',
        'cognac' + _any_and + 'cuban cigars': 'Cognac and Cuban Cigars',
        'foug[èeé]re': 'Fougère',
        'la poire fran[çc]aise?': 'La Poire Française',
        'deuce': 'Deuce',
        'chestnut l' + _apostophe + 'orange': 'Chestnut l\'Orange',
        'absinthe': 'Absinthe',
        'nautilus': 'Nautilus',
     },

    'Heritage Hill Shave Company': { },

    'Highland Springs Soap Company': { },

    'The Holy Black': {
        'jack' + _any_and + 'ginger': 'Jack & Ginger',
        'dr\\. jekyl+' + _any_and + 'mr\\. hyde': 'Dr. Jekyll & Mr. Hyde',
    },

    'Hub City Soap Company': { },

    'Los Jabones de Joserra': {
        'brihuega': 'Brihuega',
        'kilix': 'Kilix'
     },
    
    'Like Grandpa': { },
    
    'Maggard Razors': { },

    'Maol Grooming': { },

    'Mama Bear': { },

    'Mammoth Soaps': { },

    'Martin de Candre': {
        '\\s*$': 'Original',
        'classic': 'Original',
        'foug[èeé]re': 'Fougère',
        'agrumes': 'Agrumes',
        'vet[iy]ver': 'Vetyver',
     },

    'Mickey Lee Soapworks': {
        'kraken': 'The Kraken',
        'drunken goat': 'The Drunken Goat',
        'reuniou?n': 'Réunion',
        'lu' + _apostophe + 'au': 'Lu\'au',
     },

    'Mike\'s Natural Soaps': { },

    'Mitchell\'s Wool Fat': { '': 'Mitchell\'s Wool Fat' },

    'Mondial 1908': {
        'sandal(?:o\\b|wood)': 'Sandalo',
        'bergamot(?:to|)' + _any_and + 'neroli': 'Bergamotto Neroli',
        'bergamot(?:to|) neroli': 'Bergamotto Neroli',
        'green tobacco': 'Tobacco Verde',
    },

    'Murphy and McNeil': { },

    'Noble Otter': {
        'the night before': 'The Night Before',
        '(?:th[èeé] |)noir et vanille': 'Thé Noir et Vanille',
        'tnev\\b': 'Thé Noir et Vanille',
        'northern" elix[ie]r': 'Northern Elixir',
        'hama[mn]i': 'Hamami',
        'bar+\\s*bar+': 'Barrbarr',
        '(?:two|2)\\s*kings': 'Two Kings',
     },

    'Ogallala Bay Rum': {
        'sage,?' + _any_and + 'cedar': 'Bay Rum, Sage & Cedar',
        'limes,?' + _any_and + 'peppercorn': 'Bay Rum, Limes & Peppercorn',
        _any_and + 'sweet orange': 'Bay Rum & Sweet Orange',
        _any_and + 'vanilla': 'Bay Rum & Vanilla',
        '\\s*$': 'Bay Rum',
    },

    'Old Spice': { },

    'Oz Shaving': { },

    'P.160': {
        'tipo morbido': 'Tipo Morbido',
        'tipo duro': 'Tipo Duro'
    },

    'Palmolive': { 
        # TODO classic, stick, sensitive, "Rinfrescante"???
    },

    'PannaCrema': {
        'nu[àa]via blue?': 'Nuàvia Blu',
        'nu[àa]via (?:rossa|red)': 'Nuàvia Rossa',
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

    'Phoenix and Beau': { },

    'Phoenix Artisan Accoutrements': {
        'cad\\b': 'CaD',
        'club\\s*guy': 'Clubguy',
        'esp\\b': 'ESP',
     },

    'Portus Cale': {
         # looks like only black has been made as shaving soap,
         # but two patterns to avoid the assumption
         '\\s*$': 'Black',
         'black': 'Black'
    },

    'Pré de Provence': { 
        '(?:number|no\.?|num\.?|#|)\\s*63': 'No. 63',
        'bergamot' + _any_and + 'thyme': 'Bergamot and Thyme'
    },

    'Proraso': {
        'green tea' + _any_and + 'oat': 'White',
        'sandalwood': 'Red',
        'menthol' + _any_and + 'eucalyptus': 'Green',
        'aloe' + _any_and + 'vitamin e': 'Blue',
     },

    'Pinnacle Grooming': { },

    'RazoRock': {
        'blue\\s*$': 'Blue Barbershop',
        'what the puck[\W]*\\s+blue': 'Blue Barbershop',
     },

    'Red House Farms': { 
        'cedar[^\w]+lime': 'Cedar-Lime',
        'barbershop': 'Barbershop 1920',
        _apostophe + 'tis the saison': '\'Tis the Saison',
        'pan de muerto': 'Pan de Muerto',
    },

    'Reef Point Soaps': { },

    'Saponificio Varesino': {
        'Cosmo[^a-z0-9]+beta 4.2': 'Cosmo',
        'Cubebe[^a-z0-9]+beta 4.3': 'Cubebe',
        'Opuntia[^a-z0-9]+beta 4.3': 'Opuntia',
        '70th Anniversary[^a-z0-9]+beta 4.1': '70th Anniversary',
     },

    'Seaforth!': { },

    'Shannon\'s Soaps': { },

    'Siliski Soaps': { },

    'Soap Commander': { },

    'Southern Witchcrafts': {
        'grave\\s*fruit': 'Gravefruit',
        'desa?irology': 'Desairology',
        'cedar': 'Cedar',
     },

    'Spearhead Shaving Company': { },

    'Stirling Soap Co.': {
        'spice$': 'Stirling Spice',
        'noir$': 'Stirling Noir',
        'green$': 'Stirling Green',
        'gentleman': 'Stirling Gentleman',
        'rambling man': 'Ramblin Man',
        'port[\\- ]au[\\- ]prince': 'Port-au-Prince',
        'Pharoh' + _apostophe + 's Dreamsicle': 'Pharoh\'s Dreamsicle',
        'con+if+erous': 'Coniferous',
        'arcadia': 'Arkadia',
     },

    'Storybook Soapworks': { },

    'The Sudsy Soapery': {
        'top o' + _apostophe + ' the morning': 'Top O\' the Morning',
        'lavend[ea]r' + _any_and + 'peppermint': 'Lavender & Peppermint',
        'sandalwood' + _any_and + 'myrrh': 'Sandalwood & Myrrh',
        'sandalwood' + _any_and + 'citrus': 'Sandalwood & Citrus',
        'rose' + _any_and + 'black pepper': 'Rose & Black Pepper',
        'white sage' + _any_and + 'lime': 'White Sage and Lime',
     },

    'Summer Break Soaps': { },
    
    'Talbot Shaving': { },

    'Tallow + Steel': { },

    'Taylor of Old Bond Street': { },

    'La Toja': { '': 'La Toja' },

    'Vitos': {
        'verde': 'Green',
        'rosso': 'Red',
        'Extra Super': 'Red',
        '(?:super |)red': 'Red',
        'lanolin' + _any_and + 'eucalyptus': 'Lanolin & Eucalyptus'
     },

    'Wholly Kaw': {
        'eroe': 'Eroe',
        'foug[èeé]re mania': 'Fougère Mania',
        '(?:la |)foug[èeé]re parfaite': 'La Fougère Parfaite',
        'foug[èeé]re bouquet': 'Fougère Bouquet',
        'yuzu/rose/patchouli': 'Yuzu/Rose/Patchouli',
        'y/r/p': 'Yuzu/Rose/Patchouli',
        'pasha' + _apostophe + 's pride': 'Pasha\'s Pride',
        'denariou?s': 'Denarius',
     },

    'Wickham Soap Co.': { },

    'Williams Mug Soap': { '': 'Williams Mug Soap' },

    'Zingari Man': {
        'nocturne': 'Nocturne',
        '(?:number|no\.?|num\.?|#|)\\s*1\\b': 'No. 1',
        'socialite': 'The Socialite',
        '(?:the |)watchm[ae]n': 'The Watchman',
        'blacksmith': 'The Blacksmith',
        'soloist': 'The Soloist',
        'wanderer': 'The Wanderer',
        'nomad': 'The Nomad',
        '(?:the |)duo\\b': 'The Duo'
     },
}

_compiled_pats = None

def _compile( name ):
    global _compiled_pats
    if _compiled_pats is None:
        _compiled_pats = { }
    if name in _compiled_pats:
        return True
    if name in _scent_pats:
        map = _scent_pats[name]
        comp = { }
        for pattern in map:
            comp[re.compile(pattern + _ending, re.IGNORECASE)] = map[pattern]
        _compiled_pats[name] = comp
        return True
    return False


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

