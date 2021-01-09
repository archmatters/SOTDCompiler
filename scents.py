#!/usr/bin/env python3

import re

scent_pats = {
    'Abbate y la Mantia': { },

    'Acqua di Parma': { },

    'Apex Alchemy Soaps': { },

    'Ariana & Evans': { },

    'Arko': { re.compile(''): 'Arko' },

    'Art of Shaving': { },

    'Arran': { },

    'Australian Private Reserve': { },

    'Barbus': { },

    'Barrister and Mann': { },
    
    'Black Ship Grooming Co.': { },

    'Bufflehead': { },

    'C.O. Bigelow': { },

    'Captain\'s Choice': { },

    'Castle Forbes': { },

    'Catie\'s Bubbles': { },

    'CBL Soaps': { },

    'Cella': { re.compile(''): 'Cella' },

    'Central Texas Soaps': { },

    'Chicago Grooming Co.': { },

    'Chiseled Face': { },

    'Cold River Soap Works': { },

    'Col. Conk': { },

    'Crabtree & Evelyn': { },

    'Cremo': { },

    'D.R. Harris': { },

    'Declaration Grooming': { },

    'Dr. Jon\'s': { },

    'Edwin Jagger': { },

    'Eleven Shaving': { },

    'ETHOS': { },

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

    'La Toja': { re.compile(''): 'La Toja' },

    'Like Grandpa': { },
    
    'Maggard Razors': { },

    'Maol Grooming': { },

    'Mama Bear': { },

    'Mammoth Soaps': { },

    'Martin de Candre': { },

    'Mickey Lee Soapworks': { },

    'Mike\'s Natural Soaps': { },

    'Mitchell\'s Wool Fat': { re.compile(''): 'Mitchell\'s Wool Fat' },

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

    'Wholly Kaw': { },

    'Wickham Soap Co.': { },

    'William\'s Mug Soap': { re.compile(''): 'William\'s Mug Soap' },

    'Zingari Man': { },
}