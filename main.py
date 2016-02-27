import os
import sys
import threading
import queue
from datetime import datetime
import locale
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog
import idlelib.ToolTip as TT
from collections import OrderedDict
import json
import myallocator
import statistic_amt
import combobox_dicts
import calculate_statistics
from sa_options import *


"""
ma refers to MyAllocator
sa refers to Statistik Amt
"""


class MainWindow(ttk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        if sys.platform == "win32":
            locale.setlocale(locale.LC_TIME, "deu_deu")
            warning_fs = "-size 8"
            self.field_width = 40
        else:
            locale.setlocale(locale.LC_TIME, "de_DE")
            warning_fs = "-size 10"
            self.field_width = 30

        self.myallocator_login = False
        self.bookings_file = ""
        self.channel_manager = "--Select Channel Manager--"

        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)

        self.download_queue = multiprocessing.Queue()
        self.message_queue = multiprocessing.Queue()
        self.ma_cred_queue = queue.Queue()
        self.sa_cred_queue = queue.Queue()
        self.calculate_statistics_queue = queue.Queue()
        self.sa_send_queue = queue.Queue()

        self.ma_login_details = dict()
        if os.path.isfile("data_files/.ma_login.json"):
            with open("data_files/.ma_login.json") as ma_json:
                self.ma_login_details = json.load(ma_json)
        self.sa_login_details = dict()
        if os.path.isfile("data_files/.sa_login.json"):
            with open("data_files/.sa_login.json") as sa_json:
                self.sa_login_details = json.load(sa_json)

        self.theme = ttk.Style()
        self.theme.theme_create("dark_theme", parent="alt", settings={
            "TFrame": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
            "TLabel": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
            "TButton": {"configure": {"background": "#242424", "foreground": "#0FF1F0",
                                      "relief": "raised", "padding": 2
                                      }},
            "TCheckbutton": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
            "TEntry": {"configure": {"background": "#242424", "foreground": "#242424"}},
            "Horizontal.TProgressbar": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}}
        })
        self.theme.theme_use("dark_theme")

        self.label_title = ttk.Style()
        self.label_title.configure("title.TLabel", font="-size 18")
        self.warning_lbl_style = ttk.Style()
        self.warning_lbl_style.configure('Warning.TLabel', font=warning_fs, foreground='red')
        self.options_lbl_style = ttk.Style()
        self.options_lbl_style.configure('Options.TLabel', font="-size 10")

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill=tk.X)
        self.title = ttk.Label(self.title_frame, text="Statistics")
        self.title.pack(side=tk.TOP, pady=10)
        self.setup_ma()

    def setup_ma(self):
        bullet = "\u2022"
        #  MyAllocator login widgets
        self.ma_title_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ma_form_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ma_title_frame = ttk.Frame(self)
        self.ma_title_lbl = ttk.Label(self.ma_title_frame, style="title.TLabel", text="MyAllocator login details")
        self.ma_form_frame = ttk.Frame(self)
        self.ma_username_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Username: ")
        self.ma_username_var = tk.StringVar()
        self.ma_username_entry = ttk.Entry(self.ma_form_frame, width=self.field_width, textvariable=self.ma_username_var,
                                           state=tk.DISABLED)
        self.ma_password_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Password: ")
        self.ma_password_var = tk.StringVar()
        self.ma_password_entry = ttk.Entry(self.ma_form_frame, show=bullet, width=self.field_width, textvariable=self.ma_password_var)
        self.ma_button_frame = ttk.Frame(self)
        self.ma_save_login_btn = ttk.Button(self.ma_button_frame, text="Save login details",
                                            command=self.save_ma_login)
        self.ma_get_properties_btn = ttk.Button(self.ma_button_frame, text="Get Properties",
                                                command=lambda: self.check_ma_credential("get properties"))
        self.ma_change_detials_btn = ttk.Button(self.ma_button_frame, text="Change login details",
                                                command=self.ma_change_details)
        self.upload_bookings_btn = ttk.Button(self.ma_button_frame, text="Upload Bookings", command=self.upload_bookings)
        self.upload_tooltop = TT.ToolTip(self.upload_bookings_btn, "Upload a 'csv' file of all your bookings, if you "
                                                                   "don't have a MyAllocator account.")
        self.ma_warning_var = tk.StringVar()
        self.ma_warning = ttk.Label(self.ma_form_frame, style="Warning.TLabel", textvariable=self.ma_warning_var)

        #  pack MyAllocator widgets
        self.ma_title_frame.pack(fill=tk.X)
        self.ma_title_lbl.pack(side=tk.LEFT, padx=20)
        self.ma_title_separator.pack(fill=tk.X, padx=20, pady=2)
        self.ma_form_frame.pack(fill=tk.X)
        self.ma_username_lbl.grid(row=0, column=0, sticky=tk.E, padx=20, pady=2)
        self.ma_username_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(0, 20), pady=2)
        self.ma_username_var.set(self.ma_login_details["ma_username"])
        self.ma_password_lbl.grid(row=1, column=0, sticky=tk.E, padx=20, pady=2)
        self.ma_password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(0, 20), pady=2)
        self.ma_password_entry.focus()
        self.ma_password_var.set(self.ma_login_details["ma_password"])
        self.ma_button_frame.pack(fill=tk.X)
        self.ma_warning.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.ma_form_separator.pack(fill=tk.X, padx=20, pady=2)
        if self.ma_login_details["ma_password"] != "":
            self.ma_change_detials_btn.pack(side=tk.RIGHT, padx=(5, 20))
            self.ma_get_properties_btn.pack(side=tk.RIGHT, pady=2)
            self.ma_password_entry.configure(state=tk.DISABLED)
        else:
            self.upload_bookings_btn.pack(side=tk.RIGHT, padx=(5, 20), pady=2)
            self.ma_save_login_btn.pack(side=tk.RIGHT, pady=2)

    def ma_change_details(self):
        self.ma_password_entry.configure(state=tk.ACTIVE)
        self.ma_password_var.set("")
        self.ma_password_entry.focus()
        self.ma_change_detials_btn.forget()
        self.ma_get_properties_btn.forget()
        self.ma_save_login_btn.pack(side=tk.RIGHT, padx=20, pady=2)
        self.parent.update()

    def check_ma_credential(self, call_origin):
        self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
        self.ma_warning_var.set("Trying to log into MyAllocator...")
        ma_cred_thread = threading.Thread(
            target=myallocator.check_cred, args=[self.ma_login_details, self.ma_cred_queue, call_origin])
        ma_cred_thread.daemon = True
        ma_cred_thread.start()
        self.parent.after(100, self.check_ma_cred_queue)

    def save_ma_login(self):
        self.ma_username = self.ma_username_entry.get()
        self.ma_password = self.ma_password_entry.get()
        self.upload_bookings_btn.configure(state=tk.DISABLED)

        if self.ma_username != '' and self.ma_password != '':
            self.ma_login_details["ma_username"] = self.ma_username
            self.ma_login_details["ma_password"] = self.ma_password
            with open("data_files/.ma_login.json", "w") as outfile:
                json.dump(self.ma_login_details, indent=4, sort_keys=True, fp=outfile)
                self.check_ma_credential("ma save details")
        elif self.ma_username == '' or self.ma_password == '':
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("One or more fields are empty!")
            self.upload_bookings_btn.configure(state=tk.ACTIVE)

    def ma_credential_ok(self, status):
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Login successful!")
            self.ma_save_login_btn.forget()
            self.upload_bookings_btn.forget()
            self.ma_change_detials_btn.pack(side=tk.RIGHT, padx=(5, 20))
            self.ma_get_properties_btn.pack(side=tk.RIGHT, pady=2)
            self.ma_password_entry.configure(state=tk.DISABLED)
            self.myallocator_login = True
            self.parent.update()
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.upload_bookings_btn.configure(state=tk.ACTIVE)
            self.ma_login_details["ma_password"] = ""
            with open("data_Files/.ma_login.json", 'w', encoding='utf-8') as outfile:
                json.dump(self.ma_login_details, indent=4, sort_keys=True, fp=outfile)

    def get_properties(self, status):
        self.ma_get_properties_btn.configure(state=tk.DISABLED)
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Login successful!")
            self.ma_button_frame.destroy()
            self.ma_password_entry.configure(state=tk.DISABLED)
            property_process = multiprocessing.Process(target=myallocator.get_properties, args=(self.ma_login_details,))
            property_process.daemon = True
            property_process.start()
            property_process.join()
            self.load_properties()
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_password_entry.configure(state=tk.ACTIVE)
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_change_detials_btn.forget()
            self.ma_get_properties_btn.forget()
            self.ma_save_login_btn.pack(side=tk.RIGHT, padx=20, pady=2)

    def load_properties(self):
        self.ma_properties = dict()
        with open("data_files/properties.json") as propfile:
            self.ma_properties = json.load(propfile)

            self.ma_properties_frame = ttk.Frame(self)
            self.ma_properties_lbl = ttk.Label(self.ma_properties_frame, text="Property: ")
            self.ma_properties_combobox = ttk.Combobox(self.ma_properties_frame,
                                                       values=sorted(list(self.ma_properties.keys())))
            self.ma_download_btn = ttk.Button(self.ma_properties_frame, text="Download Bookings",
                                                command=self.download_bookings)
            self.ma_properties_serparator = ttk.Separator(self, orient=tk.HORIZONTAL)
            self.ma_properties_frame.pack(fill=tk.X)
            self.ma_properties_lbl.grid(row=0, column=0, sticky=tk.E, padx=20, pady=2)
            self.ma_properties_combobox.grid(row=0, column=1, sticky=tk.W, pady=2)
            self.ma_download_btn.grid(row=0, column=2, sticky=tk.E, padx=20, pady=2)
            self.ma_properties_combobox.current(0)
            self.ma_properties_serparator.pack(fill=tk.X, padx=20, pady=2)

    def upload_bookings(self):
        self.browse_files_frame = ttk.Frame(self)
        self.browse_files_btn = ttk.Button(self.browse_files_frame, text="Browse...", command=self.browse_csv)
        self.browse_files_var = tk.StringVar()
        self.browse_files_lbl = ttk.Entry(self.browse_files_frame, width=self.field_width+5, textvariable=self.browse_files_var)
        self.channel_lbl = ttk.Label(self.browse_files_frame, text="Channel Manager:")
        self.channel_combobox = ttk.Combobox(self.browse_files_frame, width=26, values=sorted(list(combobox_dicts.channel_managers.keys())))
        self.channel_combobox.bind("<<ComboboxSelected>>", self.channel_selected)
        self.browse_files_separator = ttk.Separator(self, orient="horizontal")

        self.ma_title_frame.forget()
        self.ma_form_frame.forget()
        self.ma_button_frame.forget()
        self.ma_form_separator.forget()
        self.browse_files_frame.pack(fill=tk.X)
        self.browse_files_btn.grid(row=0, column=0, padx=20, pady=2, sticky=tk.E)
        self.browse_files_lbl.grid(row=0, column=1, pady=2, padx=(0, 20), sticky=tk.W+tk.E)
        self.channel_lbl.grid(row=1, column=0, padx=20, pady=2, sticky=tk.E)
        self.channel_combobox.grid(row=1, column=1, pady=2, sticky=tk.W)
        self.channel_combobox.current(0)
        self.browse_files_separator.pack(fill=tk.X, padx=20)
        self.update()

    def browse_csv(self):
        self.bookings_file = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
        self.browse_files_var.set(self.bookings_file)
        #self.setup_sa()

    def channel_selected(self, event):
        try:
            self.sa_title_separator.forget()
            self.sa_title_frame.forget()
            self.sa_form_frame.forget()
            self.calculate_frame.forget()
        except:
            pass
        self.channel_manager = self.channel_combobox.get()
        self.setup_sa()

    def download_bookings(self):
        self.ma_warning_var.set("")
        property = self.ma_properties[self.ma_properties_combobox.get()][0]
        self.ma_properties_warn_var = tk.StringVar()
        if property != "" and self.ma_properties_warn_var.get() in ["", "Finished!"]:
            self.ma_download_btn.configure(state=tk.DISABLED)
            self.ma_properties_combobox.configure(state=tk.DISABLED)
            try:
                self.sa_title_frame.forget()
                self.sa_form_frame.forget()
                self.sa_calculate_separator.forget()
                self.calculate_frame.forget()
            except:
                pass
            download_process = multiprocessing.Process(
                target=myallocator.download_bookings_csv, args=(self.ma_login_details, property, self.download_queue))
            download_process.daemon = True
            download_process.start()
            self.download_bar = ttk.Progressbar(self.ma_properties_frame, orient="horizontal", mode="determinate")
            self.download_bar.grid(row=1, column=1, sticky=tk.W+tk.E)
            self.download_lbl_var = tk.StringVar()
            self.download_lbl = ttk.Label(self.ma_properties_frame, textvariable=self.download_lbl_var)
            self.download_lbl.grid(row=1, column=2, sticky=tk.W, padx=20)
            self.download_lbl_var.set("Downloading...")
            self.parent.after(100, self.load_bar)
            self.setup_sa()
        else:
            self.ma_properties_warn_lbl = ttk.Label(self.ma_properties_frame, style="Warning.TLabel",
                                                    textvariable=self.ma_properties_warn_var)
            self.ma_properties_warn_lbl.grid(row=1, column=1, columnspan=2, sticky=tk.W)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_properties_warn_var.set("Please choose a property first.")

    def setup_sa(self):
        bullet = "\u2022"
        bundeslaende = combobox_dicts.bundeslaende
        try:
            self.sa_property = self.ma_properties_combobox.get()
        except AttributeError:
            self.sa_property = "Upload Bookings"

        #  Statistik Amt login widgets
        self.sa_title_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.sa_form_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.sa_title_frame = ttk.Frame(self)
        self.sa_title_lbl = ttk.Label(self.sa_title_frame, style="title.TLabel", text="Statistik Amt login details")
        self.sa_form_frame = ttk.Frame(self)
        self.sa_user_id_var = tk.StringVar()
        self.sa_user_id_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt ID nr: ")
        self.sa_user_id_entry = ttk.Entry(self.sa_form_frame, width=self.field_width, textvariable=self.sa_user_id_var)
        self.sa_password_var = tk.StringVar()
        self.sa_password_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt Password: ")
        self.sa_password_entry = ttk.Entry(self.sa_form_frame, show=bullet, width=self.field_width, textvariable=self.sa_password_var)
        self.sa_save_login_btn = ttk.Button(self.sa_form_frame, text="Save login details", command=self.save_sa_login)
        self.sa_change_details_btn = ttk.Button(self.sa_form_frame, text="Change login details",
                                                command=self.change_sa_login)
        self.sa_warning_var = tk.StringVar()
        window_width = self.parent.winfo_width()
        wraplength = window_width/4
        self.sa_warning_lbl = ttk.Label(self.sa_form_frame, wraplength=wraplength,
                                        textvariable=self.sa_warning_var, style="Warning.TLabel")
        self.sa_login_separator = ttk.Separator(self.sa_form_frame, orient=tk.HORIZONTAL)
        self.bundesland_combobox_lbl = ttk.Label(self.sa_form_frame, text="Bundesland: ")
        self.bundesland_combobox = ttk.Combobox(self.sa_form_frame, value=list(bundeslaende.keys()))
        self.calculate_frame = ttk.Frame(self)
        self.sa_login_separator = ttk.Separator(self.calculate_frame, orient=tk.HORIZONTAL)
        self.date_lbl = ttk.Label(self.calculate_frame, text="Submission Month: ")
        self.month_combobox = ttk.Combobox(self.calculate_frame, values=list(combobox_dicts.months.keys()), width=10)
        self.year_combobox = ttk.Combobox(self.calculate_frame,
                                          values=sorted(list(combobox_dicts.years.keys())), width=6)
        self.calculate_btn = ttk.Button(self.calculate_frame, text="Calculate Statistics", command=self.calculate_statistics)
        self.sa_calculate_separator = ttk.Separator(self.calculate_frame, orient=tk.HORIZONTAL)

        #  pack Statistik Amt widgets
        self.sa_title_frame.pack(fill=tk.X)
        self.sa_title_lbl.pack(side=tk.LEFT, padx=20)
        self.sa_title_separator.pack(fill=tk.X, padx=20, pady=2)
        self.sa_form_frame.pack(fill=tk.X)
        self.sa_user_id_lbl.grid(row=0, column=0,sticky=tk.E, padx=20, pady=2)
        self.sa_user_id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(0, 20), pady=2)
        self.sa_password_lbl.grid(row=1, column=0, sticky=tk.E, padx=20, pady=2)
        self.sa_password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(0, 20), pady=2)
        self.bundesland_combobox_lbl.grid(row=2, column=0, sticky=tk.E, padx=20, pady=2)
        self.bundesland_combobox.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.bundesland_combobox.current(0)
        if self.sa_login_details.get(self.sa_property, {}).get("sa_password", "") == "":
            self.sa_warning_lbl.grid(row=3, column=1, sticky=tk.W, pady=2)
            self.sa_save_login_btn.grid(row=3, column=1, sticky=tk.E, padx=20, pady=2)
        else:
            self.sa_user_id_var.set(self.sa_login_details[self.sa_property]["sa_user_id"])
            self.sa_password_var.set(self.sa_login_details[self.sa_property]["sa_password"])
            self.bundesland_combobox.current(
                combobox_dicts.bundeslaende[self.sa_login_details[self.sa_property]["bundesland"]][1])
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.bundesland_combobox.configure(state=tk.DISABLED)
            self.sa_warning_lbl.grid(row=3, column=1, sticky=tk.W, pady=2)
            self.sa_change_details_btn.grid(row=3, column=1, sticky=tk.E, padx=20, pady=2)
        self.calculate_frame.pack(fill=tk.X)
        self.sa_login_separator.grid(row=0, column=0, columnspan=4, sticky=tk.W+tk.E, padx=20)
        self.date_lbl.grid(row=1, column=0, sticky=tk.E, padx=(20, 10), pady=2)
        self.month_combobox.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(0, 10), pady=2)
        self.month_combobox.current(0)
        self.year_combobox.grid(row=1, column=2, sticky=tk.W+tk.E, padx=(0, 10), pady=2)
        self.year_combobox.current(0)
        self.calculate_btn.grid(row=1, column=3, padx=(10, 20), sticky=tk.W, pady=2)
        self.sa_calculate_separator.grid(row=4, column=0, columnspan=4, sticky=tk.W+tk.E, padx=20)

    def check_sa_credential(self, call_origin, ma_property):
        time_now = datetime.now().time()
        eleven = datetime.strptime("23:00", "%H:%M").time()
        eleven_thirty = datetime.strptime("23:30", "%H:%M").time()
        if eleven <= time_now <= eleven_thirty:
            if call_origin == "sa save details":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("Statistics Amt website is not available between 23:00 - 23:30")
            elif call_origin == "send stats":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Statistics Amt website is not available between 23:00 - 23:30")
        else:
            if call_origin == "sa save details":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_warning_var.set("Signing into Statistics Amt site...")
                sa_cred_thread = threading.Thread(
                    target=statistic_amt.check_cred, args=[self.sa_login_details, self.sa_cred_queue, call_origin, ma_property])
                sa_cred_thread.daemon = True
                sa_cred_thread.start()
                self.parent.after(100, self.check_sa_cred_queue)
            elif call_origin == "send stats":
                self.send_to_sa.configure(state=tk.DISABLED)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_options_warning_var.set("Signing into Statistics Amt site...")
                sa_cred_thread = threading.Thread(
                    target=statistic_amt.check_cred, args=[self.sa_login_details, self.sa_cred_queue, call_origin, ma_property])
                sa_cred_thread.daemon = True
                sa_cred_thread.start()
                self.parent.after(100, self.check_sa_cred_queue)

    def save_sa_login(self):
        # self.sa_property = self.ma_properties_combobox.get()
        self.sa_user_id = self.sa_user_id_entry.get()
        self.sa_password = self.sa_password_entry.get()
        self.bundesland = combobox_dicts.bundeslaende[self.bundesland_combobox.get()][0]
        try:
            self.calculate_warning_var.set("")
        except AttributeError:
            pass  # doesn't exist yet

        if self.sa_user_id != "" and self.sa_password != "":
            if self.bundesland != "":
                if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
                    self.sa_login_details[self.sa_property] = {}
                    self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                    self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                    self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland
                    self.sa_login_details[self.sa_property]["beds"] = 0
                else:
                    self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                    self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                    self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland
                with open("data_files/.sa_login.json", 'w', encoding="utf-8") as outfile:
                    json.dump(self.sa_login_details, indent=4, sort_keys=True, fp=outfile)
                    self.check_sa_credential("sa save details", self.sa_property)
            else:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("Please choose a Bundesland.")
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("One or more fields empty!")

    def sa_credential_ok(self, status):
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.sa_warning_var.set("Login successful!")
            self.sa_change_details_btn.grid(row=3, column=1, sticky=tk.E, padx=20, pady=2)
            self.sa_save_login_btn.grid_forget()
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.bundesland_combobox.configure(state=tk.DISABLED)
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Statistics Amt website timed out, please try again later.")
        else:
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.bundesland_combobox.configure(state=tk.DISABLED)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Details incorrect, could not sign in")
            self.sa_user_id_var.set("")
            self.sa_user_id_entry.focus()
            self.sa_password_var.set("")

    def change_sa_login(self):
        self.sa_user_id_var.set("")
        self.sa_user_id_entry.configure(state=tk.ACTIVE)
        self.sa_user_id_entry.focus()
        self.sa_password_var.set("")
        self.sa_password_entry.configure(state=tk.ACTIVE)
        self.bundesland_combobox.configure(state=tk.ACTIVE)
        self.sa_change_details_btn.grid_forget()
        self.sa_save_login_btn.grid(row=3, column=1, sticky=tk.E, padx=20, pady=2)

    def calculate_statistics(self):
        self.sa_warning_var.set("")
        width = self.parent.winfo_width()
        wrap_length = width / 3.0
        self.statistics_results = None
        self.today_date = datetime.strptime(str(datetime.now())[:7], "%Y-%m")
        month_chosen = self.month_combobox.get()
        year_chosen = self.year_combobox.get()
        self.calculate_warning_var = tk.StringVar()
        self.calculate_warning = ttk.Label(self.calculate_frame, style="Warning.TLabel", wraplength=wrap_length,
                                           textvariable=self.calculate_warning_var)
        self.chosen_date_obj = None
        try:
            self.chosen_date_obj = datetime.strptime("{}-{}".format(year_chosen, month_chosen), "%Y-%B")
        except ValueError:
            self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please choose a date first.")

        save_button_visible = self.sa_save_login_btn.winfo_ismapped()
        try:
            date_in_past = self.chosen_date_obj < self.today_date
        except TypeError:
            date_in_past = False
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please choose a date first.")

        if not save_button_visible:
            if os.path.isfile(self.bookings_file):
                if date_in_past:
                    if self.channel_manager != "--Select Channel Manager--":
                        self.calculate_btn.configure(state=tk.DISABLED)
                        calculate_thread = threading.Thread(
                            target=calculate_statistics.calculate, args=[month_chosen, year_chosen, self.bookings_file,
                                                                         self.calculate_statistics_queue, self.channel_manager])
                        calculate_thread.daemon = True
                        calculate_thread.start()
                        self.calculate_progress_bar = ttk.Progressbar(self.calculate_frame, orient="horizontal",
                                                                      mode="determinate")
                        self.calculate_progress_bar.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2)
                        self.calculate_progress_lbl_var = tk.StringVar()
                        self.calculate_progress_lbl = ttk.Label(self.calculate_frame,
                                                                textvariable=self.calculate_progress_lbl_var)
                        self.calculate_progress_lbl.grid(row=2, column=3, sticky=tk.W, padx=20)
                        self.calculate_progress_lbl_var.set("Calculating...")
                        self.parent.after(100, self.process_calculate_progress_bar)
                    else:
                        self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                        self.calculate_warning_var.set("Please choose your channel manager first.")
                else:
                    self.calculate_warning.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
                    self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                    self.calculate_warning_var.set("Please choose a date in the past.")
            else:
                self.calculate_warning.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Wait for bookings to finish downloading.")
        else:
            self.calculate_warning.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please fill in login details above first")

    def setup_sa_options(self):
        window_width = self.parent.winfo_width()
        wrap_length = window_width * 0.45
        #  Statistics Amt options Widgets
        self.sa_options_frame = ttk.Frame(self)
        self.number_beds_var = tk.StringVar()
        self.number_beds_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=beds, justify=tk.RIGHT)
        self.number_beds_entry = ttk.Entry(self.sa_options_frame, width=5, textvariable=self.number_beds_var)
        self.closed_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=closed, justify=tk.RIGHT)
        self.closed_lbl2 = ttk.Label(self.sa_options_frame, style="Options.TLabel", text="dieses Berichtsmonats")
        self.closed_combo = ttk.Combobox(self.sa_options_frame, values=list(combobox_dicts.days_in_month.keys()), width=2)
        self.reopen_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=opened, justify=tk.RIGHT)
        self.reopen_frame = ttk.Frame(self.sa_options_frame)
        self.reopen_entry = ttk.Entry(self.sa_options_frame, width=10)
        self.reopen_combo_d = ttk.Combobox(self.sa_options_frame, values=list(combobox_dicts.days_in_month.keys()), width=2)
        self.reopen_combo_m = ttk.Combobox(self.sa_options_frame, values=list(combobox_dicts.month_num.keys()), width=2)
        self.reopen_combo_y = ttk.Combobox(self.sa_options_frame, values=sorted(list(combobox_dicts.options_years.keys())), width=4)
        self.forced_closed_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=forced_close, justify=tk.RIGHT)
        self.forced_closed_combo = ttk.Combobox(self.sa_options_frame, values=list(combobox_dicts.days_in_month.keys()), width=2)
        self.forced_closed_lbl2 = ttk.Label(self.sa_options_frame, style="Options.TLabel", text="dieses Berichtsmonats")
        self.sa_options_warning_var = tk.StringVar()
        self.sa_options_warning_lbl = ttk.Label(self.sa_options_frame, style="Warning.TLabel", textvariable=self.sa_options_warning_var)
        self.send_to_sa = ttk.Button(self.sa_options_frame, text="SEND",
                                     command=lambda: self.check_sa_credential("send stats", self.sa_property))

        #  Pack Statistcs Amt options widgets
        self.sa_options_frame.pack(fill=tk.X)
        self.number_beds_lbl.grid(row=0, column=0, padx=(20, 10), pady=2, sticky=tk.E)
        self.number_beds_entry.grid(row=0, column=1, columnspan=2, pady=2, sticky=tk.W)
        self.number_beds_entry.focus()
        self.closed_lbl.grid(row=1, column=0, padx=(20, 10), pady=(0, 2), sticky=tk.E)
        self.closed_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 2))
        self.closed_lbl2.grid(row=1, column=2, columnspan=3, padx=(0, 20), pady=(0, 2), sticky=tk.W)
        self.reopen_lbl.grid(row=2, column=0, padx=(20, 10), pady=(0, 2), sticky=tk.E)
        self.reopen_combo_d.grid(row=2, column=1, padx=2, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_m.grid(row=2, column=2, padx=2, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_y.grid(row=2, column=3, padx=2, pady=(0, 2), sticky=tk.W)
        self.forced_closed_lbl.grid(row=3, column=0, padx=(20, 10), pady=(0, 2), sticky=tk.E)
        self.forced_closed_combo.grid(row=3, column=1, sticky=tk.W, pady=(0, 2))
        self.forced_closed_lbl2.grid(row=3, column=2, columnspan=3, padx=(0, 20), pady=(0, 2), sticky=tk.W)
        self.send_to_sa.grid(row=4, column=4, columnspan=4, padx=(0, 20), pady=(0, 2), sticky=tk.W)
        self.sa_options_warning_lbl.grid(row=4, column=0, columnspan=4, sticky=tk.E, padx=10, pady=(0, 2))
        if self.sa_login_details.get(self.sa_property, {}).get("beds", 0) > 0:
            self.number_beds_var.set(self.sa_login_details[self.sa_property]["beds"])
        else:
            self.number_beds_var.set("0")

    def send_statistics(self, status, already_sent_continue=False):
        self.sa_options_warning_var.set("")
        try:
            self.send_sa_progress_var.set("")
            self.send_sa_progress_frame.forget()
        except:
            pass
        if status == "good":
            self.beds = int(self.number_beds_entry.get().replace(",", "").replace(".", ""))
            sa_options_dict = {
                "beds": self.beds,
                "closed on": self.closed_combo.get(),
                "open on": "{}.{}.{}".format(self.reopen_combo_d.get(), self.reopen_combo_m.get(),
                                           self.reopen_combo_y.get()),
                "force closure": self.forced_closed_combo.get(),
                "sub month": "{} {}".format(self.month_combobox.get(), self.year_combobox.get())
            }
            self.sa_login_details[self.sa_property]["beds"] = self.beds
            try:
                if int(self.beds) > 0:
                    with open("data_files/.sa_login.json", 'w', encoding='utf-8') as outfile:
                        json.dump(self.sa_login_details, indent=4, sort_keys=True, fp=outfile)

                        send_stats_thread = threading.Thread(
                            target=statistic_amt.send, args=[self.sa_login_details, sa_options_dict, self.sa_send_queue,
                                                             self.sa_property, self.statistics_results,
                                                             already_sent_continue])
                        send_stats_thread.daemon = True
                        send_stats_thread.start()
                        self.parent.after(100, self.process_sa_send_queue)

                        window_width = self.parent.winfo_width()
                        wrap_length = window_width - 40
                        self.send_sa_progress_frame = ttk.Frame(self)
                        self.options_separator = ttk.Separator(self.send_sa_progress_frame, orient=tk.HORIZONTAL)
                        self.send_sa_progress_bar = ttk.Progressbar(self.send_sa_progress_frame, orient="horizontal",
                                                                    mode="determinate")
                        self.send_sa_progress_var = tk.StringVar()
                        self.send_sa_progress_lbl = ttk.Label(self.send_sa_progress_frame, style="Options.TLabel", wraplength=wrap_length,
                                                              textvariable=self.send_sa_progress_var)
                        self.send_sa_yes_btn = ttk.Button(self.send_sa_progress_frame, text="Yes",
                                                          command=lambda: self.send_statistics("good", True))
                        self.send_sa_no_btn = ttk.Button(self.send_sa_progress_frame, text="No",
                                                         command=lambda: self.send_sa_progress_var.set("Program stopped."))
                        self.send_sa_separator = ttk.Separator(self.send_sa_progress_frame, orient="horizontal")

                        self.send_sa_progress_frame.pack(fill=tk.X)
                        self.options_separator.pack(fill=tk.X, padx=20, pady=(0, 2))
                        self.send_sa_progress_bar.pack(fill=tk.X, padx=20, pady=(0, 2))
                        self.send_sa_progress_lbl.pack(fill=tk.X, padx=20, pady=(0, 2))
                        self.send_sa_separator.pack(fill=tk.X, padx=20)
                elif int(self.beds) == 0:
                    self.send_to_sa.configure(state=tk.ACTIVE)
                    self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                    self.sa_options_warning_var.set("Number of beds must be more than zero!")
            except TypeError and ValueError:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Number of beds must be an integer")
                self.send_to_sa.configure(state=tk.ACTIVE)
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Details incorrect, could not sign in")
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.sa_user_id_var.set("")
            self.sa_user_id_entry.focus()
            self.sa_password_var.set("")
            self.sa_change_details_btn.grid_forget()
            self.sa_save_login_btn.grid(row=3, column=1, sticky=tk.E, padx=20, pady=2)
            self.sa_options_frame.forget()
            self.calculate_btn.configure(state=tk.ACTIVE)
            self.calculate_warning_var.set("")
            self.calculate_progress_lbl.grid_forget()
            self.calculate_progress_bar.grid_forget()
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Statistics Amt website timed out, please try again later.")

    def load_bar(self):
        try:
            message = self.download_queue.get(0)
            if message == "Finished!":
                self.download_lbl_var.set(message)
                self.channel_manager = "MyAllocator"
                self.parent.after(100, self.load_bar)
            elif message == "bookings.csv":
                self.bookings_file = message
            elif isinstance(message, list):
                self.download_bar.grid_forget()
                self.download_lbl.grid_forget()
                self.ma_properties_warn_lbl = ttk.Label(self.ma_properties_frame, style="Warning.TLabel",
                                                        textvariable=self.ma_properties_warn_var)
                self.ma_properties_warn_lbl.grid(row=1, column=1, columnspan=2, sticky=tk.W)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.ma_properties_warn_var.set(message[1])
            else:
                self.download_bar.step(message)
                self.parent.after(100, self.load_bar)
        except queue.Empty:
            self.parent.after(100, self.load_bar)

    def check_ma_cred_queue(self):
        try:
            message = self.ma_cred_queue.get(0)
            if message == "ma ok ma save details":
                self.ma_credential_ok("good")
            elif message == "ma not ok ma save details":
                self.ma_credential_ok("bad")
            elif message == "ma ok get properties":
                self.get_properties("good")
            elif message == "ma not ok get properties":
                self.get_properties("bad")
            elif isinstance(message, list):
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.ma_warning_var.set(message[1])
        except queue.Empty:
            self.parent.after(100, self.check_ma_cred_queue)

    def check_sa_cred_queue(self):
        try:
            message = self.sa_cred_queue.get(0)
            if message == "sa ok sa save details":
                self.sa_credential_ok("good")
                self.parent.after(100, self.check_sa_cred_queue)
            elif message == "sa not ok sa save details":
                self.sa_credential_ok("bad")
            elif message == "sa page timeout sa save details":
                self.sa_credential_ok("failed")
            elif message == "sa address bad sa save details":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("It seems you haven't saved your address on your Statistik Amt profile, please "
                                        "do so before continuing")
            elif message == "sa ok send stats":
                self.send_statistics("good")
            elif message == "sa not ok send stats":
                self.send_statistics("bad")
            elif message == "sa page timeout send stats":
                self.send_statistics("failed")
        except queue.Empty:
            self.parent.after(100, self.check_sa_cred_queue)

    def process_calculate_progress_bar(self):
        try:
            message = self.calculate_statistics_queue.get(0)
            if message == "Finished!":
                self.calculate_progress_lbl_var.set(message)
                self.setup_sa_options()
                self.parent.after(100, self.process_calculate_progress_bar)
            elif message == "wrong channel":
                self.calculate_warning.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Could not calculate the statistics properly, please make sure you have"
                                               " chosen the correct channel manager above and try again.")
            elif isinstance(message, OrderedDict):
                self.statistics_results = message
            else:
                self.calculate_progress_bar.step(message)
                self.parent.after(25, self.process_calculate_progress_bar)
        except queue.Empty:
            self.parent.after(100, self.process_calculate_progress_bar)

    def process_sa_send_queue(self):
        try:
            message = self.sa_send_queue.get(0)
            if message == "already sent":
                self.send_sa_progress_var.set("You have already sent statistics for this month, would you like to send "
                                              "them again?")
                self.send_sa_progress_bar.forget()
                self.send_sa_yes_btn.pack(side=tk.LEFT, padx=(20, 10))
                self.send_sa_no_btn.pack(side=tk.LEFT)
            elif isinstance(message, int):
                self.send_sa_progress_bar.step(message)
                self.parent.after(10, self.process_sa_send_queue)
            elif message == "Finished":
                self.send_sa_progress_var.set("Statistics successfully sent!")
            elif message == "no date":
                self.send_sa_progress_bar.forget()
                self.send_sa_progress_var.set("Sorry, the Statistics Amt website is not allowing statistics to be "
                                              "submitted for the month you have chosen, please choose a different "
                                              "month and try again.")
            else:
                self.send_sa_progress_var.set(message)
                self.parent.after(10, self.process_sa_send_queue)
        except queue.Empty:
            self.parent.after(100, self.process_sa_send_queue)


def main():
    root = tk.Tk()
    # root.geometry("100x100+500+100")
    # root.minsize(height=600, width=600)
    # root.maxsize(height=600, width=600)
    root.wm_title("Setup")
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
