#!/usr/bin/env python3

import re

_any_and = '\\s*(?:&(?:amp;|)|and|\\+|/|×|x|X|-)\\s*'
_apostrophe = '(?:\'|&#39;|’|)'
_opt_company = '\\s*(?:company|co\\.?|)\\s*'

_maker_pats = {
    # known soapmakers
    'a\\.?\\s*j\\.? murray' + _apostrophe + 's(?: shaving(?: soap|)|)': 'A. J. Murray\'s',

    'abbate y la mantia': 'Abbate y la Mantia',

    'acca kappa': 'Acca Kappa',

    'ach brito': 'Ach Brito',

    'ac?qua di parma': 'Acqua di Parma',

    'alphy' + _any_and + 'becs': 'Alphy & Becs',

    'antica barberia': 'Antica Barberia',

    'apex alchemy\\s*(?:soaps?|shaving|)': 'Apex Alchemy Soaps',

    'ariana' + _any_and + 'evans' + _any_and + 'gr[ea]y matter': 'Ariana & Evans',
    '(?:ariana' + _any_and + 'evans|a' + _any_and + 'e)\\s*(?:/?|-)\\s*"?(?:the |)club"?': 'Ariana & Evans',
    'the club\\s*/\\s*ariana' + _any_and + 'evans': 'Ariana & Evans',
    '@?ariana\\.evans\\.thebrand': 'Ariana & Evans',
    'arian+a' + _any_and + 'evans': 'Ariana & Evans',
    'ariana\\s*evans': 'Ariana & Evans',

    'arko\\b': 'Arko',

    'archaic alchemy': 'Archaic Alchemy',

    'arran\\b(?: aromatics|sense of scotland|)': 'Arran',

    '@arsenalgrooming': 'Arsenal Grooming',
    'aresenal(?: grooming|)': 'Arsenal Grooming',

    '(?:the |)artisan soap shop(?:pe|)': 'The Artisan Soap Shoppe',

    'asylum(?: shave works|)': 'Asylum Shave Works',

    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'mammoth\\s*(?:soaps?|)': 'House of Mammoth',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'house of mammoth': 'House of Mammoth',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'noble otter': 'Noble Otter',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'southern witchcrafts': 'Southern Witchcrafts',
    '(?:australian private|ap)\\s*r(?:eserve|\\b)' + _any_and + 'story\\s*br?ook soap\\s*works': 'Storybook Soapworks',
    '@australianprivatereserve': 'Australian Private Reserve',
    '(?:australian private|ap) reserve': 'Australian Private Reserve',

    'aveeno': 'Aveeno',

    'aven[èe]': 'Avenè',

    'ballenclaugh': 'Ballenclaugh',

    'barbasol': 'Barbasol',

    'barbus\\b': 'Barbus',

    'b\\s*(?:&(?:amp;|)|\\+|a)\\s*m' + _any_and + 'zingari(?: man|)': 'Zingari Man',
    'barrister' + _any_and + 'mann' + _any_and + 'zingari(?: man|)': 'Zingari Man',
    'barri?sters?' + _any_and + 'mann?': 'Barrister and Mann',
    'barrister' + _apostrophe + 's? (?=reserve)': 'Barrister and Mann',

    'bartigan' + _any_and + 'stark': 'Bartigan & Stark',

    'baume?\\.be': 'BAUME.BE',

    'bear(?:skin|)' + _any_and + 'tunic': 'Bearskin & Tunic',

    'biobaza': 'Biobaza',

    'black\\s*ship\\s(?:grooming\\s*(?:co\\.?|)|)': 'Black Ship Grooming Co.',

    '(?:the |)blade' + _apostrophe + 's grim+': 'The Blades Grim',

    'blue devil shav(?:e|ing)' + _opt_company: 'Blue Devil Shave Co.',

    '(?:the |)bluebeard' + _apostrophe + 's revenge': 'The Bluebeards Revenge',

    'the body shop': 'The Body Shop',

    'boellis': 'Boellis',

    'boots': 'Boots',

    'brutalt bra(?: barber\w+|)': 'Brutalt Bra Barbersåpe',

    'bufflehead(?: soap' + _opt_company + '|)': 'Bufflehead',

    'b[ue]rma\\s*-?\\s*shave': 'Burma-Shave',

    'butterface': 'Butterface',

    '(?:the |)butterfly garden(?: soaps|)': 'The Butterfly Garden',

    'b[vu]lgari': 'Bvlgari',

    'c\\.?\\s*o\\.?\\s*bigelow': 'C.O. Bigelow',

    'capt(?:ain|) fawcett(?: limited|ltd\\.?|)': 'Captain Fawcett Limited',

    'captain' + _apostrophe + 's choice': 'Captain\'s Choice',

    'castle forbes': 'Castle Forbes',

    '@catiesbubbles' + _any_and + '@talbotshaving': 'Talbot Shaving',
    'catie' + _apostrophe + 's bubbles' + _any_and + 'talbot(?: shaving|)': 'Talbot Shaving',
    'sfws\\s*/\\s*catie' + _apostrophe + 's bubbles': 'Catie\'s Bubbles',
    'Carnavis' + _any_and + 'Richardson\\s*/\\s*Catie' + _apostrophe + 's Bubbles': 'Catie\'s Bubbles',
    '@catiesbubbles': 'Catie\'s Bubbles',
    '[ck]att?i' + _apostrophe + 'e' + _apostrophe + 's bubble' + _apostrophe + 's': 'Catie\'s Bubbles',

    'cbl (?:premium shave |)soaps?': 'CBL Soaps',

    'cella': 'Cella',

    'central (?:texas|tx) (?:soaps?|)': 'Central Texas Soaps',

    'chicago groom\\w+' + _opt_company + '(?:\\((?:form(?:er|al)ly|) *oleo *(?:soapworks|soaps?|)\\)?|)' + _any_and + 'wcs': 'West Coast Shaving',
    'chicago groom\\w+' + _opt_company + '(?:\\((?:formerly|formally|fr\\.?|) *oleo *(?:soapworks|soaps?|)\\)?|)': 'Chicago Grooming Co.',
    'oleo *(?:soapworks|soaps?|)' + _any_and + 'west coast shaving': 'West Coast Shaving',
    'oleo' + _any_and + '(?:that darn rob|tdr\\b|chisel' + _any_and + 'hound)': 'Chicago Grooming Co.',
    'oleo *(?:soapworks|soaps?|)' + _any_and + 'chicago grooming' + _opt_company: 'Chicago Grooming Co.',
    'oleo *(?:soapworks|soaps?|) *\\((?:now |)chicago grooming' + _opt_company + '\\)': 'Chicago Grooming Co.',
    'oleo *(?:soapworks|soaps?|grooming|)' + _opt_company: 'Chicago Grooming Co.',

    'zoologist(?: perfumes|)\\s*/\\s*chiseled face': 'Chiseled Face',
    'chiseled face\\s*/\\s*zoologist(?: perfumes|)': 'Chiseled Face',
    '@chiseled_face': 'Chiseled Face',
    'chise?led face(?: groomatorium|)': 'Chiseled Face',

    'classic edge': 'Classic Edge',

    '(?:the |)clovelly(?: soap' + _opt_company + '|)': 'The Clovelly Soap Co.',

    'clubman pinaud': 'Clubman Pinaud',

    'cold river\\s*(?:soap\\s*works)': 'Cold River Soap Works',

    'vintage colgate': 'Colgate',
    'colgate': 'Colgate',

    'col\\.? ichabod conk': 'Col. Conk',
    '(?:col(?:onel|\\.|)\\s*|)conk': 'Col. Conk',

    'cooper' + _any_and + 'french': 'Cooper & French',

    'crabtree' + _any_and + 'evelyn': 'Crabtree & Evelyn',

    'crafts?man soap' + _opt_company: 'Craftsman Soap Co.',

    'cremo': 'Cremo',

    'crescent city shave(?:works|)': 'Crescent City Shaveworks',

    'crowne?' + _any_and + 'crane': 'Crowne & Crane',

    'cyril *(?:r\\.? *|)salter(?: luxury shaving cream|)': 'Cyril R. Salter',

    'd\\.?\\s*r\\.?\\s*harris(?:' + _any_and + ' *co\\.?,? *ltd\\.?|)': 'D.R. Harris',

    'd(?:ai|ia)sho\\s*(?:shaving(?:products|)|soaps?|)': 'Daisho Shaving Products',

    'dalane? (?:d' + _apostrophe + '|)men': 'Dalan',
    'dalane?\\b': 'Dalan',

    'dalit(?: goods|)': 'Dalit Goods',

    'dapper dragon': 'Dapper Dragon',

    'dead\\s*sea\\s*shave': 'Dead Sea Shave',

    '@declarationgrooming' + _any_and + '@chatillonlux': 'Declaration Grooming',
    'Chatillon Lux' + _any_and + 'Declaration Grooming': 'Declaration Grooming',
    'Declaration(?: Grooming|)' + _any_and + '(?:Chat+il+on Lux|cl\\b)': 'Declaration Grooming',
    'DG' + _any_and + '(?:Chat+il+on Lux|cl\\b)': 'Declaration Grooming',
    'declaration grooming' + _any_and + 'maggard(?: *razors|' + _apostrophe + 's|)': 'Declaration Grooming',
    'maggard(?: *razors|' + _apostrophe + 's|)' + _any_and + 'declaration(?: grooming|)': 'Declaration Grooming',
    'l' + _any_and + 'l(?:/declaration|) grooming': 'Declaration Grooming',
    'l' + _any_and + 'l\\s*\\(declaration\\)(?: grooming|)': 'Declaration Grooming',

    'dindi naturals': 'Dindi Naturals',

    '(?:dr.?|doctor) bron+[eo]r' + _apostrophe + 's': 'Dr. Bronner\'s',

    '(?:dr.?|doctor) dittmar': 'Dr. Dittmar',

    '(?:dr.?|doctor) joh?n(?:' + _apostrophe + 's|)': 'Dr. Jon\'s',

    'dr.? k soap' + _opt_company: 'Dr K Soap Company',

    'dr\\.? selby': 'Dr. Selby',

    'eleven(?: shaving|)': 'Eleven Shaving',

    'elvado': 'Elvado',

    'esbjerg': 'Esbjerg',

    'esteem': 'Esteem',

    'ethos(?: grooming(?: essentials|)|)': 'ETHOS',

    'jabon\\s*man eufros': 'Eufros',
    'eufu?ros \\(jabonman\\)': 'Eufros',
    'eufu?ros by jabonman': 'Eufros',
    'eufu?ros': 'Eufros',
    'jabon\\s*man': 'Eufros',

    'extr[òo]’?(?: cosmesi|\\b)': 'Extrò Cosmesi',
    'extra cosmesi': 'Extrò Cosmesi',

    'executive shaving': 'Executive Shaving',

    'face fat(?: shaving|)': 'Face Fat',

    'fenom[ei]no\\s*(?:shave|)': 'Fenomeno Shave',

    'figaro': 'Figaro',

    'first canad(?:ian|a) *(?:shav(?:e|ing)(?: soap|)' + _opt_company + '|)': 'First Canadian Shave',

    '@first_line_shave': 'First Line Shave',
    'first line shave': 'First Line Shave',

    'fitjar\\s*(?:islands?|)': 'Fitjar Islands',

    'floris\\s*(?:(?:of|)\\s*london|)': 'Floris London',

    'free soap collective': 'Free Soap Collective',

    'fuzzy\\s*face(?: soaps|)': 'Fuzzyface Soaps',

    'g' + _any_and + 'g grooming': 'G&G Grooming',

    'geo(?:rge|\\.|)\\s*f?\\.? trumpe(?:r|ts)': 'Geo. F. Trumper',

    '@gentlemansnod / @worldofzaharoff': 'Gentleman\'s Nod',
    '@gentlemansnod': 'Gentleman\'s Nod',
    'gentlem[ae]n' + _apostrophe + 's? nod': 'Gentleman\'s Nod',
    'zaharoff': 'Gentleman\'s Nod',

    'gentlemans face care club': 'Gentlemans Face Care Club',

    'godrej': 'Godrej',

    'golden beards': 'Golden Beards',

    'goldex': 'Goldex',

    '(?:the|)\\s*good\\s*fella' + _apostrophe + 's' + _apostrophe + '\\s*(?:smile|)': 'The Goodfellas\' Smile',

    'gr?oomin?g dep[at]\\S*': 'Grooming Department',

    'Gryphon\'s Groomatorium': 'Gryphon\'s Groomatorium',

    'haslinger': 'Haslinger',

    'hecho sma': 'Hecho SMA',

    '@henrietvictoria': 'Henri et Victoria',
    'henri et victoria': 'Henri et Victoria',

    'heritage hill(?: shave' + _opt_company + '|)': 'Heritage Hill Shave Company',

    'high desert soap' + _opt_company: 'High Desert Soap Co.',

    'highland springs? soap' + _opt_company + _any_and + '(?:australian private|ap) reserve': 'Highland Springs Soap Company',
    'highland springs? soap' + _opt_company + _any_and + 'stone *field shav(?:ing|e)' + _opt_company + '(?:ltd\\.|)': 'Highland Springs Soap Company',
    '@highlandspringssoap': 'Highland Springs Soap Company',
    'high?land springs? soap' + _opt_company: 'Highland Springs Soap Company',
    'highland springs?': 'Highland Springs Soap Company',

    '(?:the |)holy black': 'The Holy Black',
    '@theholyblack': 'The Holy Black',

    'mammoth\\s*(?:soaps?|)' + _any_and + 'ap(?:\\s*reserve|r\\b)': 'House of Mammoth',
    'house of mammoth' + _any_and + 'wholly kaw': 'Wholly Kaw',
    '@?mammoth\\s*(?:soaps?|)': 'House of Mammoth',
    'house of mammoth': 'House of Mammoth',

    'hub city soapworks': 'Hub City Soap Company',
    'hub city\\s*(?:soap' + _opt_company + '|)': 'Hub City Soap Company',

    'imperial\\s*(?:barber (?:products|grade products?|)|)': 'Imperial Barber',

    'ing[áa] saboaria artesanal': 'Ingá Saboaria Artesanal',
    'mythos': 'Ingá Saboaria Artesanal',

    'institut karit[ée]': 'Institut Karité',

    'Irisch Moos': 'Irisch Moos',

    'italian barber': 'Italian Barber',

    'j' + _any_and + 'e atkinsons?': 'J & E Atkinsons',

    'los jabones de joserra': 'Los Jabones de Joserra',

    'k shave worx': 'K Shave Worx',

    'kakashi soap': 'Kakashi Soap',

    '(?:karo|kapo|каро)\\b': 'Каро (Karo)',

    'kells?' + _apostrophe + 's original(?: soap|)': 'Kell\'s Original',

    'kepkinh': 'Kepkinh',

    'Kieh?l' + _apostrophe + 's\\b': 'Kiehl\'s',

    'kiss my face': 'Kiss My Face',

    'klar(?: seifen?| soap|\\b)': 'Klar Seifen',

    'knightsbridge': 'Knightsbridge',

    'le labo\\b(?: inc\\.?|)': 'Le Labo Inc.',

    'lakewood soap' + _opt_company: 'Lakewood Soap Company',

    'lather\\s*bro(?:thers|s)\\.?': 'Lather Bros.',

    'lather jack': 'Lather Jack',

    'laugar(?: of sweden|)': 'Laugar of Sweden',

    'like grandpa': 'Like Grandpa',

    'lisa' + _apostrophe + 's natural(?: herbal creations|)': 'Lisa\'s Natural Herbal Creations',

    'lodrino': 'Lodrino',

    'long rifle(?: +soaps?' + _opt_company + '|)': 'Long Rifle Soap Company',
    
    '(?:the |)(?:los angeles|l *a) shaving(?: soap|)' + _opt_company: 'Los Angeles Shaving Soap Co.',

    'l[øo]thur(?: grooming|)': 'Løthur Grooming',

    'lotus eater': 'Lotus Eater',

    'lucky tiger': 'Lucky Tiger',

    'm' + _any_and + 'e shaving(?: soaps|)': 'M&E Shaving Soaps',

    'macduff' + _apostrophe + 's? soap' + _opt_company: 'MacDuff\'s Soap Company',
    'macduff' + _apostrophe + 's': 'MacDuff\'s Soap Company',

    'maggard razors \\((?:through the fire fine craft|ttffc)\\)': 'Maggard Razors',

    'mama bear(?: +soaps?|)': 'Mama Bear',

    'La Maison du Savon de Marseille': 'La Maison du Savon de Marseille',

    'maol\\s*(?:grooming|)' + _any_and + 'talbot(?: shaving|)': 'Talbot Shaving',
    'maol\\s*(?:grooming|)': 'Maol Grooming',

    'martin de candre': 'Martin de Candre',

    'mastro miche': 'Mastro Miche',

    'matti lindholm(?: shaving(?: supplies|)|)': 'Matti Lindholm Shaving Supplies',

    'mei(?:ß|ss)ner tremonia': 'Meißner Tremonia',

    '@mickeyleesoapworks': 'Mickey Lee Soapworks',
    'micke?y lee\\b(?: soap\w+|)': 'Mickey Lee Soapworks',

    'midnight' + _any_and + 'two': 'Midnight & Two',

    'mike' + _apostrophe + 's naturu?al(?: soaps?|)': 'Mike\'s Natural Soaps',

    'mi[rt]chel+' + _apostrophe + 's\\s*(?:wool fat|)': 'Mitchell\'s Wool Fat',

    'mondial(?: 1908|)': 'Mondial 1908',

    'moon soaps?': 'Moon Soaps',

    'mount royal(?: soap' + _opt_company + '|)': 'Mount Royal Soap Co.',

    'mur(?:ph|hp)y' + _any_and + 'daughters?': 'Murphy & Daughters',

    'mur(?:ph|hp)y' + _any_and + 'mcn(?:ei|ea)l': 'Murphy and McNeil',

    'Myrsol': 'Myrsol',

    'mystic water\\s*(?:soaps?|)': 'Mystic Water Soap',

    'n[eu]+trogena': 'Neutrogena',

    'nivea(?: men|)': 'Nivea',
    'nueva men': 'Nivea',

    'imaginary authors' + _any_and + '(?:noble otter|no\\b)': 'Noble Otter',
    'imaginary authors': 'Noble Otter',
    'nob(?:le|el) otter' + _any_and + '(?:australian private|ap)\\s*r(?:eserve|\\b)': 'Noble Otter',
    '@?noble_otter': 'Noble Otter',
    'nob(?:le|el) otter': 'Noble Otter',
    'apr' + _any_and + 'no': 'Noble Otter',
    'no' + _any_and + 'apr': 'Noble Otter',

    'nordic shaving' + _opt_company: 'Nordic Shaving Company',

    'o melhor': 'O Melhor',

    'oaken\\b(?: lab|)': 'Oaken Lab',

    'oatcake(?: shaving|)(?: soaps?|)': 'Oatcake Soaps',

    'obsessive soap(?:s|\\s+perfect\w+|)': 'Obsessive Soap Perfectionist',
    'osp(?:\\s*soaps?|\\b)': 'Obsessive Soap Perfectionist',

    'l' + _apostrophe + 'occitane': 'l\'Occitane',

    'officina artigiana': 'Officina Artigiana',

    'officina di (?:santa maria|s\\.?m\\.?) novella': 'Officina di Santa Maria Novella',
    'santa maria novella': 'Officina di Santa Maria Novella',

    'ogal+al+a(?: *bay *rum| *bay|)': 'Ogallala Bay Rum',

    'vintage shulton old spice': 'Old Spice',
    'old spice': 'Old Spice',

    'olive blossom': 'Olive Blossom',

    '1000' + _any_and + '1 seife': '1000&1 Seife',

    'opus ruri': 'Opus Ruri',

    '(?:bloc *|)osma': 'Osma',

    'p\\.?160': 'P.160',

    'palmolive': 'Palmolive',

    'pacific shav(?:ing|e)' + _opt_company: 'Pacific Shaving Co.',

    'panee\\b(?: soaps|)': 'Panee Soaps',

    '(?:panna\\s*crema|nu[àa]via)': 'PannaCrema',

    'paragon shaving': 'Paragon Shaving',

    'park avenue': 'Park Avenue',

    'passionately natural(?: soap|)' + _opt_company: 'Passionately Natural Soap Co.',

    'patanjali': 'Patanjali',

    'l' + _apostrophe + 'asinerie de la vioune' + _any_and + 'le p[èeé]re lucien': 'Le Père Lucien',
    'l[ea] p[èeé]re luciene?': 'Le Père Lucien',

    'pereiras?\\b(?:shavery|)': 'Pereira Shavery',

    'ph[oe]+nix' + _any_and + 'beau': 'Phoenix and Beau',

    'pink ?woo?lf': 'Pink Woolf',

    'pinnacle grooming': 'Pinnacle Grooming',

    'portus cale': 'Portus Cale',

    'power ?stick': 'Power Stick',

    'pr[éeè] de provence': 'Pré de Provence',

    'pro(?:ro?as+o|saro)': 'Proraso',
    'p(?:ro|or)aso': 'Proraso',

    'prosar': 'Prosar',

    'provence sant[ée]': 'Provence Santé',

    'purely skinful': 'Purely Skinful',

    'queen charlotte soaps': 'Queen Charlotte Soaps',

    'razor emporium': 'Razor Emporium',

    'what the puck\\??!?\\??': 'RazoRock',

    'red house farms?,? *by *u/grindermonk': 'Red House Farm',
    'red house farms? *\\( *\\[u/grindermonk\\]\\([^\\)]+\\)+' + _apostrophe + 's?\\)?': 'Red House Farm',
    'red\\s*house farms?(?: \\( *u?/?grindermonk\\)?' + _apostrophe + 's?\\)|)': 'Red House Farm',
    '(?:u/|)grinder\\s*monk' + _apostrophe + '(?:s |)(?: homemade| red house farms?|)': 'Red House Farm',
    'red farm': 'Red House Farm',

    'reef *point(?: soapworks| soaps?|)': 'Reef Point Soaps',

    'River Valley Trading': 'River Valley Trading',

    '(?:st\\.?|saint) *james(?: of london|)': 'St. James of London',

    'sapone d[ei] paolo': 'Sapone di Paolo',

    'saponificio +bignoli(?: +c\\.? +galliate| +carlo|)': 'Saponificio Bignoli',
    's\\.? *c\\.? *bignoli': 'Saponificio Bignoli',

    'saponificio\\s*va?r[ei]sino': 'Saponificio Varesino',
    'saponifici?o\\s*varen?s[ie]n?i?o': 'Saponificio Varesino',

    '(?:the |)savage homestead': 'The Savage Homestead',

    'la Savon+i[èe]r+e du moulin': 'La Savonnière du Moulin',

    'scentsy(?:cream shave soap|)': 'Scentsy',

    'scheermonnik': 'Scheermonnik',

    'schmiere': 'Schmiere',
    
    'scottish fine soaps': 'Scottish Fine Soaps',

    's[eē]' + _apostrophe + 'b[uŭ]m gold': 'Sē\'bŭm Gold',

    'shannon' + _apostrophe + 's(?: soaps?|)': 'Shannon\'s Soaps',

    's *h *a *v *e.{0,4}d *a *n *d *y': 'SHAVE DANDY',
    '𝕊 ℍ 𝔸 𝕍 𝔼 ⭐ 𝔻 𝔸 ℕ 𝔻 𝕐': 'SHAVE DANDY',

    'shaver heaven': 'Shaver Heaven',

    'Signature Soaps': 'Signature Soaps',

    'siliski\\s*(?:soaps|soapworks|)': 'Siliski Soaps',

    'smg soaps': 'SMG Soaps',

    'soap commander': 'Soap Commander',

    'the soap exchange': 'The Soap Exchange',

    'soap smooth': 'Soap Smooth',

    'soapy bathman': 'Soapy Bathman',

    'some irish guy' + _apostrophe + 's': 'Some Irish Guy\'s',

    'southern witchcrafts' + _any_and + 'ap(?: reserve|r\\b)': 'Southern Witchcrafts',
    'southern witchcrafts' + _any_and + 'australian private reserve': 'Southern Witchcrafts',
    'southern witchcrafts' + _any_and + 'the razor company': 'Southern Witchcrafts',
    'southern(?:er|)\\s*wh?itchc?raf?ts?': 'Southern Witchcrafts',
    'southern\\s*witchworks?': 'Southern Witchcrafts',

    'spartium (?:natural |)cosmetics': 'Spartium Natural Cosmetics',

    'seat?forth!?': 'Spearhead Shaving Company',
    'spearhead\\s*(?:(?:shaving|soap)' + _opt_company + '|)': 'Spearhead Shaving Company',

    'sp[ei]{2}c?k': 'Speick',

    'stone cottage(?: soapworks|soaps?|)': 'Stone Cottage Soapworks',

    'chatillon lux' + _any_and + 'story\\s*book soap\\s*works': 'Storybook Soapworks',
    'story\\s*book soap\\s*works' + _any_and + 'australian private reserve': 'Storybook Soapworks',
    'story\\s*book soap\\s*works' + _any_and + '(?:ap reserve|apr\\b)': 'Storybook Soapworks',
    'story\\s*book soap\\s*works': 'Storybook Soapworks',
    'story\\s*book(?: soaps?|)': 'Storybook Soapworks',

    'strike gold(?: shaving| shave|)': 'Strike Gold Shave',

    'strop shoppe': 'Strop Shoppe',

    'stubble buster': 'Stubble Buster',

    'stubble trubble': 'Stubble Trubble',

    'stuga\\b': 'Stuga',

    'suavecito': 'Suavecito',

    'chatillon lux' + _any_and + '(?:the|) *sudsy soap[ae]ry?': 'The Sudsy Soapery',
    '(?:the|)\\s*sudsy soap[ae]ry?' + _any_and + '(?:chatillon lux|cl)': 'The Sudsy Soapery',
    '(?:the|)\\s*sudsy soap[ae]ry?': 'The Sudsy Soapery',
    'soapy sudsery': 'The Sudsy Soapery',
    'sudsy' + _apostrophe + 's soapery': 'The Sudsy Soapery',

    'london razors' + _any_and + '(?:summer break(?: soaps?|)|sbs)' : 'Summer Break Soaps',
    'london razors' : 'Summer Break Soaps',
    'summer break(?: soaps?|)' + _any_and + 'london razors' : 'Summer Break Soaps',

    'svoboda': 'Svoboda',
    'свобода': 'Svoboda',

    '(?:the |)swedish witch': 'The Swedish Witch',

    'talbot(?: shaving|)' + _any_and + 'catie' + _apostrophe + 's bubbles': 'Talbot Shaving',
    'talbot\\s*(?:shaving|)' + _any_and + 'CB': 'Talbot Shaving',
    '@talbotshaving @maolgrooming': 'Talbot Shaving',
    'talbot\\s*(?:shaving|)' + _any_and + 'maol(?: grooming|)': 'Talbot Shaving',
    '@talbotshaving': 'Talbot Shaving',
    'talbot\\s*(?:shaving|)': 'Talbot Shaving',

    'tabac\\b': 'Tabac',

    'taconic\\b(?: shave|)': 'Taconic Shave',

    'tallow' + _any_and + 'steel': 'Tallow + Steel',

    'taylor' + _apostrophe + 's? +of +(?:old +|)bond *st(?:reet|\\.|)': 'Taylor of Old Bond Street',
    'taylor' + _apostrophe + 's? +of +(?:old +|)bonds': 'Taylor of Old Bond Street',

    'tcheon? fung sing': 'Tcheon Fung Sing',

    'the club\\b(?:/a&e|)': 'Ariana & Evans',
    'a&e[ /]the club': 'Ariana & Evans',

    '345 soaps?' + _opt_company: '345 Soap Co.',

    'thr?ough the fire fine craft': 'Through the Fire Fine Craft',

    'tiki (?:bar |)soaps?': 'Tiki Bar Soaps',

    'la toj[ao]\\b': 'La Toja',

    'tonka bean shave' + _opt_company: 'Tonka Bean Shave Co.',

    'true?fitt?' + _any_and + 'hill': 'Truefitt & Hill',

    'turtleship(?: shave' + _opt_company + '|)': 'Turtleship Shave Co.',

    'twa burds(?: soaps?|)': 'Twa Burds Soaps',

    'uncle jon' + _apostrophe + 's(?: soap|)': 'Uncle Jon\'s',

    'uncle mike' + _apostrophe + 's': 'Uncle Mike\'s',

    'urth\\b(?: skin solutions(?: for men)|)': 'Urth Skin Solutions',

    'valobra\\b': 'Valobra',

    'Van Yulay': 'Van Yulay',

    'veleiro': 'Veleiro',

    'vera bradley' + _any_and + '(?:venus|gillette)(?: pure|)': 'Gillette',

    'de ver?gulde? hande?': 'De Vergulde Hand',

    'Via Barberia': 'Via Barberia',

    'Vicco': 'Vicco',

    'viking soap' + _any_and + 'cosmetic': 'Viking Soap & Cosmetic',
    'viking(?: (?:shaving |)soap|)': 'Viking Soap & Cosmetic',

    'vito' + _apostrophe + 's': 'Vitos',

    'west of olympia': 'West of Olympia',

    'wet shav(?:ing|er) delight': 'Wet Shaving Delight', # this one's uncertain

    'whispers from the woods': 'Whispers from the Woods',

    'wild magnolia soaps' + _apostrophe: 'Wild Magnolia Soaps',

    'chatillon lux' + _any_and + 'wholly kaw': 'Wholly Kaw',
    'wholly kaw' + _any_and + 'chatillon lux': 'Wholly Kaw',
    'wholly kaw' + _any_and + '(?:house of |)mammoth(?: soaps|)': 'Wholly Kaw',
    'wholly kaw' + _any_and + 'pasteur' + _apostrophe + 's? pharmacy': 'Wholly Kaw',
    'wholly\\s*[kl]aw': 'Wholly Kaw',

    'wickham(?: (?:soap|shave)' + _opt_company + '|)': 'Wickham Soap Co.',

    'william' + _apostrophe + 's(?: mug soap| shave soap|)': 'Williams Mug Soap',

    'wood\\s*box(?:\\s*soap|)': 'Wood Box Soap',

    'yrfce': 'YRFCE',

    'yardley(?: shaving soap|)': 'Yardley',

    'zingar[io] *(?:man|)' + _any_and + 'barrister' + _any_and + 'mann': 'Zingari Man',
    'zingar[io] *(?:man|)' + _any_and + 'b' + _any_and + 'm': 'Zingari Man',
    'zingari *(?:man|)' + _any_and + 'wcs': 'Zingari Man',
    'zingar[io] *(?:mann?|)': 'Zingari Man',
    'z\\*{4,} *(?:mann?|)': 'Zingari Man',
}

# these also make hardware
_hw_maker_pats = {
    '(?:the |)art of shaving': 'Art of Shaving',
    'bundu-? *beard': 'Bundubeard',
    '@declarationgrooming': 'Declaration Grooming',
    'declaration\\s*(?:grooming?|)': 'Declaration Grooming',
    'dec\\.? grooming': 'Declaration Grooming',
    'edwin jagg[ea]r *(?:shav(?:ing|e) soap|)': 'Edwin Jagger',
    'fendrihan': 'Fendrihan',
    'fine accoutrements': 'Fine Accoutrements',
    'gillette': 'Gillette',
    'harry' + _apostrophe + 's': 'Harry\'s',
    'jack black': 'Jack Black',
    'k shave wor(?:x|ks)': 'K Shave Worx',
    'karve(?: shaving' + _opt_company + '|)': 'Karve Shaving Co.',
    '(?:gb |)kent': 'Kent',
    'maggard' + _apostrophe + 's?\\s*(?:razors?|)': 'Maggard Razors',
    'm[üu]hle': 'Mühle',
    'olivina(?: men|)': 'Olivina Men',
    'oz shaving' + _opt_company: 'Oz Shaving Co.',
    'paladin(?: shaving|)': 'Paladin Shaving',
    'paragon(?: shaving|)': 'Paragon Shaving',
    'crown king': 'Phoenix Artisan Accoutrements',
    'phoenix artisan accout(?:re|er)ments': 'Phoenix Artisan Accoutrements',
    'phoenix shaving': 'Phoenix Artisan Accoutrements',
    'razor?rock': 'RazoRock',
    'raz[\\*★]?war': 'Raz*War',
    'rockwell\\b(?: razors|)': 'Rockwell Razors',
    'rocky mountain barber' + _opt_company: 'Rocky Mountain Barber Company',
    'alexander simpson': 'Simpsons',
    'simpson' + _apostrophe + 's?(?: luxury shaving cream|)': 'Simpsons',
    '@stirlingsoap': 'Stirling Soap Co.',
    'st[ei]rl[ei]ng\s*(?:soap(?:works|s|)' + _opt_company + '|)': 'Stirling Soap Co.',
    'striling (?:soaps?|)' + _opt_company: 'Stirling Soap Co.',
    'stilring (?:soaps?|)' + _opt_company: 'Stirling Soap Co.',
    'summer? break\\s*(?:soap\\s*works|soaps?|)': 'Summer Break Soaps',
    '(?:the |)traditional shaving' + _opt_company: 'The Traditional Shaving Co.',
    'van der hag[ea]n': 'Van der Hagen',
    '(?:west coast shaving|wcs)' + _any_and + 'chicago groom\w+' + _opt_company + '(?:\((?:form(?:er|al)ly\\s+|)oleo\\b[^)]*\)|)': 'West Coast Shaving',
    '(?:west coast shaving|wcs)' + _any_and + 'oleo\\b\\s*(?:soap\\s*works|soap)': 'West Coast Shaving',
    '(?:west coast shaving|wcs)' + _any_and + 'catie' + _apostrophe + 's bubbles': 'West Coast Shaving',
    'west coast shaving': 'West Coast Shaving',
    'wet shaving products': 'Wet Shaving Products',
    'wild west (?:shaving|shave)' + _opt_company: 'Wild West Shaving Co.',
    'wilkinson sword': 'Wilkinson Sword',
}

_other_pats = {
    '(?:friend' + _apostrophe + 's|) *homemade\\s+[a-z\\s\\(\\)]*?soap\\.?': '(homemade)',
    'mug of many samples': 'Mug of many samples',
    'tester(?: soap|)': 'Tester',
    'test batch': 'Tester',
    'scent tester': 'Tester',

    # things that aren't really "lather," but for some reason got used anyway
    'k[ae]rosene\\.*': 'kerosene',
}

_abbrev_pats = {
    # abbreviations or more common words
    'aylm': 'Abbate y la Mantia',
    'apex': 'Apex Alchemy Soaps',
    'apr' + _any_and + 'no': 'Noble Otter',
    'apr' + _any_and + 'sw': 'Southern Witchcrafts',
    'apr': 'Australian Private Reserve',
    'b\\s*(?:&(?:amp;|)|\\+|a|-|)\\s*m': 'Barrister and Mann',
    'bea': 'BEA', # not an abbreviation, just a very short word
    'cb': 'Catie\'s Bubbles',
    'cbl': 'CBL Soaps',
    'c' + _any_and + 'e': 'Crabtree & Evelyn',
    'cf': 'Chiseled Face',
    'cf' + _any_and + 'zoologist': 'Chiseled Face',
    'crsw': 'Cold River Soap Works',
    'dg' + _any_and + 'cl': 'Declaration Grooming',
    'l' + _any_and + 'l': 'Declaration Grooming',
    'e' + _any_and + 's': 'E&S', # TODO some company in France
    'esc': 'Executive Shaving',
    'fcs': 'First Canadian Shave',
    'fls': 'First Line Shave',
    'gn': 'Gentleman\'s Nod',
    'gfcc': 'Gentlemans Face Care Club',
    'gfs': 'The Goodfellas\' Smile',
    'gd': 'Grooming Department',
    'hssc': 'Highland Springs Soap Company',
    'thb': 'The Holy Black',
    'hom': 'House of Mammoth',
    'lea': 'LEA', # not actually abbreviated, just a very short word
    'lnhc': 'Lisa\'s Natural Herbal Creations',
    'lassco?': 'Los Angeles Shaving Soap Co.',
    'ly[kc]o': 'Lyko', # not actually abbreviated, just a very short word
    'mdc': 'Martin de Candre',
    'mlsw?': 'Mickey Lee Soapworks',
    'mike' + _apostrophe + 's': 'Mike\'s Natural Soaps',
    'mwf': 'Mitchell\'s Wool Fat',
    'm' + _any_and + 'm\\b': 'Murphy and McNeil',
    'no' + _any_and + 'apr?': 'Noble Otter',
    'p' + _any_and + 'b': 'Phoenix and Beau',
    'p' + _any_and + 'p': 'P&P', # TODO who is this?  Makes 'Lope,' in California, no other detail
    'pdp': 'Pré de Provence',
    'pears': 'Pears', # not abbreviated, just too common to be in the normal block
    'sv': 'Saponificio Varesino',
    'a' + _any_and + 'e': 'Ariana & Evans',
    'sjol': 'St. James of London',
    'smg': 'SMG Soaps',
    'sdp': 'Sapone di Paolo',
    'sw' + _any_and + 'apr?': 'Southern Witchcrafts',
    'sw': 'Southern Witchcrafts',
    'ssc': 'Spearhead Shaving Company',
    'sbsw': 'Storybook Soapworks',
    't' + _any_and + 's': 'Tallow + Steel',
    'tfs': 'Tcheon Fung Sing',
    '345': '345 Soap Co.',
    'tse for men': 'The Soap Exchange',
    'ttffc': 'Through the Fire Fine Craft',
    'tobs': 'Taylor of Old Bond Street',
    'taylor' + _apostrophe + 's': 'Taylor of Old Bond Street',
    'wk': 'Wholly Kaw',
    'wms': 'William\'s Mug Soap',
    'z *man': 'Zingari Man',
    'zm': 'Zingari Man',
    # hardware vendors
    'aos': 'Art of Shaving',
    'd&?g': 'Declaration Grooming',
    'ej': 'Edwin Jagger',
    'fine': 'Fine Accoutrements',
    'n\\.?\\s*o\\.?': 'Noble Otter',
    'paa': 'Phoenix Artisan Accoutrements',
    'rr': 'RazoRock',
    'rmbc': 'Rocky Mountain Barber Company',
    'sbs': 'Summer Break Soaps',
    'vdh': 'Van der Hagen',
    'wcs': 'West Coast Shaving',
    'wsp': 'Wet Shaving Products',
    'wwsc': 'Wild West Shaving Co.',
}

# TODO special category for more complicated patterns,
# e.g. 'wms\\s*[_\*]*\\s*$' for Williams (single scent makes misidentification more likely)

_ending = '(?:\\.|' + _apostrophe + '(?<! )s|)\\s*(.*)'
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
            if saved_full_hw and saved_full_hw['match'].start() == result.start():
                continue
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
