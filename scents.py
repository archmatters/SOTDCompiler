#!/usr/bin/env python3

import re

_apostophe = '(?:\'|&#39;|’|)'
_any_and = '\\s*(?:&(?:amp;|)|and|\+)\\s*'

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

    'Barbus': { },

    'Barrister and Mann': {
        'seville': 'Seville',
        'eigengrau': 'Eigengrau',
        '[\\w\\s]*grande? chypre.*': 'Le Grand Chypre',
        'dickens,?\\s+revisited': 'Dickens, Revisited',
        'oh?' + _apostophe + ',?\\s*delight': 'O, Delight!',
        'brew ha': 'Brew Ha-Ha',
        'hallow': 'Hallows',
        'paganini': 'Paganini\'s Violin',
        'leviathan': 'Leviathan',
        'beaudelaire': 'Beaudelaire',
        'foug[èeé]re gothi': 'Fougère Gothique',
        'foug[èeé]re angel': 'Fougère Angelique'
     },
    
    'Black Ship Grooming Co.': {
        'captain' + _apostophe + 's choice': 'Captain\'s Choice',
        'calypso' + _apostophe + 's curse': 'Calypso\'s Curse',
     },

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
        'son et lumiere': 'Son et Lumiere',
        'b cubed?': 'B Cubed',
        'b3\\b': 'B Cubed',
        'blackberry blossom bay': 'B Cubed',
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

    'Ogallala Bay Rum': {
        'sage,?' + _any_and + 'cedar': 'Bay Rum, Sage & Cedar',
        'limes,?' + _any_and + 'peppercorn': 'Bay Rum, Limes & Peppercorn',
        _any_and + 'sweet orange': 'Bay Rum & Sweet Orange',
        _any_and + 'vanilla': 'Bay Rum & Vanilla',
        '\\s*$': 'Bay Rum'
    },

    'Old Spice': { },

    'Oz Shaving': { },

    'PannaCrema': { },

    'Phoenix and Beau': { },

    'Phoenix Artisan Accoutrements': { },

    'Pré de Provence': { 
        '(?:number|no\.?|num\.?)\\s*63': 'No. 63',
        'bergamot' + _any_and + 'thyme': 'Bergamot and Thyme'
    },

    'Proraso': { },

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

    'Vitos': {
        'verde': 'Green',
        'rosso': 'Red',
        'Extra Super': 'Red',
        '(?super |)red': 'Red',
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

