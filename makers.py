#!/usr/bin/env python3

import re

_any_and = '\\s*(?:&(?:amp;|)|and|\+|/|×|x|-)\\s*'
_apostophe = '(?:\'|&#39;|’|)'
_opt_company = '\\s*(?:company|co\\.?|)\\s*'

_maker_pats = {
    # known soapmakers
    'abbate y la mantia': 'Abbate y la Mantia',

    'acqua di parma': 'Acqua di Parma',

    'apex alchemy\\s*(?:soaps?|shaving|)': 'Apex Alchemy Soaps',

    'ariana' + _any_and + 'evans' + _any_and + 'gr[ea]y matter': 'Ariana & Evans',
    'ariana' + _any_and + 'evans\\s*/?\\s*the club': 'Ariana & Evans',
    '@?ariana\\.evans\\.thebrand': 'Ariana & Evans',
    'arian+a' + _any_and + 'evans': 'Ariana & Evans',

    'arko\\b': 'Arko',

    'archaic alchemy': 'Archaic Alchemy',

    'arran\\b(?: aromatics|sense of scotland|)': 'Arran',

    '@arsenalgrooming': 'Arsenal Grooming',
    'aresenal(?: grooming|)': 'Arsenal Grooming',

    '(?:the |)artisan soap shop(?:pe|)': 'The Artisan Soap Shoppe',

    'asylum(?: shave works|)': 'Asylum Shave Works',

    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'mammoth\\s*(?:soaps?|)': 'Mammoth Soaps',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'noble otter': 'Noble Otter',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'southern witchcrafts': 'Southern Witchcrafts',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'story\\s*br?ook soap\\s*works': 'Storybook Soapworks',
    '@australianprivatereserve': 'Australian Private Reserve',
    '(?:australian private|ap) reserve': 'Australian Private Reserve',

    'ballenclaugh': 'Ballenclaugh',

    'barbasol': 'Barbasol',

    'barbus\\b': 'Barbus',

    'b\\s*(?:&(?:amp;|)|\\+|a)\\s*m' + _any_and + 'zingari(?: man|)': 'Zingari Man',
    'barrister' + _any_and + 'mann' + _any_and + 'zingari(?: man|)': 'Zingari Man',
    'barri?sters?' + _any_and + 'mann?': 'Barrister and Mann',
    'barrister' + _apostophe + 's? (?=reserve)': 'Barrister and Mann',

    'baume?\\.be': 'BAUME.BE',

    'black\\s*ship\\s(?:grooming\\s*(?:co\\.?|)|)': 'Black Ship Grooming Co.',

    '(?:the |)bluebeard' + _apostophe + 's revenge': 'The Bluebeards Revenge',

    'the body shop': 'The Body Shop',

    'brutalt bra(?: barber\w+|)': 'Brutalt Bra Barbersåpe',

    'bufflehead(?: soap' + _opt_company + '|)': 'Bufflehead',

    'bundubeard': 'Bundubeard',

    'c\\.?\\s*o\\.?\\s*bigelow': 'C.O. Bigelow',

    'capt(?:ain|) fawcett(?: limited|ltd\\.?|)': 'Captain Fawcett Limited',

    'captain' + _apostophe + 's choice': 'Captain\'s Choice',

    'castle forbes': 'Castle Forbes',

    '@catiesbubbles' + _any_and + '@talbotshaving': 'Talbot Shaving',
    'catie' + _apostophe + 's bubbles' + _any_and + 'talbot(?: shaving|)': 'Talbot Shaving',
    'sfws\\s*/\\s*catie' + _apostophe + 's bubbles': 'Catie\'s Bubbles',
    'Carnavis' + _any_and + 'Richardson\\s*/\\s*Catie' + _apostophe + 's Bubbles': 'Catie\'s Bubbles',
    '@catiesbubbles': 'Catie\'s Bubbles',
    '[ck]att?i' + _apostophe + 'e' + _apostophe + 's bubbles': 'Catie\'s Bubbles',

    'cbl soaps': 'CBL Soaps',

    'cella': 'Cella',

    'central texas (?:soaps?|)': 'Central Texas Soaps',

    'chicago groom\\w+' + _opt_company + '(?:\\((?:form(?:er|al)ly|)\\s*oleo\\b[^)]*\\)|)' + _any_and + 'wcs': 'West Coast Shaving',
    'chicago groom\\w+' + _opt_company + '(?:\\((?:formerly|formally|)\\s*oleo\\b[^)]*\\)|)': 'Chicago Grooming Co.',
    'oleo\\s*(?:soapworks|soap|)': 'Chicago Grooming Co.',

    'zoologist(?: perfumes|)\\s*/\\s*chiseled face': 'Chiseled Face',
    'chiseled face\\s*/\\s*zoologist(?: perfumes|)': 'Chiseled Face',
    '@chiseled_face': 'Chiseled Face',
    'chiseled face(?: groomatorium|)': 'Chiseled Face',

    'classic edge': 'Classic Edge',

    'clubman pinaud': 'Clubman Pinaud',

    'cold river\\s*(?:soap\\s*works)': 'Cold River Soap Works',

    'vintage colgate': 'Colgate',
    'colgate': 'Colgate',

    '(?:col(?:onel|\\.|)\\s*|)conk': 'Col. Conk',

    'cooper' + _any_and + 'french': 'Cooper & French',

    'crabtree' + _any_and + 'evelyn': 'Crabtree & Evelyn',

    'cremo': 'Cremo',

    'cyril r\\.? salter': 'Cyril R. Salter',

    'd\\.?\\s*r\\.?\\s*harris': 'D.R. Harris',

    'd(?:ai|ia)sho\\s*(?:shaving(?:products|)|soaps?|)': 'Daisho Shaving Products',

    'dalane? (?:d' + _apostophe + '|)men': 'Dalan',
    'dalane?\\b': 'Dalan',

    'dindi naturals': 'Dindi Naturals',

    '@declarationgrooming' + _any_and + '@chatillonlux': 'Declaration Grooming',
    'Chatillon Lux' + _any_and + 'Declaration Grooming': 'Declaration Grooming',
    'Declaration Grooming' + _any_and + '(?:Chat+il+on Lux|cl\\b)': 'Declaration Grooming',
    'Declaration Grooming' + _any_and + 'Maggard(?: Razors|)': 'Declaration Grooming',
    'Maggard Razors' + _any_and + 'Declaration Grooming': 'Declaration Grooming',
    'l' + _any_and + 'l grooming': 'Declaration Grooming',

    'dr.? joh?n' + _apostophe + 's': 'Dr. Jon\'s',

    'dr\\.? selby': 'Dr. Selby',

    'edwin jagg[ea]r': 'Edwin Jagger',

    'eleven': 'Eleven Shaving',

    'esbjerg': 'Esbjerg',

    'ethos(?: grooming(?: essentials|)|)': 'ETHOS',

    'jabon\\s*man eufros': 'Eufros',
    'eufu?ros': 'Eufros',

    'extr[òo]’?(?: cosmesi|\\b)': 'Extrò Cosmesi',

    'executive shaving': 'Executive Shaving',

    'face fat(?: shaving|)': 'Face Fat',

    'fenom[ei]no\\s*(?:shave|)': 'Fenomeno Shave',

    'fine accoutrements': 'Fine Accoutrements',

    'first canadian\\s*(?:shav(?:e|ing)(?: soap|)' + _opt_company + '|)': 'First Canadian Shave',

    '@first_line_shave': 'First Line Shave',
    'first line shave': 'First Line Shave',

    'floris\\s*(?:(?:of|)\\s*london|)': 'Floris London',

    'fitjar\\s*(?:islands?|)': 'Fitjar Islands',

    'fuzzy\\s*face(?: soaps|)': 'Fuzzyface Soaps',

    'geo(?:rge|\\.|)\\s*f?\\.? trumper': 'Geo. F. Trumper',

    '@gentlemansnod / @worldofzaharoff': 'Gentleman\'s Nod',
    '@gentlemansnod': 'Gentleman\'s Nod',
    'gentlem[ae]n' + _apostophe + 's? nod': 'Gentleman\'s Nod',

    'gillette': 'Gillette',

    'golden beards': 'Golden Beards',

    'goldex': 'Goldex',

    '(?:the|)\\s*goodfella' + _apostophe + 's' + _apostophe + '\\s*(?:smile|)': 'The Goodfellas\' Smile',

    'grooming dep[at]\\S*': 'Grooming Department',

    'haslinger': 'Haslinger',

    'hecho sma': 'Hecho SMA',

    '@henrietvictoria': 'Henri et Victoria',
    'henri et victoria': 'Henri et Victoria',

    'heritage hill(?: shave' + _opt_company + '|)': 'Heritage Hill Shave Company',

    'high desert soap' + _opt_company: 'High Desert Soap Co.',

    'highland springs? soap' + _opt_company + _any_and + '(?:australian private|ap) reserve': 'Highland Springs Soap Company',
    '@highlandspringssoap': 'Highland Springs Soap Company',
    'highland springs? soap' + _opt_company: 'Highland Springs Soap Company',
    'highland springs?': 'Highland Springs Soap Company',

    '(?:the |)holy black': 'The Holy Black',

    'mammoth\\s*(?:soaps?|)' + _any_and + 'ap(?:\\s*reserve|r\\b)': 'House of Mammoth',
    '@?mammoth\\s*(?:soaps?|)': 'House of Mammoth',
    'house of mammoth': 'House of Mammoth',

    'hub city\\s*(?:soap' + _opt_company + '|)': 'Hub City Soap Company',

    'imperial\\s*(?:barber (?:products|grade products?|)|)': 'Imperial Barber',

    'ing[áa] saboaria artesanal': 'Ingá Saboaria Artesanal',
    'mythos': 'Ingá Saboaria Artesanal',

    'j' + _any_and + 'e atkinsons?': 'J & E Atkinsons',

    'los jabones de joserra': 'Los Jabones de Joserra',

    '(?:karo|kapo|каро)\\b': 'Каро (Karo)',

    'kell' + _apostophe + 's original(?: soap|)': 'Kell\'s Original',

    'Kieh?l' + _apostophe + 's\\b': 'Kiehl\'s',

    'klar(?: seifen?| soap|\\b)': 'Klar Seifen',

    'le labo\\b(?: inc\\.?|)': 'Le Labo Inc.',

    'lakewood soap' + _opt_company: 'Lakewood Soap Company',

    'lather bro(?:thers|s)\\.?': 'Lather Bros.',

    'like grandpa': 'Like Grandpa',

    'lisa' + _apostophe + 's natural herbal creations': 'Lisa\'s Natural Herbal Creations',

    'long rifle(?:soaps?' + _opt_company + '|)': 'Long Rifle Soap Company',
    
    '(?:the |)(?:los angeles|la) shaving(?: soap|)' + _opt_company: 'Los Angeles Shaving Soap Co.',

    'lotus eater': 'Lotus Eater',

    'lucky tiger': 'Lucky Tiger',

    'macduff' + _apostophe + 's? soap co\\.?': 'MacDuff\'s Soap Company',

    'maggard razors \\((?:through the fire fine craft|ttffc)\\)': 'Maggard Razors',
    'mama bear': 'Mama Bear',

    'maol\\s*(?:grooming|)' + _any_and + 'talbot(?: shaving|)': 'Talbot Shaving',
    'maol\\s*(?:grooming|)': 'Maol Grooming',

    'martin de candre': 'Martin de Candre',

    'matti lindholm(?: shaving(?: supplies|)|)': 'Matti Lindholm Shaving Supplies',

    'mei(?:ß|ss)ner tremonia': 'Meißner Tremonia',

    '@mickeyleesoapworks': 'Mickey Lee Soapworks',
    'micke?y lee\\b(?: soap\w+|)': 'Mickey Lee Soapworks',

    'midnight' + _any_and + 'two': 'Midnight & Two',

    'mike' + _apostophe + 's natural(?: soaps?|)': 'Mike\'s Natural Soaps',

    'mi[rt]chell' + _apostophe + 's\\s*(?:wool fat|)': 'Mitchell\'s Wool Fat',

    'mondial\\b(?: 1908|)': 'Mondial 1908',

    'moon soaps?': 'Moon Soaps',

    'murphy' + _any_and + 'daughters?': 'Murphy & Daughters',

    'murphy' + _any_and + 'mcneil': 'Murphy and McNeil',

    'mystic water\\s*(?:soaps?|)': 'Mystic Water Soap',

    'nivea\\b': 'Nivea',

    'nob(?:le|el) otter' + _any_and + '(?:australian private|ap)\\s*r(?:eserve|\\b)': 'Noble Otter',
    '@?noble_otter': 'Noble Otter',
    'nob(?:le|el) otter': 'Noble Otter',
    'apr' + _any_and + 'no': 'Noble Otter',
    'no' + _any_and + 'apr': 'Noble Otter',

    'nordic shaving' + _opt_company: 'Nordic Shaving Company',

    'oaken\\b(?: lab|)': 'Oaken Lab',

    'oatcake(?: shaving|)(?: soaps?|)': 'Oatcake Soaps',

    'obsessive soap(?:s|\\s+perfect\w+|)': 'Obsessive Soap Perfectionist',
    'osp(?:\\s*soaps?|\\b)': 'Obsessive Soap Perfectionist',

    'l' + _apostophe + 'occitane': 'l\'Occitane',

    'officina di (?:santa maria|s\\.?m\\.?) novella': 'Officina di Santa Maria Novella',
    'santa maria novella': 'Officina di Santa Maria Novella',

    'ogalalla(?: bay rum|)': 'Ogallala Bay Rum',
    'ogallala(?: bay rum|)': 'Ogallala Bay Rum',

    'vintage shulton old spice': 'Old Spice',
    'old spice': 'Old Spice',

    '1000' + _any_and + '1 seife': '1000&1 Seife',

    'oz shaving' + _opt_company: 'Oz Shaving Co.',

    'p\\.?160': 'P.160',

    'palmolive': 'Palmolive',

    'panee\\b(?: soaps|)': 'Panee Soaps',

    'panna\\s*crema': 'PannaCrema',

    'paragon shaving': 'Paragon Shaving',

    'park avenue': 'Park Avenue',

    'l' + _apostophe + 'asinerie de la vioune' + _any_and + 'le p[èeé]re lucien': 'Le Père Lucien',
    'le p[èeé]re luciene?': 'Le Père Lucien',

    'pereiras?\\b(?:shavery|)': 'Pereira Shavery',

    'ph[oe]+nix' + _any_and + 'beau': 'Phoenix and Beau',

    'portus cale': 'Portus Cale',

    'pr[éeè] de provence': 'Pré de Provence',

    'pro(?:raso|saro)': 'Proraso',
    'poraso': 'Proraso',

    'pinnacle grooming': 'Pinnacle Grooming',

    'razor emporium': 'Razor Emporium',

    'red house farms?\\s*\\(\\s*\\[u/grindermonk\\]\\([^\\)]+\\)+' + _apostophe + 's?\\)?': 'Red House Farm',
    'red house farms?(?: \\(\\s*u?/?grindermonk\\)?' + _apostophe + 's?\\)|)': 'Red House Farm',
    '(?:u/|)grindermonk' + _apostophe + 's?': 'Red House Farm',

    'reef point(?: soaps?|)': 'Reef Point Soaps',

    'River Valley Trading': 'River Valley Trading',

    'st\\.?\\s*james(?: of london|)': 'St. James of London',

    'sapone d[ei] paolo': 'Sapone di Paolo',

    'saponificio\\s*va?r[ei]sino': 'Saponificio Varesino',

    'scentsy(?:cream shave soap|)': 'Scentsy',
    
    'scottish fine soaps': 'Scottish Fine Soaps',

    'seat?forth!?': 'Seaforth!',

    'shannon' + _apostophe + 's soaps': 'Shannon\'s Soaps',

    's\\s*h\\s*a\\s*v\\s*e.{0,4}d\\s*a\\s*n\\s*d\\s*y': 'SHAVE DANDY',

    'Signature Soaps': 'Signature Soaps',

    'siliski\\s*(?:soaps|soapworks|)': 'Siliski Soaps',

    'soap commander': 'Soap Commander',

    'some irish guy' + _apostophe + 's': 'Some Irish Guy\'s',

    'southern witchcrafts' + _any_and + 'ap(?: reserve|r\\b)': 'Southern Witchcrafts',
    'southern\\s*witchcraf?ts?': 'Southern Witchcrafts',
    'southern\\s*witchworks?': 'Southern Witchcrafts',

    'spartium natural cosmetics': 'Spartium Natural Cosmetics',

    'spearhead\\s*(?:(?:shaving|soap)' + _opt_company + '|)': 'Spearhead Shaving Company',

    'sp[ei]{2}c?k': 'Speick',

    'chatillon lux' + _any_and + 'story\\s*book soap\\s*works': 'Storybook Soapworks',
    'story\\s*book soap\\s*works\\s*[&/]\\s*ap\\s*r(?:eserve|\\b)': 'Storybook Soapworks',
    'story\\s*book soap\\s*works': 'Storybook Soapworks',
    'story\\s*book': 'Storybook Soapworks',

    'strike gold(?: shaving| shave|)': 'Strike Gold Shave',

    'stubble buster': 'Stubble Buster',

    'stuga\\b': 'Stuga',

    'chatillon lux' + _any_and + '(?:the|)\\s*sudsy soap[ae]ry?': 'The Sudsy Soapery',
    '(?:the|)\\s*sudsy soap[ae]ry?\\s*[/&]\\s*chatillon lux': 'The Sudsy Soapery',
    '(?:the|)\\s*sudsy soap[ae]ry?': 'The Sudsy Soapery',

    'summer break(?: soaps|)': 'Summer Break Soaps',

    'svoboda': 'Svoboda',
    'свобода': 'Svoboda',

    '@talbotshaving @maolgrooming': 'Talbot Shaving',
    '@talbotshaving': 'Talbot Shaving',
    'talbot\\s*(?:shaving|)': 'Talbot Shaving',

    'tabac\\b': 'Tabac',

    'taconic\\b(?: shave|)': 'Taconic Shave',

    'tallow' + _any_and + 'steel': 'Tallow + Steel',

    'taylor' + _apostophe + 's? of old bond st\S*': 'Taylor of Old Bond Street',
    'tobs\\b': 'Taylor of Old Bond Street',

    'tcheon? fung sing': 'Tcheon Fung Sing',

    'the club\\b(?:/a&e|)': 'Ariana & Evans',
    'a&e[ /]the club': 'Ariana & Evans',

    '345 soap' + _opt_company: '345 Soap Co.',

    'through the fire fine craft': 'Through the Fire Fine Craft',

    'tiki bar soaps?': 'Tiki Bar Soaps',

    'la toj[ao]\\b': 'La Toja',

    'truefitt?' + _any_and + 'hill': 'Truefitt & Hill',

    'turtleship shave' + _opt_company: 'Turtleship Shave Co.',

    'uncle jon' + _apostophe + 's(?: soap|)': 'Uncle Jon\'s',

    'urth\\b(?: skin solutions(?: for men)|)': 'Urth Skin Solutions',

    'valobra\\b': 'Valobra',

    'Van Yulay': 'Van Yulay',

    'viking(?: (?:shaving |)soap|)\\b': 'Viking Soap & Cosmetic',

    'vito' + _apostophe + 's': 'Vitos',

    'west coast shaving' + _any_and + 'chicago groom\w+' + _opt_company + '(?:\((?:form(?:er|al)ly\\s+|)oleo\\b[^)]*\)|)': 'West Coast Shaving',
    'west coast shaving' + _any_and + 'oleo\\b\\s*(?:soap\\s*works|soap)': 'West Coast Shaving',
    'west coast shaving' + _any_and + 'catie' + _apostophe + 's bubbles': 'West Coast Shaving',
    'west coast shaving': 'West Coast Shaving',

    'west of olympia': 'West of Olympia',

    'whispers from the woods': 'Whispers from the Woods',

    'wild magnolia soaps' + _apostophe: 'Wild Magnolia Soaps',

    'chatillon lux' + _any_and + 'wholly kaw': 'Wholly Kaw',
    'wholly kaw' + _any_and + 'chatillon lux': 'Wholly Kaw',
    'wholly kaw' + _any_and + 'mammoth soaps': 'Wholly Kaw',
    'wholly kaw' + _any_and + 'pasteur' + _apostophe + 's? pharmacy': 'Wholly Kaw',
    'wholly [kl]aw': 'Wholly Kaw',

    'wickham(?: (?:soap|shave)' + _opt_company + '|)': 'Wickham Soap Co.',

    'william' + _apostophe + 's(?: mug soap| shave soap|)': 'Williams Mug Soap',

    'wood\\s*box(?:\\s*soap|)': 'Wood Box Soap',

    'zingar[io]\\s*(?:man|)' + _any_and + 'barrister' + _any_and + 'mann': 'Zingari Man',
    'zingar[io]\\s*(?:man|)' + _any_and + 'b\\s*(?:&(?:amp;|)|\\+|a|)\\s*m\\b': 'Zingari Man',
    'zingari\\s*(?:man|)' + _any_and + 'wcs\\b': 'Zingari Man',
    'zingar[io]\\s*(?:mann?|)': 'Zingari Man',
}

# these also make hardware
_hw_maker_pats = {
    '(?:the |)art of shaving': 'Art of Shaving',
    '@declarationgrooming': 'Declaration Grooming',
    'declaration\\s*(?:grooming|)': 'Declaration Grooming',
    '(?:gb |)kent': 'Kent',
    'maggard' + _apostophe + 's?\\s*(?:razors?|)': 'Maggard Razors',
    'm[üu]hle': 'Mühle',
    'crown king': 'Phoenix Artisan Accoutrements',
    'phoenix artisan accoutrements': 'Phoenix Artisan Accoutrements',
    'phoenix shaving': 'Phoenix Artisan Accoutrements',
    'razorock': 'RazoRock',
    'rockwell\\b(?: razors|)': 'Rockwell Razors',
    '@stirlingsoap': 'Stirling Soap Co.',
    'st[ei]rl[ei]ng\s*(?:soap(?:works|)' + _opt_company + '|)(.*)': 'Stirling Soap Co.',
    'summer break\\s*(?:soap\w*|)': 'Summer Break Soaps',
    'west coast shaving': 'West Coast Shaving',
    'wet shaving products': 'Wet Shaving Products',
    'wild west shaving' + _opt_company: 'Wild West Shaving Co.',
}

_other_pats = {
    '(?:friend' + _apostophe + 's|) *homemade\\s+[a-z\\s\\(\\)]*?soap\\.?': '(homemade)',
    'mug of many samples': 'Mug of many samples',
    'tester(?: soap|)': 'Tester',
    'test batch': 'Tester',
    'scent tester': 'Tester',

    # things that aren't really "lather," but for some reason got used anyway
    'k[ae]rosene\\.*': 'kerosene',
}

_abbrev_pats = {
    # abbreviations or more common words
    'apr': 'Australian Private Reserve',
    'b\\s*(?:&(?:amp;|)|\\+|a|-|)\\s*m': 'Barrister and Mann',
    'cb': 'Catie\'s Bubbles',
    'cbl': 'CBL Soaps',
    'c' + _any_and + 'e': 'Crabtree & Evelyn',
    'cf': 'Chiseled Face',
    'crsw': 'Cold River Soap Works',
    'esc': 'Executive Shaving',
    'fcs': 'First Canadian Shave',
    'l' + _any_and + 'l': 'Declaration Grooming',
    'hssc': 'Highland Springs Soap Company',
    'thb': 'The Holy Black',
    'lnhc': 'Lisa\'s Natural Herbal Creations',
    'lassco?': 'Los Angeles Shaving Soap Co.',
    'mlsw?': 'Mickey Lee Soapworks',
    'mike' + _apostophe + 's': 'Mike\'s Natural Soaps',
    'mwf': 'Mitchell\'s Wool Fat',
    'm' + _any_and + 'm\\b': 'Murphy & McNeil',
    'pdp': 'Pré de Provence',
    'sv': 'Saponificio Varesino',
    'a' + _any_and + 'e': 'Ariana & Evans',
    'sjol': 'St. James of London',
    'sdp': 'Sapone di Paolo',
    'sw': 'Southern Witchcrafts',
    'sbsw': 'Storybook Soapworks',
    't' + _any_and + 's': 'Tallow + Steel',
    'tfs': 'Tcheon Fung Sing',
    'ttffc': 'Through the Fire Fine Craft',
    'wk': 'Wholly Kaw',
    'wms': 'William\'s Mug Soap',
    # hardware vendors
    'aos': 'Art of Shaving',
    'dg' + _any_and + 'cl': 'Declaration Grooming',
    'dg': 'Declaration Grooming',
    'fine': 'Fine Accoutrements',
    'n\\.?\\s*o\\.?': 'Noble Otter',
    'paa': 'Phoenix Artisan Accoutrements',
    'rr': 'RazoRock',
    'sbs': 'Summer Break Soaps',
    'wcs': 'West Coast Shaving',
    'wsp': 'Wet Shaving Products',
    'wwsc': 'Wild West Shaving Co.',
}

# TODO special category for more complicated patterns,
# e.g. 'wms\\s*[_\*]*\\s*$' for Williams (single scent makes misidentification more likely)

_ending = '(?:\\.|' + _apostophe + '(?<! )s|)\\s*(.*)'
_compiled_pats = None
_compiled_hw = None
_compiled_other = None
_compiled_abbrev = None

def _compile():
    global _compiled_pats, _compiled_abbrev, _compiled_hw, _compiled_other
    if _compiled_pats is None:
        _compiled_pats = { }
        for pattern in _maker_pats:
            _compiled_pats[re.compile(pattern + _ending, re.IGNORECASE)] = _maker_pats[pattern]
        _compiled_hw = { }
        for pattern in _hw_maker_pats:
            _compiled_hw[re.compile(pattern + _ending, re.IGNORECASE)] = _hw_maker_pats[pattern]
        _compiled_other = { }
        for pattern in _other_pats:
            _compiled_other[re.compile(pattern + _ending, re.IGNORECASE)] = _other_pats[pattern]
        _compiled_abbrev = { }
        for pattern in _abbrev_pats:
            _compiled_abbrev[re.compile('\\b' + pattern + '\\b' + _ending, re.IGNORECASE)] = _abbrev_pats[pattern]


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
            return { 'match': result, 'name': _compiled_pats[pattern], 'abbreviated': False }
    saved_full_hw = None
    for pattern in _compiled_hw:
        result = pattern.match(text)
        if result:
            saved_full_hw = { 'match': result, 'name': _compiled_hw[pattern], 'abbreviated': False }
    for pattern in _compiled_other:
        result = pattern.match(text)
        if result:
            return { 'match': result, 'name': _compiled_other[pattern], 'abbreviated': False }
    for pattern in _compiled_abbrev:
        result = pattern.match(text)
        if result:
            return { 'match': result, 'name': _compiled_abbrev[pattern], 'abbreviated': True }
    return saved_full_hw


def searchMaker( text: str ):
    """ Searches for a maker through the entire provided text. Will preferably
        return a match at the beginning of a line (less non-alphanumeric
        chars). But will also return a match in the middle of a line. Returns
        a dict with these attributes:
            'match': the result object from Pattern.match()
            'name': the standard maker name
            'first': boolean value indicating if the match is the first word on a line
            'abbreviated': boolean value indicating an abbreviation match instead of a spelled out maker name
    """
    # TODO we have a real problem with Noble Otter's abbreviation matching the word "no"
    # this might also be a problem with other two or three letter abbreviations
    _compile()
    saved_full_hw = None
    rpos = len(text)
    multiline = text.find("\n") >= 0

    result = _subSearch(text, _compiled_pats)
    if result:
        rpos = result['match'].start()
    if not result or multiline:
        saved_full_hw = _subSearch(text, _compiled_hw)
        next_rs = _subSearch(text, _compiled_other)
        if next_rs and next_rs['match'].start() < rpos:
            result = next_rs
            rpos = result['match'].start()
    if not result or multiline:
        next_rs = _subSearch(text, _compiled_abbrev)
        if next_rs and next_rs['match'].start() < rpos:
            result = next_rs
            rpos = result['match'].start()
            result['abbreviated'] = True
    if result:
        return result
    else:
        return saved_full_hw


def _subSearch( text: str, pat_dict: dict ):
    best_match = None
    best_pos = len(text)
    best_begins_line = False
    for pattern in pat_dict:
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
            if (begin_line and not best_begins_line) or (begin_line == best_begins_line and result.start() < best_pos):
                best_match = result
                best_pos = result.start()
                best_begins_line = begin_line
    if best_match:
        return {
            'match': best_match,
            'name': pat_dict[best_match.re],
            'first': best_begins_line,
            'abbreviated': False
        }
    return None
