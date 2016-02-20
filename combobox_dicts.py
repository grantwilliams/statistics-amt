from datetime import datetime
from collections import OrderedDict


bundeslaende = (
    ("--Select Bundesland--", ["", 0]),
    ("Schleswig-Holstein", ["Schleswig-Holstein", 1]),
    ("Hamburg", ["Hamburg", 2]),
    ("Niedersachsen", ["Niedersachsen", 3]),
    ("Bremen", ["Bremen", 4]),
    ("Nordrhein-Westfalen", ["Nordrhein-Westfalen", 5]),
    ("Hessen", ["Hessen", 6]),
    ("Rheinland-Pfalz", ["Rheinland-Pfalz", 7]),
    ("Baden-Württemberg", ["Baden-Württemberg", 8]),
    ("Bayern", ["Bayern", 9]),
    ("Saarland", ["Saarland", 10]),
    ("Berlin", ["Berlin", 11]),
    ("Brandenburg", ["Brandenburg", 12]),
    ("Mecklenburg-Vorpommern", ["Mecklenburg-Vorpommern", 13]),
    ("Sachsen", ["Sachsen", 14]),
    ("Sachsen-Anhalt", ["Sachsen-Anhalt", 15]),
    ("Thüringen", ["Thüringen", 16])
)
bundeslaende = OrderedDict(bundeslaende)

months = (
    ("--Month--", ""),
    ("Januar", "Januar"),
    ("Februar", "Februar"),
    ("März", "März"),
    ("April", "April"),
    ("Mai", "Mai"),
    ("Juni", "Juni"),
    ("Juli", "Juli"),
    ("August", "August"),
    ("September", "September"),
    ("Oktober", "Oktober"),
    ("November", "November"),
    ("Dezember", "Dezember")
)
months = OrderedDict(months)

years = {"--Year--": ""}
this_year = datetime.now().year
for year in range(2014, this_year+1):
    years[str(year)] = str(year)



