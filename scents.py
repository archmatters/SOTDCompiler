#!/usr/bin/env python3

import re

_apostophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'

_scent_pats = {
    'Abbate y la Mantia': { },

    'Acqua di Parma': { },

    'Apex Alchemy Soaps': { },

    'Archaic Alchemy': { },

    'Ariana & Evans': { },

    'Arko': { '': 'Arko' },

    'Art of Shaving': { },

    'Arran': { },

    'Australian Private Reserve': { },

    'Barbus': { },

    'Barrister and Mann': {
        'seville': 'Seville',
        'eigengrau': 'Eigengrau',
        '[\\w\\s]*grande? chypre.*': 'Le Grand Chypre',
        'dickens,?\\s+revisited': 'Dickens, Revisited',
        'oh?' + _apostophe + ',?\\s*delight': 'O, Delight!',
        'brew ha': 'Brew Ha-Ha',
        'hallow': 'Hallows',
        'paganini': 'Paganini\'s Violin'
     },
    
    'Black Ship Grooming Co.': { },

    'Bufflehead': { },

    'C.O. Bigelow': { },

    'Captain\'s Choice': { },

    'Castle Forbes': { },

    'Catie\'s Bubbles': { },

    'CBL Soaps': { },

    'Cella': { '': 'Cella' },

    'Central Texas Soaps': { },

    'Chicago Grooming Co.': { },

    'Chiseled Face': { },

    'Cold River Soap Works': { },

    'Col. Conk': { },

    'Crabtree & Evelyn': { },

    'Cremo': { },

    'D.R. Harris': { },

    'Declaration Grooming': {
        'sellout': 'Sellout',
        'tribute': 'Tribute',
        'opulence': 'Opulence',
        'cuir et \S+pices': 'Cuir et Épices',
        'cygnus x': 'Cygnus X-1',
        'hindsight': 'Hindsight',
        'gratiot league': 'Gratiot League Square',
        'original': 'Original',
        'trismegistus': 'Trismegistus',
        'after the rain': 'After the Rain',
        'yrp\\b': 'Yuzu/Rose/Patchouli',
        'y/r/p\\b': 'Yuzu/Rose/Patchouli',
        'moti\\b': 'Massacre of the Innocents',
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

    'Floris London': { },

    'Fitjar Islands': { },

    'Geo. F. Trumper': { },

    'Gentleman\'s Nod': { },

    'Gillette': { },

    'The Goodfellas\' Smile': { },

    'Grooming Department': { },

    'First Canadian Shave Soap Co.': { },

    'Haslinger': { },

    'Henri et Victoria': { },

    'Heritage Hill Shave Company': { },

    'Highland Springs Soap Company': { },

    'Hub City Soap Company': { },
    
    'L\'Occitane': { },

    'La Toja': { '': 'La Toja' },

    'Like Grandpa': { },
    
    'Maggard Razors': { },

    'Maol Grooming': { },

    'Mama Bear': { },

    'Mammoth Soaps': { },

    'Martin de Candre': { },

    'Mickey Lee Soapworks': { },

    'Mike\'s Natural Soaps': { },

    'Mitchell\'s Wool Fat': { '': 'Mitchell\'s Wool Fat' },

    'Murphy and McNeil': { },

    'Noble Otter': { },

    'Old Spice': { },

    'Oz Shaving': { },

    'PannaCrema': { },

    'Phoenix and Beau': { },

    'Phoenix Artisan Accoutrements': { },

    'Pré de Provence': { },

    'Proraso': { },

    'Pinnacle Grooming': { },

    'RazoRock': { },

    'Reef Point Soaps': { },

    'Saponificio Varesino': { },

    'Seaforth!': { },

    'Shannon\'s Soaps': { },

    'Siliski Soaps': { },

    'Soap Commander': { },

    'Southern Witchcrafts': { },

    'Spearhead Shaving Company': { },

    'Stirling Soap Co.': { },

    'Storybook Soapworks': { },

    'The Sudsy Soapery': { },

    'Summer Break Soaps': { },
    
    'Talbot Shaving': { },

    'Tallow + Steel': { },

    'Taylor of Old Bond Street': { },

    'Vitos': { },

    'Wholly Kaw': { },

    'Wickham Soap Co.': { },

    'William\'s Mug Soap': { '': 'William\'s Mug Soap' },

    'Zingari Man': {
        'nocturne': 'Nocturne'
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
            comp[re.compile(pattern, re.IGNORECASE)] = map[pattern]
        _compiled_pats[name] = comp
        return True
    return False

def matchScent( maker, scent ):
    """ Attempts to match a scent name.  If successful, a dict is returned with the
        following elements:
            'result': the result object from re.match()
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

