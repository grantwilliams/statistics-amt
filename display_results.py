import os
import sys
import tkinter as tk
from tkinter import ttk
from collections import OrderedDict
import tkinter.messagebox
import pyscreenshot


results = OrderedDict([('GERMANY', [4, 10]), ('BELGIUM', [5, 17]), ('BULGARIA', [0, 0]), ('DENMARK', [2, 4]), ('ESTONIA', [0, 0]), ('FINLAND', [0, 0]), ('FRANCE', [4, 17]), ('GREECE', [0, 0]), ('GREAT BRITAIN', [8, 23]), ('IRELAND', [2, 6]), ('ICELAND', [0, 0]), ('ITALY', [3, 9]), ('CROATIA', [0, 0]), ('LATVIA', [0, 0]), ('LITHUANIA', [0, 0]), ('LUXEMBOURG', [0, 0]), ('MALTA', [0, 0]), ('NETHERLANDS', [6, 12]), ('NORWAY', [0, 0]), ('AUSTRIA', [0, 0]), ('POLAND', [0, 0]), ('PORTUGAL', [0, 0]), ('ROMANIA', [0, 0]), ('RUSSIA', [0, 0]), ('SWEDEN', [3, 6]), ('SWITZERLAND', [4, 18]), ('SLOVAKIA', [0, 0]), ('SLOVENIA', [1, 4]), ('SPAIN', [0, 0]), ('CZECH REPUBLIC', [0, 0]), ('TURKEY', [0, 0]), ('UKRAINE', [0, 0]), ('HUNGARY', [0, 0]), ('CYPRUS', [0, 0]), ('OTHER EUROPE', [0, 0]), ('SOUTH AFRICA', [0, 0]), ('OTHER AFRICA', [0, 0]), ('CANADA', [5, 17]), ('USA', [16, 54]), ('MIDDLE AMERICA/CARIBBEAN', [0, 0]), ('BRAZIL', [0, 0]), ('OTHER SOUTH AMERICA', [4, 13]), ('OTHER NORTH AMERICA', [1, 2]), ('ARAB GULF', [0, 0]), ('CHINA/HONG KONG', [3, 6]), ('INDIA', [1, 2]), ('ISRAEL', [1, 3]), ('JAPAN', [0, 0]), ('SOUTH KOREA', [1, 3]), ('TAIWAN', [0, 0]), ('OTHER ASIA', [0, 0]), ('AUSTRALIA', [9, 33]), ('NEW ZEALAND', [1, 2]), ('INFO NOT GIVEN', [11, 32]), ('TOTAL', [95, 293])])


class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, statistics_results, month):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.sent_confirm_frame = None
        self.statistics_results = statistics_results
        self.month = month
        self.display_results(self.statistics_results, self.month)

    def save_image(self, month):
        self.sent_confirm_frame.grid_forget()
        self.update()
        x_plot = self.winfo_rootx()
        y_plot = self.winfo_rooty()
        width = self.winfo_width()
        height = self.winfo_height()

        image_name = "{}/Statistics {}.png".format(self.file_location, month)
        image = pyscreenshot.grab(bbox=(x_plot, y_plot, (x_plot+width), (y_plot+height)))
        image.save(fp=image_name)

        if os.path.isfile(image_name):
            tk.messagebox.showinfo("Saved file", "Saved!\n{}".format(os.path.abspath(image_name)))

    def display_results(self, statistics_results, month):
        self.title("Statistics Results")
        title_style = ttk.Style()
        title_style.configure("Title.TLabel", font="-size 16 -weight bold", background="#98FB98")
        frame_style = ttk.Style()
        frame_style.configure("Sent.TFrame", background="#98FB98")

        def stats_generator():
            for item in statistics_results.keys():
                if item == "USA":
                    yield [item, statistics_results[item][0], statistics_results[item][1]]
                else:
                    yield [item.title(), statistics_results[item][0], statistics_results[item][1]]
        statistics_generator = stats_generator()

        results_frame = ttk.Frame(self)
        country_header_one = ttk.Label(results_frame, style="Title.TLabel", text=" Country ", anchor=tk.CENTER)
        guests_header_one = ttk.Label(results_frame, style="Title.TLabel", text=" Guests ", anchor=tk.CENTER)
        nights_header_one = ttk.Label(results_frame, style="Title.TLabel", text=" Overnights ", anchor=tk.CENTER)
        europe_header_one = ttk.Label(results_frame, text=" Europe", font="-weight bold", background="#E9967A")
        title_separator = ttk.Separator(results_frame, orient=tk.HORIZONTAL)
        results_frame.grid(row=0, column=0)
        country_header_one.grid(row=0, column=0, sticky=tk.W+tk.E)
        guests_header_one.grid(row=0, column=1, sticky=tk.W+tk.E)
        nights_header_one.grid(row=0, column=2, sticky=tk.W+tk.E)
        title_separator.grid(row=1, column=0, columnspan=11, sticky=tk.W+tk.E)
        europe_header_one.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E)

        for i in range(3, 23):
            current_stats = next(statistics_generator)
            lbl = ttk.Label(results_frame, text="{}: ".format(current_stats[0]), anchor=tk.CENTER)
            lbl.grid(row=i, column=0, sticky=tk.W+tk.E)
            if i % 2 == 0:
                lbl.configure(background="#ADD8E6")
            else:
                lbl.configure(background="#FFFACD")

            guests_entry = ttk.Label(results_frame, text="{}".format(current_stats[1]), anchor=tk.CENTER)
            guests_entry.grid(row=i, column=1, sticky=tk.W+tk.E)
            if i % 2 == 0:
                guests_entry.configure(background="#ADD8E6")
            else:
                guests_entry.configure(background="#FFFACD")

            nights_entry = ttk.Label(results_frame, text="{}".format(current_stats[2]), anchor=tk.CENTER)
            nights_entry.grid(row=i, column=2, sticky=tk.W+tk.E)
            if i % 2 == 0:
                nights_entry.configure(background="#ADD8E6")
            else:
                nights_entry.configure(background="#FFFACD")

        section_one_separator = ttk.Separator(results_frame, orient=tk.VERTICAL)
        section_one_separator.grid(row=0, column=3, rowspan=23, sticky=tk.N+tk.S)
        country_header_two = ttk.Label(results_frame, style="Title.TLabel", text=" Country ", anchor=tk.CENTER)
        guests_header_two = ttk.Label(results_frame, style="Title.TLabel", text=" Guests ", anchor=tk.CENTER)
        nights_header_two = ttk.Label(results_frame, style="Title.TLabel", text=" Overnights ", anchor=tk.CENTER)
        europe_header_two = ttk.Label(results_frame, text=" Europe", font="-weight bold", background="#E9967A")
        country_header_two.grid(row=0, column=4, sticky=tk.W+tk.E)
        guests_header_two.grid(row=0, column=5, sticky=tk.W+tk.E)
        nights_header_two.grid(row=0, column=6, sticky=tk.W+tk.E)
        europe_header_two.grid(row=2, column=4, columnspan=3, sticky=tk.W+tk.E)

        for i in range(3, 18):
            current_stats = next(statistics_generator)
            lbl = ttk.Label(results_frame, text="{}: ".format(current_stats[0]), anchor=tk.CENTER)
            lbl.grid(row=i, column=4, sticky=tk.W+tk.E)
            if i % 2 == 0:
                lbl.configure(background="#ADD8E6")
            else:
                lbl.configure(background="#FFFACD")

            guests_entry = ttk.Label(results_frame, text="{}".format(current_stats[1]), anchor=tk.CENTER)
            guests_entry.grid(row=i, column=5, sticky=tk.W+tk.E)
            if i % 2 == 0:
                guests_entry.configure(background="#ADD8E6")
            else:
                guests_entry.configure(background="#FFFACD")

            nights_entry = ttk.Label(results_frame, text="{}".format(current_stats[2]), anchor=tk.CENTER)
            nights_entry.grid(row=i, column=6, sticky=tk.W+tk.E)
            if i % 2 == 0:
                nights_entry.configure(background="#ADD8E6")
            else:
                nights_entry.configure(background="#FFFACD")

        africa_header = ttk.Label(results_frame, text=" Africa", font="-weight bold", background="#E9967A")
        africa_header.grid(row=18, column=4, columnspan=3, sticky=tk.W+tk.E)

        for i in range(19, 21):
            current_stats = next(statistics_generator)
            lbl = ttk.Label(results_frame, text="{}: ".format(current_stats[0]), anchor=tk.CENTER)
            lbl.grid(row=i, column=4, sticky=tk.W+tk.E)
            if i % 2 == 0:
                lbl.configure(background="#ADD8E6")
            else:
                lbl.configure(background="#FFFACD")

            guests_entry = ttk.Label(results_frame, text="{}".format(current_stats[1]), anchor=tk.CENTER)
            guests_entry.grid(row=i, column=5, sticky=tk.W+tk.E)
            if i % 2 == 0:
                guests_entry.configure(background="#ADD8E6")
            else:
                guests_entry.configure(background="#FFFACD")

            nights_entry = ttk.Label(results_frame, text="{}".format(current_stats[2]), anchor=tk.CENTER)
            nights_entry.grid(row=i, column=6, sticky=tk.W+tk.E)
            if i % 2 == 0:
                nights_entry.configure(background="#ADD8E6")
            else:
                nights_entry.configure(background="#FFFACD")

        section_two_separator = ttk.Separator(results_frame, orient=tk.VERTICAL)
        section_two_separator.grid(row=0, column=7, rowspan=23, sticky=tk.N+tk.S)
        country_header_three = ttk.Label(results_frame, style="Title.TLabel", text=" Country ", anchor=tk.CENTER)
        guests_header_three = ttk.Label(results_frame, style="Title.TLabel", text=" Guests ", anchor=tk.CENTER)
        nights_header_three = ttk.Label(results_frame, style="Title.TLabel", text=" Overnights ", anchor=tk.CENTER)
        america_header = ttk.Label(results_frame, text=" America", font="-weight bold", background="#E9967A")
        asia_header = ttk.Label(results_frame, text=" Asia", font="-weight bold", background="#E9967A")
        australia_header = ttk.Label(results_frame, text=" Australia, Oceania", font="-weight bold",
                                     background="#E9967A")
        country_header_three.grid(row=0, column=8, sticky=tk.W+tk.E)
        guests_header_three.grid(row=0, column=9, sticky=tk.W+tk.E)
        nights_header_three.grid(row=0, column=10, sticky=tk.W+tk.E)
        america_header.grid(row=2, column=8, columnspan=3, sticky=tk.W+tk.E)

        for i in range(3, 22):
            if i == 9:
                asia_header.grid(row=i, column=8, columnspan=3, sticky=tk.W+tk.E)
            elif i == 18:
                australia_header.grid(row=i, column=8, columnspan=3, sticky=tk.W+tk.E)
            else:
                current_stats = next(statistics_generator)
                lbl = ttk.Label(results_frame, text="{}: ".format(current_stats[0]), anchor=tk.CENTER)
                lbl.grid(row=i, column=8, sticky=tk.W+tk.E)
                if i % 2 == 0:
                    lbl.configure(background="#ADD8E6")
                else:
                    lbl.configure(background="#FFFACD")

                guests_entry = ttk.Label(results_frame, text="{}".format(current_stats[1]), anchor=tk.CENTER)
                guests_entry.grid(row=i, column=9, sticky=tk.W+tk.E)
                if i % 2 == 0:
                    guests_entry.configure(background="#ADD8E6")
                else:
                    guests_entry.configure(background="#FFFACD")

                nights_entry = ttk.Label(results_frame, text="{}".format(current_stats[2]), anchor=tk.CENTER)
                nights_entry.grid(row=i, column=10, sticky=tk.W+tk.E)
                if i % 2 == 0:
                    nights_entry.configure(background="#ADD8E6")
                else:
                    nights_entry.configure(background="#FFFACD")

        total_header = ttk.Label(results_frame, text=" Total", font="-weight bold", background="#E9967A")
        total_guests = ttk.Label(results_frame, text=statistics_results["TOTAL"][0], font="-weight bold",
                                 background="#E9967A", anchor=tk.CENTER)
        total_nights = ttk.Label(results_frame, text=statistics_results["TOTAL"][1], font="-weight bold",
                                 background="#E9967A", anchor=tk.CENTER)
        month_lbl = ttk.Label(results_frame, style="Title.TLabel", text="Month: {}".format(month))
        results_separator = ttk.Separator(results_frame, orient=tk.HORIZONTAL)

        total_header.grid(row=22, column=8, sticky=tk.W+tk.E)
        total_guests.grid(row=22, column=9, sticky=tk.W+tk.E)
        total_nights.grid(row=22, column=10, sticky=tk.W+tk.E)
        month_lbl.grid(row=23, column=0, columnspan=11, sticky=tk.W+tk.E)
        results_separator.grid(row=24, column=0, columnspan=11, sticky=tk.W+tk.E)

        if sys.platform == 'win32':
            self.file_location = "Statistics Saved Files"
        else:
            self.file_location = "~/Statistik-Amt/Statistics Saved Files"

        sent_text = "These results have already been sent to the Statistik Amt, you do not need to do anything " \
                    "further, a copy of the results have been saved as a 'csv' file at '{}', which you can open in " \
                    "Excel, Open Office etc.  Alternatively, you can save this image with the button below, which " \
                    "will save the image to the same folder.".format(os.path.abspath(self.file_location))

        self.parent.update()
        window_width = self.winfo_width()
        print(window_width)
        wrap_length = window_width * 0.5
        self.sent_confirm_frame = ttk.Frame(self, style="Sent.TFrame")
        self.sent_confirm_frame.columnconfigure(0, weight=1)

        sent_confirm_lbl = ttk.Label(self.sent_confirm_frame, wraplength=wrap_length, text=sent_text,
                                     background="#98FB98")
        save_image_btn = ttk.Button(self.sent_confirm_frame, text="Save image to file",
                                    command=lambda: self.save_image(month))
        self.sent_confirm_frame.grid(row=1, column=0, sticky=tk.W+tk.E)
        sent_confirm_lbl.grid(row=1, column=0, sticky=tk.W+tk.E)
        save_image_btn.grid(row=2, column=0, columnspan=11, pady=5, sticky=tk.W)

if __name__ == "__main__":
    boot = tk.Tk()
    app = ResultsWindow(boot, results, "Februar 2016")
    boot.mainloop()
