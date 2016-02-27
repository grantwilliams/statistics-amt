import os
import sys
import csv
import copy
import locale
from datetime import datetime
from country_dicts import *


def check_other(country):
    if country in south_america:
        return "OTHER SOUTH AMERICA"
    elif country in north_america:
        return "OTHER NORTH AMERICA"
    elif country in middle_america:
        return "MIDDLE AMERICA/CARIBBEAN"
    elif country in other_europe:
        return "OTHER EUROPE"
    elif country in other_africa:
        return "OTHER AFRICA"
    elif country in arab_gulf:
        return "ARAB GULF"
    elif country in china_group:
        return "CHINA/HONG KONG"
    elif country in other_asia:
        return "OTHER ASIA"
    elif country in gb:
        return "GREAT BRITAIN"


#takes ISO country code and returns a country name
def check_code(code):
    if code in ISO3166:
        if ISO3166.get(code) in south_america:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in north_america:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in middle_america:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in china_group:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in other_asia:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in gb:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in other_europe:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in arab_gulf:
            return check_other(ISO3166.get(code))
        elif ISO3166.get(code) in other_africa:
            return check_other(ISO3166.get(code))
        else:
            return ISO3166.get(code)

#  csv column numbers for the different channel managers csv bookings export
channel_managers = {
    "MyAllocator": {
        "arrival date": 6,
        "nights": 8,
        "canceled": 9,
        "nationality": 13,
        "guests": 15,
        "date format": "%Y-%m-%d"
    },
    "Switchboard": {
        "arrival date": 2,
        "nights": 1,
        "canceled": 6,
        "nationality": 13,
        "guests": 9,
        "date format": "%Y-%B"
    }
}


def calculate(month, year, filename, progress_queue, channel):
    statistics = copy.deepcopy(statistics_results)
    csv_column = copy.deepcopy(channel_managers[channel])
    print(csv_column)

    if sys.platform == "win32":
        locale.setlocale(locale.LC_TIME, "deu_deu")
    else:
        locale.setlocale(locale.LC_TIME, "de_DE")
    month_to_calculate = datetime.strptime("{}-{}".format(month, year), "%B-%Y")
    progress_queue.put(10)
    with open(filename, encoding='utf-8') as file_read:
        bookings_csv_read = csv.reader(file_read)
        next(bookings_csv_read)
        progress_queue.put(10)
        queue_next = 20
        errors = [0, 0]  # index 0 date errors, index 1 int value errors
        for row in bookings_csv_read:
            if errors[0] <= 20 and errors[1] <= 20:
                print(errors)
                try:
                    row_date = datetime.strptime(row[csv_column["arrival date"]], csv_column["date format"])
                    if row_date.month == month_to_calculate.month and row_date.year == month_to_calculate.year:
                        if queue_next < 55:
                            progress_queue.put(1)
                            queue_next += 1
                        if row[csv_column["canceled"]] == "No":
                            try:
                                if row[csv_column["nationality"]].upper() in statistics:
                                    statistics[row[csv_column["nationality"]].upper()][0] += int(row[csv_column["guests"]])
                                    statistics[row[csv_column["nationality"]].upper()][1] += int(row[csv_column["nights"]])*int(row[csv_column["guests"]])
                                elif row[csv_column["nationality"]] == "":
                                    statistics["INFO NOT GIVEN"][0] += int(row[csv_column["guests"]])
                                    statistics["INFO NOT GIVEN"][1] += int(row[csv_column["nights"]])*int(row[csv_column["guests"]])
                                elif check_other(row[csv_column["nationality"]].upper()) in statistics:
                                    statistics[check_other(row[csv_column["nationality"]].upper())][0] += int(row[csv_column["guests"]])
                                    statistics[check_other(row[csv_column["nationality"]].upper())][1] += int(row[csv_column["nights"]])*int(row[csv_column["guests"]])
                                elif check_code(row[csv_column["nationality"]].upper()) in statistics:
                                    statistics[check_code(row[csv_column["nationality"]].upper())][0] += int(row[csv_column["guests"]])
                                    statistics[check_code(row[csv_column["nationality"]].upper())][1] += int(row[csv_column["nights"]])*int(row[csv_column["guests"]])
                                elif row[csv_column["nationality"]] not in statistics:
                                    statistics["INFO NOT GIVEN"][0] += int(row[csv_column["guests"]])
                                    statistics["INFO NOT GIVEN"][1] += int(row[csv_column["nights"]])*int(row[csv_column["guests"]])
                            except ValueError:
                                pass#next(bookings_csv_read)  # skip if can't convert to int
                                errors[1] += 1
                except ValueError:
                    pass#next(bookings_csv_read)  # skip if date doesn't match
                    errors[0] += 1
            else:
                progress_queue.put("wrong channel")
                return
        if queue_next != 55:
            progress_queue.put(55-queue_next)
        progress_queue.put(10)
        if not os.path.isdir("Statistics_Saved_Files"):
            os.makedirs("Statistics_Saved_Files")
        with open("Statistics_Saved_Files/Statistics-{}-{}.csv".format(month, year), 'w',
                  encoding='utf-8') as write_file:
            statistics_csv_write = csv.writer(write_file)

            statistics_csv_write.writerow(['Country', 'Guests', 'Nights'])
            total_guests = 0
            total_overnights = 0
            queue_next = 65
            for key, value in statistics.items():
                if queue_next < 95:
                    progress_queue.put(1)
                    queue_next += 1
                if key == "USA":
                    statistics_csv_write.writerow([key] + [str(value[0])] + [str(value[1])])
                else:
                    statistics_csv_write.writerow([key.title()] + [str(value[0])] + [str(value[1])])
                try:
                    total_guests += int(value[0])
                except ValueError:
                    pass  # Empty dictionary entry for separator between country groups
                try:
                    total_overnights += int(value[1])
                except ValueError:
                    pass  # Empty dictionary entry for separator between country groups
            progress_queue.put(4)
            statistics_csv_write.writerow(['Total', total_guests, total_overnights])
            progress_queue.put("Finished!")
            progress_queue.put(statistics)
            return
