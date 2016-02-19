from datetime import datetime
from collections import OrderedDict


bundeslaende = (
    ("--Select Bundesland--", ""),
    ("Schleswig-Holstein", "Schleswig-Holstein"),
    ("Hamburg", "Hamburg"),
    ("Niedersachsen", "Niedersachsen"),
    ("Bremen", "Bremen"),
    ("Nordrhein-Westfalen", "Nordrhein-Westfalen"),
    ("Hessen", "Hessen"),
    ("Rheinland-Pfalz", "Rheinland-Pfalz"),
    ("Baden-Württemberg", "Baden-Württemberg"),
    ("Bayern", "Bayern"),
    ("Saarland", "Saarland"),
    ("Berlin", "Berlin"),
    ("Brandenburg", "Brandenburg"),
    ("Mecklenburg-Vorpommern", "Mecklenburg-Vorpommern"),
    ("Sachsen", "Sachsen"),
    ("Sachsen-Anhalt", "Sachsen-Anhalt"),
    ("Thüringen", "Thüringen")
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



