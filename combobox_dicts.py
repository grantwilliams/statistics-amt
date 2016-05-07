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
    ("-Month-", ""),
    ("Januar", "01"),
    ("Februar", "02"),
    ("März", "03"),
    ("April", "04"),
    ("Mai", "05"),
    ("Juni", "06"),
    ("Juli", "07"),
    ("August", "08"),
    ("September", "09"),
    ("Oktober", "10"),
    ("November", "11"),
    ("Dezember", "12")
)
months = OrderedDict(months)

days_in_month = (
    ("", ""),
    ("01", "01"),
    ("02", "02"),
    ("03", "03"),
    ("04", "04"),
    ("05", "05"),
    ("06", "06"),
    ("07", "07"),
    ("08", "08"),
    ("09", "09"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
    ("13", "13"),
    ("14", "14"),
    ("15", "15"),
    ("16", "16"),
    ("17", "17"),
    ("18", "18"),
    ("19", "19"),
    ("20", "20"),
    ("21", "21"),
    ("22", "22"),
    ("23", "23"),
    ("24", "24"),
    ("25", "25"),
    ("26", "26"),
    ("27", "27"),
    ("28", "28"),
    ("29", "29"),
    ("30", "30"),
    ("31", "31")
)

days_in_month = OrderedDict(days_in_month)

month_num = (
    ("", ""),
    ("01", "01"),
    ("02", "02"),
    ("03", "03"),
    ("04", "04"),
    ("05", "05"),
    ("06", "06"),
    ("07", "07"),
    ("08", "08"),
    ("09", "09"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12")
)
month_num = OrderedDict(month_num)

channel_managers = {
    "--Select Channel Manager--": "",
    "MyAllocator": "MyAllocator",
}

years = {"-Year-": ""}
this_year = datetime.now().year
for year in range(2014, this_year+1):
    years[str(year)] = str(year)

options_years = {"": ""}
this_year = datetime.now().year
for year in range(2014, this_year+15):
    options_years[str(year)] = str(year)
