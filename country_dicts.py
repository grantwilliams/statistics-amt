# -*- coding: utf-8 -*-
from collections import OrderedDict


ISO3166 = {
    'AF': 'AFGHANISTAN',
    'AX': 'SWEDEN',
    'AL': 'ALBANIA',
    'DZ': 'ALGERIA',
    'AS': 'AMERICAN SAMOA',
    'AD': 'ANDORRA',
    'AO': 'ANGOLA',
    'AI': 'ANGUILLA',
    'AQ': 'ANTARCTICA',
    'AG': 'ANTIGUA AND BARBUDA',
    'AR': 'ARGENTINA',
    'AM': 'ARMENIA',
    'AW': 'ARUBA',
    'AU': 'AUSTRALIA',
    'AT': 'AUSTRIA',
    'AZ': 'AZERBAIJAN',
    'BS': 'BAHAMAS',
    'BH': 'BAHRAIN',
    'BD': 'BANGLADESH',
    'BB': 'BARBADOS',
    'BY': 'BELARUS',
    'BE': 'BELGIUM',
    'BZ': 'BELIZE',
    'BJ': 'BENIN',
    'BM': 'BERMUDA',
    'BT': 'BHUTAN',
    'BO': 'BOLIVIA',
    'BQ': 'BONAIRE, SINT EUSTATIUS AND SABA',
    'BA': 'BOSNIA',
    'BW': 'BOTSWANA',
    'BV': 'BOUVET ISLAND',
    'BR': 'BRAZIL',
    'IO': 'BRITISH INDIAN OCEAN TERRITORY',
    'BN': 'BRUNEI DARUSSALAM',
    'BG': 'BULGARIA',
    'BF': 'BURKINA FASO',
    'BI': 'BURUNDI',
    'KH': 'CAMBODIA',
    'CM': 'CAMEROON',
    'CA': 'CANADA',
    'CV': 'CAPE VERDE',
    'KY': 'CAYMAN ISLANDS',
    'CF': 'CENTRAL AFRICAN REPUBLIC',
    'TD': 'CHAD',
    'CL': 'CHILE',
    'CN': 'CHINA',
    'CX': 'AUSTRALIA',  # CHRISTMAS ISLAND
    'CC': 'COCOS (KEELING) ISLANDS',
    'CO': 'COLOMBIA',
    'KM': 'COMOROS',
    'CG': 'CONGO',
    'CD': 'CONGO, THE DEMOCRATIC REPUBLIC OF THE',
    'CK': 'COOK ISLANDS',
    'CR': 'COSTA RICA',
    'CI': 'CÔTE D\'IVOIRE',
    'HR': 'CROATIA',
    'CU': 'CUBA',
    'CW': 'CURAÇAO',
    'CY': 'CYPRUS',
    'CZ': 'CZECH REPUBLIC',
    'DK': 'DENMARK',
    'DJ': 'DJIBOUTI',
    'DM': 'DOMINICA',
    'DO': 'DOMINICAN REPUBLIC',
    'EC': 'ECUADOR',
    'EG': 'EGYPT',
    'SV': 'EL SALVADOR',
    'GQ': 'EQUATORIAL GUINEA',
    'ER': 'ERITREA',
    'EE': 'ESTONIA',
    'ET': 'ETHIOPIA',
    'FK': 'FALKLAND ISLANDS',
    'FO': 'DENMARK',  # FAROE ISLANDS
    'FJ': 'FIJI',
    'FI': 'FINLAND',
    'FR': 'FRANCE',
    'GF': 'FRENCH GUIANA',
    'PF': 'FRENCH POLYNESIA',
    'TF': 'FRENCH SOUTHERN TERRITORIES',
    'GA': 'GABON',
    'GM': 'GAMBIA',
    'GE': 'GEORGIA',
    'DE': 'GERMANY',
    'GB' : 'UNITED KINGDOM',
    'GH': 'GHANA',
    'GI': 'GIBRALTAR',
    'GR': 'GREECE',
    'GL': 'GREENLAND',
    'GD': 'GRENADA',
    'GP': 'GUADELOUPE',
    'GU': 'GUAM',
    'GT': 'GUATEMALA',
    'GG': 'GUERNSEY',
    'GN': 'GUINEA',
    'GW': 'GUINEA-BISSAU',
    'GY': 'GUYANA',
    'HT': 'HAITI',
    'HM': 'HEARD ISLAND AND MCDONALD ISLANDS',
    'VA': 'HOLY SEE (VATICAN CITY STATE)',
    'HN': 'HONDURAS',
    'HK': 'HONG KONG',
    'HU': 'HUNGARY',
    'IS': 'ICELAND',
    'IN': 'INDIA',
    'ID': 'INDONESIA',
    'IR': 'IRAN',
    'IQ': 'IRAQ',
    'IE': 'IRELAND',
    'IM': 'ISLE OF MAN',
    'IL': 'ISRAEL',
    'IT': 'ITALY',
    'JM': 'JAMAICA',
    'JP': 'JAPAN',
    'JE': 'JERSEY',
    'JO': 'JORDAN',
    'KZ': 'KAZAKHSTAN',
    'KE': 'KENYA',
    'KI': 'KIRIBATI',
    'KP': 'KOREA, DEMOCRATIC PEOPLE\'S REPUBLIC OF',
    'KR': 'SOUTH KOREA',
    'KW': 'KUWAIT',
    'KG': 'KYRGYZSTAN',
    'LA': 'LAO PEOPLE\'S DEMOCRATIC REPUBLIC',
    'LV': 'LATVIA',
    'LB': 'LEBANON',
    'LS': 'LESOTHO',
    'LR': 'LIBERIA',
    'LY': 'LIBYAN ARAB JAMAHIRIYA',
    'LI': 'SWITZERLAND',  # LIECHTENSTEIN
    'LT': 'LITHUANIA',
    'LU': 'LUXEMBOURG',
    'MO': 'MACAU',
    'MK': 'MACEDONIA',
    'MG': 'MADAGASCAR',
    'MW': 'MALAWI',
    'MY': 'MALAYSIA',
    'MV': 'MALDIVES',
    'ML': 'MALI',
    'MT': 'MALTA',
    'MH': 'MARSHALL ISLANDS',
    'MQ': 'MARTINIQUE',
    'MR': 'MAURITANIA',
    'MU': 'MAURITIUS',
    'YT': 'MAYOTTE',
    'MX': 'MEXICO',
    'FM': 'MICRONESIA, FEDERATED STATES OF',
    'MD': 'MOLDOVA, REPUBLIC OF',
    'MC': 'MONACO',
    'MN': 'MONGOLIA',
    'ME': 'MONTENEGRO',
    'MS': 'MONTSERRAT',
    'MA': 'MOROCCO',
    'MZ': 'MOZAMBIQUE',
    'MM': 'MYANMAR',
    'NA': 'NAMIBIA',
    'NR': 'NAURU',
    'NP': 'NEPAL',
    'NL': 'NETHERLANDS',
    'NC': 'NEW CALEDONIA',
    'NZ': 'NEW ZEALAND',
    'NI': 'NICARAGUA',
    'NE': 'NIGER',
    'NG': 'NIGERIA',
    'NU': 'NIUE',
    'NF': 'NORFOLK ISLAND',
    'MP': 'NORTHERN MARIANA ISLANDS',
    'NO': 'NORWAY',
    'OM': 'OMAN',
    'PK': 'PAKISTAN',
    'PW': 'PALAU',
    'PS': 'PALESTINIAN TERRITORY, OCCUPIED',
    'PA': 'PANAMA',
    'PG': 'PAPUA NEW GUINEA',
    'PY': 'PARAGUAY',
    'PE': 'PERU',
    'PH': 'PHILIPPINES',
    'PN': 'PITCAIRN',
    'PL': 'POLAND',
    'PT': 'PORTUGAL',
    'PR': 'PUERTO RICO',
    'QA': 'QATAR',
    'RE': 'RÉUNION',
    'RO': 'ROMANIA',
    'RU': 'RUSSIA',
    'RW': 'RWANDA',
    'BL': 'SAINT BARTHÉLEMY',
    'SH': 'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA',
    'KN': 'SAINT KITTS AND NEVIS',
    'LC': 'SAINT LUCIA',
    'MF': 'SAINT MARTIN (FRENCH PART)',
    'PM': 'SAINT PIERRE AND MIQUELON',
    'VC': 'SAINT VINCENT AND THE GRENADINES',
    'WS': 'SAMOA',
    'SM': 'SAN MARINO',
    'ST': 'SAO TOME AND PRINCIPE',
    'SA': 'SAUDI ARABIA',
    'SN': 'SENEGAL',
    'RS': 'SERBIA',
    'SC': 'SEYCHELLES',
    'SL': 'SIERRA LEONE',
    'SG': 'SINGAPORE',
    'SX': 'SINT MAARTEN (DUTCH PART)',
    'SK': 'SLOVAKIA',
    'SI': 'SLOVENIA',
    'SB': 'SOLOMON ISLANDS',
    'SO': 'SOMALIA',
    'ZA': 'SOUTH AFRICA',
    'GS': 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS',
    'SS': 'SOUTH SUDAN',
    'ES': 'SPAIN',
    'LK': 'SRI LANKA',
    'SD': 'SUDAN',
    'SR': 'SURINAME',
    'SJ': 'SVALBARD AND JAN MAYEN',
    'SZ': 'SWAZILAND',
    'SE': 'SWEDEN',
    'CH': 'SWITZERLAND',
    'SY': 'SYRIAN ARAB REPUBLIC',
    'TW': 'TAIWAN',
    'TJ': 'TAJIKISTAN',
    'TZ': 'TANZANIA, UNITED REPUBLIC OF',
    'TH': 'THAILAND',
    'TL': 'TIMOR-LESTE',
    'TG': 'TOGO',
    'TK': 'TOKELAU',
    'TO': 'TONGA',
    'TT': 'TRINIDAD AND TOBAGO',
    'TN': 'TUNISIA',
    'TR': 'TURKEY',
    'TM': 'TURKMENISTAN',
    'TC': 'TURKS AND CAICOS ISLANDS',
    'TV': 'TUVALU',
    'UG': 'UGANDA',
    'UA': 'UKRAINE',
    'AE': 'UNITED ARAB EMIRATES',
    'US': 'USA',
    'UM': 'UNITED STATES MINOR OUTLYING ISLANDS',
    'UY': 'URUGUAY',
    'UZ': 'UZBEKISTAN',
    'VU': 'VANUATU',
    'VE': 'VENEZUELA',
    'VN': 'VIETNAM',
    'VG': 'VIRGIN ISLANDS, BRITISH',
    'VI': 'VIRGIN ISLANDS, U.S.',
    'WF': 'WALLIS AND FUTUNA',
    'EH': 'WESTERN SAHARA',
    'YE': 'YEMEN',
    'ZM': 'ZAMBIA',
    'ZW': 'ZIMBABWE'
    }

statistics_results = (
    ("GERMANY", [0, 0]),
    ("BELGIUM", [0, 0]),
    ("BULGARIA", [0, 0]),
    ("DENMARK", [0, 0]),
    ("ESTONIA", [0, 0]),
    ("FINLAND", [0, 0]),
    ("FRANCE", [0, 0]),
    ("GREECE", [0, 0]),
    ("GREAT BRITAIN", [0, 0]),
    ("IRELAND", [0, 0]),
    ("ICELAND", [0, 0]),
    ("ITALY", [0, 0]),
    ("CROATIA", [0, 0]),
    ("LATVIA", [0, 0]),
    ("LITHUANIA", [0, 0]),
    ("LUXEMBOURG", [0, 0]),
    ("MALTA", [0, 0]),
    ("NETHERLANDS", [0, 0]),
    ("NORWAY", [0, 0]),
    ("AUSTRIA", [0, 0]),
    ("POLAND", [0, 0]),
    ("PORTUGAL", [0, 0]),
    ("ROMANIA", [0, 0]),
    ("RUSSIA", [0, 0]),
    ("SWEDEN", [0, 0]),
    ("SWITZERLAND", [0, 0]),
    ("SLOVAKIA", [0, 0]),
    ("SLOVENIA", [0, 0]),
    ("SPAIN", [0, 0]),
    ("CZECH REPUBLIC", [0, 0]),
    ("TURKEY", [0, 0]),
    ("UKRAINE", [0, 0]),
    ("HUNGARY", [0, 0]),
    ("CYPRUS", [0, 0]),
    ("OTHER EUROPE", [0, 0]),
    ("SOUTH AFRICA", [0, 0]),
    ("OTHER AFRICA", [0, 0]),
    ("CANADA", [0, 0]),
    ("USA", [0, 0]),
    ("MIDDLE AMERICA/CARIBBEAN", [0, 0]),
    ("BRAZIL", [0, 0]),
    ("OTHER SOUTH AMERICA", [0, 0]),
    ("OTHER NORTH AMERICA", [0, 0]),
    ("ARAB GULF", [0, 0]),
    ("CHINA/HONG KONG", [0, 0]),
    ("INDIA", [0, 0]),
    ("ISRAEL", [0, 0]),
    ("JAPAN", [0, 0]),
    ("SOUTH KOREA", [0, 0]),
    ("TAIWAN", [0, 0]),
    ("OTHER ASIA", [0, 0]),
    ("AUSTRALIA", [0, 0]),
    ("NEW ZEALAND", [0, 0]),
    ("INFO NOT GIVEN", [0, 0]),
    ("TOTAL", [0, 0])
)

statistics_results = OrderedDict(statistics_results)

south_america = ['ARGENTINA', 'BOLIVIA', 'CHILE', 'COLUMBIA', 'ECUADOR', 'FALKLAND ISLANDS', 'FRENCH GUIANA', 'GUYANA',
                 'PARAGUAY', 'PERU', 'URUGUAY', 'VENEZUELA']
north_america = ['AMERICA SAMOA', 'ANGUILLA', 'ARUBA', 'CAYMAN ISLANDS', 'COSTA RICA', 'CUBA', 'CURAÇAO', 'DOMINICA',
                 'DOMINICAN REPUBLIC', 'EL SALVADOR', 'GRENADA', 'GUADELOUPE', 'GUATEMALA', 'MEXICO', 'PANAMA',
                 'PUERTO RICO']
middle_america = ['BAHAMAS', 'BARBADOS', 'BELIZE', 'BERMUDA', 'HONDURAS', 'JAMAICA']
china_group = ['CHINA', 'HONG KONG']
other_asia = ['AFGHANISTAN', 'ARMENIA', 'AZERBAIJAN', 'BANGLADESH', 'BHUTAN', 'BRUNEI DARUSSALAM', 'CAMBODIA',
              'COCOS (KEELING) ISLANDS', 'INDONESIA', 'MALAYSIA', 'PAKISTAN', 'PHILIPPINES', 'SINGAPORE', 'SRI LANKA',
              'TAILAND', 'VIETNAM']
gb = ['GREAT BRITAIN', 'WALES', 'SCOTLAND', 'ENGLAND', 'NORTHERN IRELAND', 'UNITED KINGDOM', 'GUERNSEY',
      'BRITISH INDIAN OCEAN TERRITORY', 'ISLE OF MAN']
other_europe = ['ALBANIA', 'ANDORRA', 'BELARUS', 'BOSNIA', 'GEORGIA', 'GIBRALTAR', 'GREENLAND', 'JERSEY', 'MACEDONIA',
                'MALTA', 'MONACO', 'MONTENEGRO', 'SERBIA']
other_africa = ['ALGERIA', 'ANGOLA', 'BENIN', 'BOTSWANA', 'BURKINA FASO', 'BURUNDI', 'CAMEROON', 'CARPE VERDE',
                'CENTRAL AFRICAN REPUBLIC', 'CHAD', 'COMOROS', 'CONGO', 'DJIBOUTI', 'EGYPT', 'EQUATORIAL GUINEA',
                'ERITREA', 'ETHIOPIA', 'GABON', 'GAMBIA', 'GHANA']
arab_gulf = ['BAHRAIN', 'OMAN', 'QATAR', 'IRAN', 'UNITED ARAB EMIRATES']
