#!/usr/bin/env python3

import re

maker_pats = {
    re.compile('abbate y la mantia\\s*(.*)', re.IGNORECASE): 'Abbate y la Mantia',

    re.compile('acqua di parma\\s*(.*)', re.IGNORECASE): 'Acqua di Parma',

    re.compile('apex alchemy\\s*(?:soaps?|)\\s*(.*)', re.IGNORECASE): 'Apex Alchemy Soaps',

    re.compile('ariana\\s*(?:&(?:amp;|)|and|n)\\s*evans\\s*(.*)', re.IGNORECASE): 'Ariana & Evans',
    re.compile('a\\s*&\\s*e\\s*(.*)', re.IGNORECASE): 'Ariana & Evans',

    re.compile('arko\\s*(.*)', re.IGNORECASE): 'Arko',

    re.compile('art of shaving\\s*(.*)', re.IGNORECASE): 'Art of Shaving',
    re.compile('aos\\b\\s*(.*)', re.IGNORECASE): 'Art of Shaving',

    re.compile('archaic alchemy\\s*(.*)', re.IGNORECASE): 'Archaic Alchemy',

    re.compile('arran\\s*(.*)', re.IGNORECASE): 'Arran',

    re.compile('australian private reserve\\s*(.*)', re.IGNORECASE): 'Australian Private Reserve',
    re.compile('apr\\b\\s*(.*)', re.IGNORECASE): 'Australian Private Reserve',

    re.compile('barbus\\s*(.*)', re.IGNORECASE): 'Barbus',

    re.compile('b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\s*(.*)', re.IGNORECASE): 'Barrister and Mann',
    re.compile('barrister\\s*(?:&(?:amp;|)|and|n)\\s*mann?\\s*(.*)', re.IGNORECASE): 'Barrister and Mann',

    re.compile('black ship\\s(?:grooming\\s*(?:co\\.?|)|)\\s*(.*)', re.IGNORECASE): 'Black Ship Grooming Co.',

    re.compile('bufflehead\\s*(.*)', re.IGNORECASE): 'Bufflehead',

    re.compile('c\\.?\\s*o\\.?\\s*bigelow\\s*(.*)', re.IGNORECASE): 'C.O. Bigelow',

    re.compile('captain(?:\'|&#39;|’|)s choice\\s*(.*)', re.IGNORECASE): 'Captain\'s Choice',

    re.compile('castle forbes\\s*(.*)', re.IGNORECASE): 'Castle Forbes',

    re.compile('catie(?:\'|&#39;|’|)s bubbles\\s*(.*)', re.IGNORECASE): 'Catie\'s Bubbles',
    re.compile('sfws\\s*/\\s*catie(?:\'|&#39;|’|)s bubbles\\s*(.*)', re.IGNORECASE): 'Catie\'s Bubbles',

    re.compile('cbl\\s*(?:soaps?|)\\s*(.*)', re.IGNORECASE): 'CBL Soaps',

    re.compile('cella\\s*(.*)', re.IGNORECASE): 'Cella',

    re.compile('central texas (?:soaps?|)\\s*(.*)', re.IGNORECASE): 'Central Texas Soaps',

    re.compile('oleo\\s*(?:soap|soapworks|)\\s*(.*)', re.IGNORECASE): 'Chicago Grooming Co.',
    re.compile('chicago groom\\w+\\s*(?:company|co\\.?)\\s*(?:\(formerly[^)]+\)|)\\s*(.*)', re.IGNORECASE): 'Chicago Gromming Co.',

    re.compile('chiseled face\\s*(.*)', re.IGNORECASE): 'Chiseled Face',

    re.compile('cold river\\s*(?:soap\\s*works)\\s*(.*)', re.IGNORECASE): 'Cold River Soap Works',

    re.compile('(?:col(?:onel|\\.|) |)conk\\s*(.*)', re.IGNORECASE): 'Col. Conk',

    re.compile('crabtree\\s*(?:&(?:amp;|)|and|n)\\s*evelyn\\s*(.*)', re.IGNORECASE): 'Crabtree & Evelyn',

    re.compile('cremo\\s*(.*)', re.IGNORECASE): 'Cremo',

    re.compile('d\\.?\\s*r\\.?\\s*harris\\s*(.*)', re.IGNORECASE): 'D.R. Harris',

    re.compile('dindi naturals\\s*(.*)', re.IGNORECASE): 'Dindi Naturals',

    re.compile('Declaration Grooming/Chatillon Lux\\s*(.*)', re.IGNORECASE): 'Declaration Grooming',
    re.compile('Declaration Grooming/Maggard Razors\\s*(.*)', re.IGNORECASE): 'Declaration Grooming',
    re.compile('declaration\\s*(?:grooming|)\\s*(.*)', re.IGNORECASE): 'Declaration Grooming',
    re.compile('dg\\b(?:/CL|)\\s*(.*)', re.IGNORECASE): 'Declaration Grooming',
    re.compile('da\\b\\s*(.*)', re.IGNORECASE): 'Declaration Grooming', #errata
    re.compile('Chatillon Lux/Declaration Grooming\\s*(.*)', re.IGNORECASE): 'Declaration Grooming',

    re.compile('dr.? joh?n(?:\'|&#39;|’|)s\\s*(.*)', re.IGNORECASE): 'Dr. Jon\'s',

    re.compile('edwin jagg[ea]r\\s*(.*)', re.IGNORECASE): 'Edwin Jagger',

    re.compile('eleven\\s*(.*)', re.IGNORECASE): 'Eleven Shaving',

    re.compile('ethos\\s*(.*)', re.IGNORECASE): 'ETHOS',

    re.compile('eufros\\s*(.*)', re.IGNORECASE): 'Eufros',

    re.compile('executive shaving\\s*(.*)', re.IGNORECASE): 'Executive Shaving',

    re.compile('fenom[ei]no\\s*(?:shave|)\\s*(.*)', re.IGNORECASE): 'Fenomeno Shave',

    re.compile('fine\\s*(?:accoutrements|)\\s*(.*)', re.IGNORECASE): 'Eleven',

    re.compile('floris\\s*(?:(?:of|)\\s*london|)\\s*(.*)', re.IGNORECASE): 'Floris London',

    re.compile('fitjar\\s*(?:islands?|)\\s*(.*)', re.IGNORECASE): 'Fitjar Islands',

    re.compile('geo\\.?\\s*f\\.?\\s*trumper\\s*(.*)', re.IGNORECASE): 'Geo. F. Trumper',

    re.compile('gentlem[ae]n(?:\'|&#39;|’|)s? nod\\s*(.*)', re.IGNORECASE): 'Gentleman\'s Nod',

    re.compile('gillette\\s*(.*)', re.IGNORECASE): 'Gillette',

    re.compile('(?:the|)\\s*goodfella(?:\'|&#39;|’|)s(?:\'|&#39;|’|)\\s*(?:smile|)\\s*(.*)', re.IGNORECASE): 'The Goodfellas\' Smile',

    re.compile('grooming dep\\S*\\s*(.*)', re.IGNORECASE): 'Grooming Department',

    re.compile('first canadian\\s*(?:shave soap\\s*(?:company|co.?|)|)\\s*(.*)', re.IGNORECASE): 'First Canadian Shave Soap Co.',

    re.compile('haslinger\\s*(.*)', re.IGNORECASE): 'Haslinger',

    re.compile('henri et victoria\\s*(.*)', re.IGNORECASE): 'Henri et Victoria',

    re.compile('henri et victoria\\s*(.*)', re.IGNORECASE): 'Henri et Victoria',

    re.compile('heritage hill(?: shave\\s*(?:company|co\\.?)|)\\s*(.*)', re.IGNORECASE): 'Heritage Hill Shave Company',

    re.compile('highland spring soap\\s*(?:company|co\\.?)\\s*(.*)', re.IGNORECASE): 'Highland Springs Soap Company',
    re.compile('highland spring\\s*(.*)', re.IGNORECASE): 'Highland Springs Soap Company',
    re.compile('hssc\\s*(.*)', re.IGNORECASE): 'Highland Springs Soap Company',

    re.compile('hub city\\s*(?:soap (?:company|co\\.?))\\s*(.*)', re.IGNORECASE): 'Hub City Soap Company',

    re.compile('imperial\\s*(?:barber (?:products|grade products?|)|)\\s*(.*)', re.IGNORECASE): 'Imperial Barber',
    
    re.compile('l(?:\'|&#39;|’|)occitane\\s*(.*)', re.IGNORECASE): 'L\'Occitane',

    re.compile('la toja\\s*(.*)', re.IGNORECASE): 'La Toja',
    
    re.compile('like grandpa\\s*(.*)', re.IGNORECASE): 'Like Grandpa',
    
    re.compile('maggard\\s*(?:razors?|)\\s*(.*)', re.IGNORECASE): 'Maggard Razors',

    re.compile('maol\\s*(?:grooming|)\\s*(.*)', re.IGNORECASE): 'Maol Grooming',

    re.compile('mama bear\\s*(.*)', re.IGNORECASE): 'Mama Bear',

    re.compile('mammoth\\s*(?:soaps?|)\\s*(.*)', re.IGNORECASE): 'Mammoth Soaps',

    re.compile('martin de candre\\s*(.*)', re.IGNORECASE): 'Martin de Candre',

    re.compile('micke?y lee soap\w+\\s*(.*)', re.IGNORECASE): 'Mickey Lee Soapworks',
    re.compile('mls\\b\\s*(.*)', re.IGNORECASE): 'Mickey Lee Soapworks',

    re.compile('mike(?:\'|&#39;|’|)s natural soaps?\\s*(.*)', re.IGNORECASE): 'Mike\'s Natural Soaps',

    re.compile('mitchell(?:\'|&#39;|’|)s\\s*(?:wool fat|)\\s*(.*)', re.IGNORECASE): 'Mitchell\'s Wool Fat',

    re.compile('m[üu]hle\\s*(.*)', re.IGNORECASE): 'Mühle',

    re.compile('murphy\\s*(?:&(?:amp;|)|and|n)\\s*mcneil\\s*(.*)', re.IGNORECASE): 'Murphy and McNeil',

    re.compile('mystic water\\s*(?:soaps?|)\\s*(.*)', re.IGNORECASE): 'Mystic Water Soap',

    re.compile('noble otter\\s*(.*)', re.IGNORECASE): 'Noble Otter',
    re.compile('n\\.?\\s*o\\.?\\s+(.*)', re.IGNORECASE): 'Noble Otter',

    re.compile('obsessive soap(?:s|\\s+perfect\w+|)\\s*(.*)', re.IGNORECASE): 'Obsessive Soap Perfectionist',
    re.compile('osp(?:\\s*soaps?|\\b)\\s*(.*)', re.IGNORECASE): 'Obsessive Soap Perfectionist',

    re.compile('old spice\\s*(.*)', re.IGNORECASE): 'Old Spice',

    re.compile('oz shaving\\s*(.*)', re.IGNORECASE): 'Oz Shaving',

    re.compile('palmolive\\s*(.*)', re.IGNORECASE): 'Palmolive',

    re.compile('panna\\s*crema\\s*(.*)', re.IGNORECASE): 'PannaCrema',

    re.compile('paragon shaving\\s*(.*)', re.IGNORECASE): 'Paragon Shaving',

    re.compile('ph[oe]+nix\\s*(?:&(?:amp;|)|and|n)\\s*beau\\s*(.*)', re.IGNORECASE): 'Phoenix and Beau',

    re.compile('phoenix artisan accoutrements\\s*(.*)', re.IGNORECASE): 'Phoenix Artisan Accoutrements',
    re.compile('paa\\b\\s*(.*)', re.IGNORECASE): 'Phoenix Artisan Accoutrements',

    re.compile('pr[ée] de provence\\s*(.*)', re.IGNORECASE): 'Pré de Provence',

    re.compile('pro(?:raso|saro)\\s*(.*)', re.IGNORECASE): 'Proraso',

    re.compile('pinnacle grooming\\s*(.*)', re.IGNORECASE): 'Pinnacle Grooming',

    re.compile('razorock\\s*(.*)', re.IGNORECASE): 'RazoRock',

    re.compile('red house farms\\s*(.*)', re.IGNORECASE): 'Red House Farms',
    re.compile('(?:u/|)grindermonk(?:\'|&#39;|’|)s?\\s*(.*)', re.IGNORECASE): 'Red House Farms',

    re.compile('reef point\\s*(?:soaps?)\\s*(.*)', re.IGNORECASE): 'Reef Point Soaps',

    re.compile('saponificio\\s*varesino\\s*(.*)', re.IGNORECASE): 'Saponificio Varesino',
    re.compile('sv\\b\\s*(.*)', re.IGNORECASE): 'Saponificio Varesino',

    re.compile('seaforth!?\\s*(.*)', re.IGNORECASE): 'Seaforth!',

    re.compile('shannon(?:\'|&#39;|’|)s soaps\\s*(.*)', re.IGNORECASE): 'Shannon\'s Soaps',

    re.compile('s\\s*h\\s*a\\s*v\\s*e.{0,4}d\\s*a\\s*n\\s*d\\s*y\\s*(.*)', re.IGNORECASE): 'SHAVE DANDY',

    re.compile('siliski soaps\\s*(.*)', re.IGNORECASE): 'Siliski Soaps',

    re.compile('soap commander\\s*(.*)', re.IGNORECASE): 'Soap Commander',

    re.compile('some irish guy(?:\'|&#39;|’|)s\\s*(.*)', re.IGNORECASE): 'Some Irish Guy\'s',

    re.compile('southern witchcrafts?\\s*(.*)', re.IGNORECASE): 'Southern Witchcrafts',
    re.compile('sw\\b\\s*(.*)', re.IGNORECASE): 'Southern Witchcrafts',
    re.compile('Australian Private Reserve/Southern Witchcrafts\\s*(.*)', re.IGNORECASE): 'Southern Witchcrafts',
    re.compile('southern witchcrafts\\s*/\\s*apr\\b\\s*(.*)', re.IGNORECASE): 'Southern Witchcrafts',

    re.compile('spearhead\\s*(?:(?:shaving|soap)\\s*(?:company|co.?|)|)\\s*(.*)', re.IGNORECASE): 'Spearhead Shaving Company',

    re.compile('sp[ei]{2}c?k\\s*(.*)', re.IGNORECASE): 'Speick',

    re.compile('st[ei]rl[ei]ng\s*(?:soap\s*(?:company|co\\.?|)|)(.*)', re.IGNORECASE): 'Stirling Soap Co.',

    re.compile('story\\s*book soap\\s*works\\s*(.*)', re.IGNORECASE): 'Storybook Soapworks',
    re.compile('sbsw\\b\\s*(.*)', re.IGNORECASE): 'Storybook Soapworks',
    re.compile('story\\s*book soap\\s*works\\s*[&/]\\s*ap\\s*r(?:eserve|\\b)(.*)', re.IGNORECASE): 'Storybook Soapworks',

    re.compile('(?:the|)\\s*sudsy soapery\\s*(.*)', re.IGNORECASE): 'The Sudsy Soapery',

    re.compile('summer break\\s*(?:soap\w+|)\\s*(.*)', re.IGNORECASE): 'Summer Break Soaps',
    re.compile('sbs\\b\\s*(.*)', re.IGNORECASE): 'Summer Break Soaps',

    re.compile('talbot\\s*(?:shaving|)\\s*(.*)', re.IGNORECASE): 'Talbot Shaving',

    re.compile('tallow\\s*(?:\\+|&(?:amp;|)|and)\\s*steel\\s*(.*)', re.IGNORECASE): 'Tallow + Steel',
    re.compile('t\\s*(?:\\+|&(?:amp;|)|and)\\s*s\\b\\s*(.*)', re.IGNORECASE): 'Tallow + Steel',

    re.compile('taylor of old bond st\S*\\s*(.*)', re.IGNORECASE): 'Taylor of Old Bond Street',
    re.compile('tobs\\b\\s*(.*)', re.IGNORECASE): 'Taylor of Old Bond Street',

    re.compile('tcheon fung sing\\s*(.*)', re.IGNORECASE): 'Tcheon Fung Sing',
    re.compile('tfs\\b\\s*(.*)', re.IGNORECASE): 'Tcheon Fung Sing',

    re.compile('valobra\\b\\s*(.*)', re.IGNORECASE): 'Valobra',

    re.compile('west coast shaving\\s*(.*)', re.IGNORECASE): 'West Coast Shaving',
    re.compile('wcs\\b\\s*(.*)', re.IGNORECASE): 'West Coast Shaving',

    re.compile('west of olympia\\s*(.*)', re.IGNORECASE): 'West of Olympia',

    re.compile('wholly kaw\\s*(.*)', re.IGNORECASE): 'Wholly Kaw',
    re.compile('wk\\b\\s*(.*)', re.IGNORECASE): 'Wholly Kaw',

    re.compile('wickham\\s(?:soap co.?|)\\s*(.*)', re.IGNORECASE): 'Wickham Soap Co.',

    re.compile('william(?:\'|&#39;|’|)s\\s(?:mug soap|)\\s*(.*)', re.IGNORECASE): 'William\'s Mug Soap',

    re.compile('zingari\\s*(?:mann?|)\\s*(.*)', re.IGNORECASE): 'Zingari Man',
    re.compile('barrister\\s*(?:&(?:amp;|)|and|n)\\s*mann/zingari\\s*(.*)', re.IGNORECASE): 'Zingari Man',
    re.compile('zingari\\s*(?:man|)\\s*/\\s*b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\s*(.*)', re.IGNORECASE): 'Zingari Man',
    re.compile('b\\s*(?:&(?:amp;|)|\\+|a)\\s*m\\s*/\\s*zingari\\s*(?:man|)\\s*(.*)', re.IGNORECASE): 'Zingari Man',

    re.compile('k[ae]rosene\\.*\\s*(.*)', re.IGNORECASE): 'kerosene',
    re.compile('homemade\\s+[a-z\\s\\(\\)]*?soap\\s*(.*)', re.IGNORECASE): '(homemade)',
}

