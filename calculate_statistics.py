import os
import sys
import csv
import calendar
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


def calculate(month, year, filename, progress_queue):
    locale.setlocale(locale.LC_TIME, "de_DE")
    month_to_calculate = datetime.strptime("{}-{}".format(month, year), "%B-%Y")
    progress_queue.put(10)
    with open(filename, encoding='utf-8') as file_read:
        bookings_csv_read = csv.reader(file_read)
        next(bookings_csv_read)
        progress_queue.put(10)
        queue_next = 20
        for row in bookings_csv_read:
            row_date = datetime.strptime(row[6], "%Y-%m-%d")
            if row_date.month == month_to_calculate.month and row_date.year == month_to_calculate.year:
                if queue_next < 55:
                    progress_queue.put(1)
                    queue_next += 1
                if row[9] == "No":
                    if row[13].upper() in statistics:
                        statistics[row[13].upper()][0] += int(row[15])
                        statistics[row[13].upper()][1] += int(row[8])*int(row[15])
                    elif row[13] == "":
                        statistics["INFO NOT GIVEN"][0] += int(row[15])
                        statistics["INFO NOT GIVEN"][1] += int(row[8])*int(row[15])
                    elif check_other(row[13].upper()) in statistics:
                        statistics[check_other(row[13].upper())][0] += int(row[15])
                        statistics[check_other(row[13].upper())][1] += int(row[8])*int(row[15])
                    elif check_code(row[13].upper()) in statistics:
                        statistics[check_code(row[13].upper())][0] += int(row[15])
                        statistics[check_code(row[13].upper())][1] += int(row[8])*int(row[15])
                    elif row[13] not in statistics:
                        statistics["INFO NOT GIVEN"][0] += int(row[15])
                        statistics["INFO NOT GIVEN"][1] += int(row[8])*int(row[15])
        progress_queue.put(10)
        if not os.path.isdir("Statistics_Saved_Files"):
            os.makedirs("Statistics_Saved_Files")
        with open("Statistics_Saved_Files/Statistics {} {}.csv".format(month, year), 'w', encoding='utf-8') as write_file:
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
                except:
                    pass
                try:
                    total_overnights += int(value[1])
                except:
                    pass
            progress_queue.put(4)
            statistics_csv_write.writerow(['Total', total_guests, total_overnights])
            progress_queue.put("Finished!")
