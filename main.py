import os
import sys
import threading
import queue
from datetime import datetime
import locale
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog
from idlelib import ToolTip as TT
from PIL import Image, ImageTk
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
            upload_button_font = "-size 14"
            self.field_width = 40
        else:
            locale.setlocale(locale.LC_TIME, "de_DE")
            warning_fs = "-size 10"
            upload_button_font = "-size 16"
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
        self.sa_change_details_flag = "no"

        from_file = []
        from_myallocator = []
        for key in self.sa_login_details.keys():
            if "User ID" in key:
                from_file.append(key.replace("User ID ", ""))
            else:
                from_myallocator.append(self.sa_login_details[key]["sa_user_id"])
        double_ups = 0
        for user in from_file:
            if user in from_myallocator:
                double_ups += 1
        self.sa_logins_used = len(from_file) + len(from_myallocator) - double_ups

        # self.theme = ttk.Style()
        # self.theme.theme_create("dark_theme", parent="alt", settings={
        #     "TFrame": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
        #     "TLabel": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
        #     "TButton": {"configure": {"background": "#242424", "foreground": "#0FF1F0",
        #                               "relief": "raised", "padding": 2
        #                               }},
        #     "TCheckbutton": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
        #     "TEntry": {"configure": {"background": "#242424", "foreground": "#242424"}},
        #     "Horizontal.TProgressbar": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}}
        # })
        # self.theme.theme_use("dark_theme")

        self.program_title = ttk.Style()
        self.program_title.configure("ProgramTitle.TLabel", font=("Abel", 48))
        self.label_title = ttk.Style()
        self.label_title.configure("title.TLabel", font="-size 14")
        self.warning_lbl_style = ttk.Style()
        self.warning_lbl_style.configure('Warning.TLabel', font=warning_fs, foreground='red')
        self.options_lbl_style = ttk.Style()
        self.options_lbl_style.configure('Options.TLabel')
        self.upload_style_buttons = ttk.Style()
        self.upload_style_buttons.configure("Upload.TButton", font=upload_button_font, padding=(0, 10, 0, 10))
        self.back_button_style = ttk.Style()
        self.back_button_style.configure("Back.TButton", padding=(10, 2, 10, 2))

        self.title_frame = ttk.Frame(self)
        self.title_frame.columnconfigure(0, weight=1)
        self.title_frame.grid(row=0, column=0)

        title_png = Image.open(".images/title_img.png")
        title_photo = ImageTk.PhotoImage(title_png)
        self.title = ttk.Label(self.title_frame, style="ProgramTitle.TLabel", image=title_photo)
        self.title.image = title_photo
        self.title.grid(row=0, column=0, sticky=tk.W+tk.E, padx=20, pady=10)
        self.upload_style()

    def upload_style(self, origin="init"):
        self.upload_style_frame = ttk.Frame(self)
        self.upload_style_frame.columnconfigure(0, weight=1)
        self.upload_style_frame.columnconfigure(1, weight=1)
        self.upload_style_title = ttk.Label(self.upload_style_frame, text="Upload with...", style="title.TLabel")
        self.upload_style_separator = ttk.Separator(self.upload_style_frame, orient="horizontal")
        self.upload_myallocator_btn = ttk.Button(self.upload_style_frame,  style="Upload.TButton", text="MyAllocator",
                                                 command=self.setup_ma)
        self.upload_myallocator_tooltip = TT.ToolTip(self.upload_myallocator_btn, "Provide MyAllocator login details "
                                                                                  "to be able to\ndownload all "
                                                                                  "bookings automacially.")
        self.upload_file_btn = ttk.Button(self.upload_style_frame, style="Upload.TButton", text="From file",
                                          command=self.upload_bookings)
        self.upload_file_tooltip = TT.ToolTip(self.upload_file_btn, "Upload a 'csv' file of your bookings from your "
                                                                    "computer")
        if origin == "myallocator":
            self.ma_form_frame.grid_forget()
        if origin == "upload bookings":
            self.browse_files_frame.grid_forget()

        self.upload_style_frame.grid(row=1, column=0, padx=20, sticky=tk.W+tk.E)
        self.upload_style_title.grid(row=0, column=0, pady=2, sticky=tk.W)
        self.upload_style_separator.grid(row=1, column=0, columnspan=2, pady=2, sticky=tk.W+tk.E)
        self.upload_myallocator_btn.grid(row=2, column=0, padx=(0, 30), pady=10, sticky=tk.E)
        self.upload_file_btn.grid(row=2, column=1, pady=10, sticky=tk.W)

    def setup_ma(self):
        self.upload_style_frame.grid_forget()
        self.parent.update()
        bullet = "\u2022"
        #  MyAllocator login widgets
        self.ma_form_frame = ttk.Frame(self)
        self.ma_form_frame.columnconfigure(1, weight=1)
        self.ma_title_separator = ttk.Separator(self.ma_form_frame, orient="horizontal")
        self.ma_form_separator = ttk.Separator(self.ma_form_frame, orient="horizontal")
        self.ma_title_lbl = ttk.Label(self.ma_form_frame, style="title.TLabel", text="MyAllocator login details")
        self.ma_username_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Username: ")
        self.ma_username_var = tk.StringVar()
        self.ma_username_entry = ttk.Entry(self.ma_form_frame, width=self.field_width, textvariable=self.ma_username_var)
        self.ma_password_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Password: ")
        self.ma_password_var = tk.StringVar()
        self.ma_password_entry = ttk.Entry(self.ma_form_frame, show=bullet, width=self.field_width, textvariable=self.ma_password_var)
        self.ma_save_login_btn = ttk.Button(self.ma_form_frame, text="Save login details",
                                            command=self.save_ma_login)
        self.ma_save_tooltip = TT.ToolTip(self.ma_save_login_btn, "Save your MyAllocator login details for future use.")
        self.ma_get_properties_btn = ttk.Button(self.ma_form_frame, text="Get Properties",
                                                command=lambda: self.check_ma_credential("get properties"))
        self.ma_properties_tooltip = TT.ToolTip(self.ma_get_properties_btn, "Retrieve your properties from your "
                                                                            "MyAllocator account.")
        self.ma_change_detials_btn = ttk.Button(self.ma_form_frame, text="Change login details",
                                                command=self.ma_change_details)
        self.ma_change_details_tooltip = TT.ToolTip(self.ma_change_detials_btn, "Change your saved MyAllocator login "
                                                                                "details.")
        self.ma_back_btn = ttk.Button(self.ma_form_frame, style="Back.TButton", text="Back", command=lambda: self.upload_style("myallocator"))
        self.ma_warning_var = tk.StringVar()
        self.ma_warning = ttk.Label(self.ma_form_frame, style="Warning.TLabel", wraplength=self.parent.winfo_width()*.6,
                                    textvariable=self.ma_warning_var)

        #  pack MyAllocator widgets
        self.ma_form_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=20)
        self.ma_title_lbl.grid(row=0, column=0, columnspan=3, pady=2, sticky=tk.W)
        self.ma_title_separator.grid(row=1, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.ma_username_lbl.grid(row=2, column=0, sticky=tk.E, padx=(0, 20), pady=2)
        self.ma_username_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.ma_username_var.set(self.ma_login_details["ma_username"])
        self.ma_password_lbl.grid(row=3, column=0, sticky=tk.E, padx=(0, 20), pady=2)
        self.ma_password_entry.grid(row=3, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.ma_password_entry.focus()
        self.ma_password_var.set(self.ma_login_details["ma_password"])
        self.ma_warning.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=2)
        self.ma_form_separator.grid(row=6, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        if self.ma_login_details["ma_password"] != "":
            self.ma_change_detials_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_get_properties_btn.grid(row=5, column=1, padx=10, pady=2, sticky=tk.E)
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
        else:
            self.ma_back_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_save_login_btn.grid(row=5, column=1, padx=10, pady=2, sticky=tk.E)

    def ma_change_details(self):
        self.parent.update()
        self.ma_username_entry.configure(state=tk.ACTIVE)
        self.ma_password_entry.configure(state=tk.ACTIVE)
        self.ma_password_var.set("")
        self.ma_password_entry.focus()
        self.ma_change_detials_btn.grid_forget()
        self.ma_get_properties_btn.grid_forget()
        self.ma_save_login_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
        self.parent.update()

    def check_ma_credential(self, call_origin):
        self.parent.update()
        self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
        self.ma_warning_var.set("Trying to log into MyAllocator...")
        ma_cred_thread = threading.Thread(
            target=myallocator.check_cred, args=[self.ma_login_details, self.ma_cred_queue, call_origin])
        ma_cred_thread.daemon = True
        ma_cred_thread.start()
        self.parent.after(100, self.check_ma_cred_queue)

    def save_ma_login(self):
        self.parent.update()
        self.ma_username = self.ma_username_entry.get()
        self.ma_password = self.ma_password_entry.get()

        if self.ma_username != '' and self.ma_password != '':
            self.ma_login_details["ma_username"] = self.ma_username
            self.ma_login_details["ma_password"] = self.ma_password
            self.check_ma_credential("ma save details")
        elif self.ma_username == '' or self.ma_password == '':
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("One or more fields are empty!")

    def ma_credential_ok(self, status):
        self.parent.update()
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Login successful!")
            self.ma_save_login_btn.grid_forget()
            self.ma_back_btn.grid_forget()
            self.ma_change_detials_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_get_properties_btn.grid(row=5, column=1, padx=10, pady=2, sticky=tk.E)
            self.ma_get_properties_btn.configure(state=tk.ACTIVE)
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
            self.myallocator_login = True
            with open("data_files/.ma_login.json", "w", encoding='utf-8') as outfile:
                json.dump(self.ma_login_details, indent=4, sort_keys=True, fp=outfile)
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_login_details["ma_password"] = ""

    def get_properties(self, status):
        self.parent.update()
        self.ma_get_properties_btn.configure(state=tk.DISABLED)
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Login successful!")
            self.ma_get_properties_btn.grid_forget()
            self.ma_change_detials_btn.grid_forget()
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
            property_process = multiprocessing.Process(target=myallocator.get_properties, args=(self.ma_login_details,))
            property_process.daemon = True
            property_process.start()
            property_process.join()
            self.load_properties()
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_username_entry.configure(state=tk.ACTIVE)
            self.ma_password_entry.configure(state=tk.ACTIVE)
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_change_detials_btn.grid_forget()
            self.ma_get_properties_btn.grid_forget()
            self.ma_save_login_btn.grid(row=5, column=2, pady=2, sticky=tk.E)

    def load_properties(self):
        self.parent.update()
        self.ma_properties = dict()
        with open("data_files/properties.json") as propfile:
            self.ma_properties = json.load(propfile)

            self.ma_properties_lbl = ttk.Label(self.ma_form_frame, text="Property: ")
            self.ma_properties_combobox = ttk.Combobox(self.ma_form_frame, state="readonly",
                                                       values=sorted(list(self.ma_properties.keys())))
            self.ma_download_btn = ttk.Button(self.ma_form_frame, text="Download Bookings",
                                                command=self.download_bookings)
            self.ma_properties_serparator = ttk.Separator(self.ma_form_frame, orient="horizontal")
            self.ma_properties_warn_var = tk.StringVar()
            self.ma_properties_warn_lbl = ttk.Label(self.ma_form_frame, style="Warning.TLabel",
                                                    textvariable=self.ma_properties_warn_var)

            self.ma_properties_lbl.grid(row=7, column=0, padx=(0, 20), pady=2, sticky=tk.E)
            self.ma_properties_combobox.grid(row=7, column=1, padx=(0, 20), pady=2, sticky=tk.W)
            self.ma_download_btn.grid(row=7, column=2, pady=2, sticky=tk.E)
            self.ma_properties_combobox.current(0)
            self.ma_properties_serparator.grid(row=10, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)

    def upload_bookings(self):
        self.upload_style_frame.grid_forget()
        self.parent.update()
        self.browse_files_frame = ttk.Frame(self)
        self.browse_files_frame.columnconfigure(1, weight=1)
        self.browse_files_title_lbl = ttk.Label(self.browse_files_frame, text="Bookings Upload", style="title.TLabel")
        self.browse_files_title_separator = ttk.Separator(self.browse_files_frame, orient="horizontal")
        self.browse_files_btn = ttk.Button(self.browse_files_frame, text="Browse...", command=self.browse_csv)
        self.browse_files_tooptip = TT.ToolTip(self.browse_files_btn, "Upload a 'csv' file of all your bookings "
                                                                      "(Can be downloaded from the channel manager you"
                                                                      " use.")
        self.browse_files_var = tk.StringVar()
        self.browse_files_lbl = ttk.Entry(self.browse_files_frame, width=self.field_width+5, textvariable=self.browse_files_var)
        self.channel_lbl = ttk.Label(self.browse_files_frame, text="Channel Manager:")
        self.channel_combobox = ttk.Combobox(self.browse_files_frame, state="readonly", width=30, values=sorted(list(combobox_dicts.channel_managers.keys())))
        self.channel_combobox.bind("<<ComboboxSelected>>", self.channel_selected)
        self.browse_files_separator = ttk.Separator(self.browse_files_frame, orient="horizontal")
        self.browse_back_btn = ttk.Button(self.browse_files_frame, style="Back.TButton", text="Back", command=lambda: self.upload_style("upload bookings"))

        self.browse_files_frame.grid(row=1, column=0, padx=20, sticky=tk.W+tk.E)
        self.browse_files_title_lbl.grid(row=0, column=0, columnspan=2, pady=2, sticky=tk.W)
        self.browse_files_title_separator.grid(row=1, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
        self.browse_files_btn.grid(row=2, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.browse_files_lbl.grid(row=2, column=1, columnspan=2, pady=2, sticky=tk.W+tk.E)
        self.channel_lbl.grid(row=3, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.channel_combobox.grid(row=3, column=1, columnspan=2, pady=2, sticky=tk.W)
        self.channel_combobox.current(0)
        self.browse_back_btn.grid(row=4, column=1, pady=2, sticky=tk.E)
        self.browse_files_separator.grid(row=5, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
        self.update()

    def browse_csv(self):
        self.bookings_file = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
        self.browse_files_var.set(self.bookings_file)
        if self.channel_combobox.get() != "--Select Channel Manager--":
            self.setup_sa(self.browse_files_frame)

    def channel_selected(self, event):
        try:
            self.sa_form_frame.grid_forget()
            self.calculate_frame.forget()
        except:
            pass
        self.channel_manager = self.channel_combobox.get()
        if self.browse_files_lbl.get() != "":
            self.setup_sa(self.browse_files_frame)

    def download_bookings(self):
        self.parent.update()
        self.ma_warning_var.set("")
        property = self.ma_properties[self.ma_properties_combobox.get()][0]
        if property != "" and self.ma_properties_warn_var.get() in ["", "Finished!"]:
            self.ma_download_btn.configure(state=tk.DISABLED)
            self.ma_properties_combobox.configure(state=tk.DISABLED)
            try:
                self.sa_form_frame.grid_forget()
                self.calculate_frame.forget()
            except:
                pass
            download_process = multiprocessing.Process(
                target=myallocator.download_bookings_csv, args=(self.ma_login_details, property, self.download_queue))
            download_process.daemon = True
            download_process.start()
            self.download_bar = ttk.Progressbar(self.ma_form_frame, orient="horizontal", mode="determinate")
            self.download_bar.grid(row=8, column=1, pady=2, sticky=tk.W+tk.E)
            self.download_lbl_var = tk.StringVar()
            self.download_lbl = ttk.Label(self.ma_form_frame, textvariable=self.download_lbl_var)
            self.download_lbl.grid(row=8, column=2, pady=2, sticky=tk.E)
            self.download_lbl_var.set("Downloading...")
            self.parent.after(100, self.load_bar)
            self.setup_sa(self.ma_form_frame)
        else:
            self.ma_properties_warn_lbl.grid(row=8, column=1, columnspan=2, sticky=tk.W)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_properties_warn_var.set("Please choose a property first.")

    def setup_sa(self, frame, sa_property="Upload Bookings"):
        try:
            self.browse_files_btn.configure(state=tk.DISABLED)
            self.browse_back_btn.grid_forget()
        except Exception:
            pass
        self.parent.update()
        bullet = "\u2022"
        bundeslaende = combobox_dicts.bundeslaende
        try:
            self.sa_property = self.ma_properties_combobox.get()
        except AttributeError:
            self.sa_property = sa_property

        #  Statistik Amt login widgets
        self.sa_form_frame = ttk.Frame(self)
        self.sa_form_frame.columnconfigure(1, weight=1)
        self.sa_title_lbl = ttk.Label(self.sa_form_frame, style="title.TLabel", text="Statistik Amt login details")
        self.sa_title_separator = ttk.Separator(self.sa_form_frame, orient="horizontal")
        self.sa_user_id_var = tk.StringVar()
        self.sa_user_id_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt ID nr: ")
        self.sa_user_id_entry = ttk.Entry(self.sa_form_frame, textvariable=self.sa_user_id_var, width=self.field_width)
        self.sa_password_var = tk.StringVar()
        self.sa_password_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt Password: ")
        self.sa_password_entry = ttk.Entry(self.sa_form_frame, show=bullet, width=self.field_width, textvariable=self.sa_password_var)
        self.sa_user_id_combobox = ttk.Combobox(self.sa_form_frame, state="readonly", values=list(user_id for user_id in self.sa_login_details.keys() if "User ID" in user_id))
        self.sa_user_id_combobox.bind("<<ComboboxSelected>>", self.load_from_combobox)
        self.sa_save_login_btn = ttk.Button(self.sa_form_frame, text="Save login details", command=self.save_sa_login)
        self.sa_save_login_tooltip = TT.ToolTip(self.sa_save_login_btn, "Save your Statistik Amt login info for future"
                                                                        " use")
        self.sa_change_details_btn = ttk.Button(self.sa_form_frame, text="Change password",
                                                command=lambda: self.change_sa_login(origin))
        self.sa_change_details_tooltip = TT.ToolTip(self.sa_change_details_btn, "Change your saved Statistik Amt "
                                                                                " password for this User ID.")
        self.sa_add_login_details_btn = ttk.Button(self.sa_form_frame, text="Add login details",
                                                   command=lambda: self.change_sa_login(origin, "no"))
        self.sa_add_login_details_tooltip = TT.ToolTip(self.sa_add_login_details_btn, "Add a new login User ID and "
                                                                                      "password for the Statistik Amt")
        self.sa_warning_var = tk.StringVar()
        window_width = self.parent.winfo_width()
        wraplength = window_width/4
        self.sa_warning_lbl = ttk.Label(self.sa_form_frame, wraplength=wraplength,
                                        textvariable=self.sa_warning_var, style="Warning.TLabel")
        self.sa_login_separator = ttk.Separator(self.sa_form_frame, orient="horizontal")
        self.bundesland_combobox_lbl = ttk.Label(self.sa_form_frame, text="Bundesland: ")
        self.bundesland_combobox = ttk.Combobox(self.sa_form_frame, state="readonly", value=list(bundeslaende.keys()))
        self.sa_login_separator = ttk.Separator(self.sa_form_frame, orient="horizontal")
        self.calculate_frame = ttk.Frame(self)
        self.calculate_frame.columnconfigure(3, weight=1)
        self.date_lbl = ttk.Label(self.calculate_frame, text="Submission Month: ")
        self.month_combobox = ttk.Combobox(self.calculate_frame, state="readonly", values=list(combobox_dicts.months.keys()), width=12)
        self.year_combobox = ttk.Combobox(self.calculate_frame, state="readonly",
                                          values=sorted(list(combobox_dicts.years.keys())), width=7)
        self.calculate_btn = ttk.Button(self.calculate_frame, text="Calculate Statistics", command=self.calculate_statistics)
        self.sa_calculate_separator = ttk.Separator(self.calculate_frame, orient="horizontal")

        #  pack Statistik Amt widgets
        self.sa_form_frame.grid(row=3, column=0, padx=20, sticky=tk.W+tk.E)

        self.sa_title_lbl.grid(row=0, column=0, columnspan=4, pady=2, sticky=tk.W)
        self.sa_title_separator.grid(row=1, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.sa_user_id_lbl.grid(row=2, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        if self.sa_property == "Upload Bookings":
            if len(list(user_id for user_id in self.sa_login_details.keys() if "User ID" in user_id)) == 0:
                self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
            else:
                self.sa_user_id_combobox.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
                origin = "file upload"
        else:
            self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
            origin = "myallocator"
        self.sa_password_lbl.grid(row=3, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.sa_password_entry.grid(row=3, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
        self.bundesland_combobox_lbl.grid(row=4, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.bundesland_combobox.grid(row=4, column=1, columnspan=3, pady=2, sticky=tk.W)
        self.bundesland_combobox.current(0)
        if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
            self.sa_warning_lbl.grid(row=5, column=1, pady=2, sticky=tk.W)
            self.sa_save_login_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
        else:
            self.sa_user_id_var.set(self.sa_login_details[self.sa_property]["sa_user_id"])
            self.sa_password_var.set(self.sa_login_details[self.sa_property]["sa_password"])
            self.bundesland_combobox.current(
                combobox_dicts.bundeslaende[self.sa_login_details[self.sa_property]["bundesland"]][1])
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.bundesland_combobox.configure(state=tk.DISABLED)
            self.sa_warning_lbl.grid(row=5, column=1, sticky=tk.W, pady=2)
            self.sa_change_details_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
        self.sa_login_separator.grid(row=6, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.calculate_frame.grid(row=4, column=0, sticky=tk.W+tk.E)
        self.calculate_frame.columnconfigure(0, weight=1)
        self.date_lbl.grid(row=0, column=0, padx=20, pady=2, sticky=tk.E)
        self.month_combobox.grid(row=0, column=1, padx=(0, 5), pady=2, sticky=tk.W)
        self.month_combobox.current(0)
        self.year_combobox.grid(row=0, column=2, padx=(0, 10), pady=2, sticky=tk.E)
        self.year_combobox.current(0)
        self.calculate_btn.grid(row=0, column=3, padx=20, pady=2, sticky=tk.E)
        self.sa_calculate_separator.grid(row=2, column=0, columnspan=4, padx=20, pady=2, sticky=tk.W+tk.E)

    def load_from_combobox(self, event):
        self.sa_password_var.set(self.sa_login_details[self.sa_user_id_combobox.get()]["sa_user_id"])
        self.bundesland_combobox.current(
            combobox_dicts.bundeslaende[self.sa_login_details[self.sa_user_id_combobox.get()]["bundesland"]][1]
        )
        self.sa_property = self.sa_user_id_combobox.get()
        self.sa_add_login_details_btn.grid(row=5, column=2, sticky=tk.E, pady=2)
        self.sa_change_details_btn.grid(row=5, column=3, sticky=tk.E, padx=(5, 0), pady=2)
        self.sa_save_login_btn.grid_forget()
        self.sa_user_id_combobox.configure(state=tk.DISABLED)
        self.sa_password_entry.configure(state=tk.DISABLED)
        self.bundesland_combobox.configure(state=tk.DISABLED)

    def check_sa_credential(self, call_origin, ma_property):
        self.parent.update()
        time_now = datetime.now().time()
        eleven = datetime.strptime("22:55", "%H:%M").time()
        eleven_thirty = datetime.strptime("23:35", "%H:%M").time()
        if eleven <= time_now <= eleven_thirty:
            if call_origin == "sa save details yes" or call_origin == "sa save details no":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("Statistics Amt website is not available between 23:00 - 23:30")
            elif call_origin == "send stats":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Statistics Amt website is not available between 23:00 - 23:30")
        else:
            if call_origin == "sa save details yes" or call_origin == "sa save details no":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_warning_var.set("Signing into Statistics Amt site...")
                sa_cred_thread = threading.Thread(
                    target=statistic_amt.check_cred, args=[self.sa_login_details, self.sa_cred_queue, call_origin, ma_property])
                sa_cred_thread.daemon = True
                sa_cred_thread.start()
                self.parent.after(100, self.check_sa_cred_queue)
            elif call_origin == "send stats":
                self.send_to_sa_btn.configure(state=tk.DISABLED)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_options_warning_var.set("Signing into Statistics Amt site...")
                sa_cred_thread = threading.Thread(
                    target=statistic_amt.check_cred, args=[self.sa_login_details, self.sa_cred_queue, call_origin, ma_property])
                sa_cred_thread.daemon = True
                sa_cred_thread.start()
                self.parent.after(100, self.check_sa_cred_queue)

    def save_sa_login(self):
        self.parent.update()
        self.sa_add_login_details_btn.grid_forget()
        if self.sa_user_id_entry.get() != "":
            self.sa_user_id = self.sa_user_id_entry.get()
        else:
            self.sa_user_id = self.sa_user_id_combobox.get().replace("User ID ", "")
        self.sa_password = self.sa_password_entry.get()
        self.bundesland = combobox_dicts.bundeslaende[self.bundesland_combobox.get()][0]
        try:
            self.calculate_warning_var.set("")
        except AttributeError:
            pass  # doesn't exist yet

        if self.sa_user_id != "" and self.sa_password != "":
            if self.bundesland != "":
                if self.sa_property == "Upload Bookings":
                    self.sa_property = "User ID {}".format(self.sa_user_id)
                    if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
                        self.sa_login_details[self.sa_property] = {}
                        self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                        self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                        self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland
                        self.sa_login_details[self.sa_property]["beds"] = 0
                    else:
                        if self.sa_logins_used < 3:
                            self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                            self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                            self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland
                            self.sa_login_details[self.sa_property]["beds"] = 0
                elif self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
                    self.sa_login_details[self.sa_property] = {}
                    self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                    self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                    self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland
                    self.sa_login_details[self.sa_property]["beds"] = 0
                else:
                    self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                    self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                    self.sa_login_details[self.sa_property]["bundesland"] = self.bundesland

                self.check_sa_credential("sa save details {}".format(self.sa_change_details_flag), self.sa_property)
            else:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("Please choose a Bundesland.")
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("One or more fields empty!")

    def sa_credential_ok(self, status):
        self.parent.update()
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.sa_warning_var.set("Login successful!")
            self.sa_change_details_btn.grid(row=5, column=3, padx=(10, 0), pady=2, sticky=tk.E)
            self.sa_save_login_btn.grid_forget()
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.bundesland_combobox.configure(state=tk.DISABLED)
            with open("data_files/.sa_login.json", 'w', encoding="utf-8") as outfile:
                    json.dump(self.sa_login_details, indent=4, sort_keys=True, fp=outfile)
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Statistics Amt website timed out, please try again later.")
        elif status[0] == "bad no":
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.bundesland_combobox.configure(state="readonly")
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Details incorrect, could not sign in")
            self.sa_user_id_var.set("")
            self.sa_user_id_entry.focus()
            self.sa_password_var.set("")
            del self.sa_login_details[status[1]]
            self.sa_property = "Upload Bookings"
        elif status == "bad yes":
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.bundesland_combobox.configure(state="readonly")
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Details incorrect, could not sign in")
            self.sa_password_var.set("")
            self.sa_password_entry.focus()

    def change_sa_login(self, origin, flag="yes"):
        self.parent.update()
        self.sa_change_details_flag = flag
        if origin == "file upload":
            self.sa_user_id_combobox.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.sa_password_var.set("")
        self.sa_password_entry.configure(state=tk.ACTIVE)
        self.sa_password_entry.focus()
        self.bundesland_combobox.configure(state="readonly")
        self.sa_change_details_btn.grid_forget()

        self.sa_save_login_btn.grid(row=5, column=3, sticky=tk.E, pady=2)
        if flag == "no":
            self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
            self.sa_user_id_combobox.grid_forget()
            self.sa_add_login_details_btn.grid_forget()
            self.sa_user_id_entry.focus()

    def calculate_statistics(self):
        self.parent.update()
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
            self.calculate_warning.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=2)
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
                        self.calculate_progress_bar.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2)
                        self.calculate_progress_lbl_var = tk.StringVar()
                        self.calculate_progress_lbl = ttk.Label(self.calculate_frame,
                                                                textvariable=self.calculate_progress_lbl_var)
                        self.calculate_progress_lbl.grid(row=1, column=3, sticky=tk.W, padx=20)
                        self.calculate_progress_lbl_var.set("Calculating...")
                        self.parent.after(100, self.process_calculate_progress_bar)
                    else:
                        self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                        self.calculate_warning_var.set("Please choose your channel manager first.")
                else:
                    self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
                    self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                    self.calculate_warning_var.set("Please choose a date in the past.")
            else:
                self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Wait for bookings to finish downloading.")
        else:
            self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please fill in login details above first")

    def setup_sa_options(self):
        self.parent.update()
        window_width = self.parent.winfo_width()
        wrap_length = window_width * 0.7
        #  Statistics Amt options Widgets
        self.sa_options_frame = ttk.Frame(self)
        self.sa_options_frame.columnconfigure(4, weight=1)
        self.number_beds_var = tk.StringVar()
        self.number_beds_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=beds, justify=tk.RIGHT)
        self.number_beds_entry = ttk.Entry(self.sa_options_frame, width=5, textvariable=self.number_beds_var)
        self.closed_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=closed, justify=tk.RIGHT)
        self.closed_lbl2 = ttk.Label(self.sa_options_frame, style="Options.TLabel", font="-size 7", text=".dieses Berichtsmonats")
        self.closed_combo = ttk.Combobox(self.sa_options_frame, state="readonly", values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.reopen_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=opened, justify=tk.RIGHT)
        self.reopen_frame = ttk.Frame(self.sa_options_frame)
        self.reopen_entry = ttk.Entry(self.sa_options_frame, width=10)
        self.reopen_combo_d = ttk.Combobox(self.sa_options_frame, state="readonly", values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.reopen_combo_m = ttk.Combobox(self.sa_options_frame, state="readonly", values=list(combobox_dicts.month_num.keys()), width=4)
        self.reopen_combo_y = ttk.Combobox(self.sa_options_frame, state="readonly", values=sorted(list(combobox_dicts.options_years.keys())), width=5)
        self.forced_closed_lbl = ttk.Label(self.sa_options_frame, style="Options.TLabel", wraplength=wrap_length, text=forced_close, justify=tk.RIGHT)
        self.forced_closed_combo = ttk.Combobox(self.sa_options_frame, state="readonly", values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.forced_closed_lbl2 = ttk.Label(self.sa_options_frame, style="Options.TLabel", font="-size 7", text=".dieses Berichtsmonats")
        self.sa_options_warning_var = tk.StringVar()
        self.sa_options_warning_lbl = ttk.Label(self.sa_options_frame, style="Warning.TLabel", textvariable=self.sa_options_warning_var)
        self.send_to_sa_btn = ttk.Button(self.sa_options_frame, style="Upload.TButton", text="SEND",
                                     command=lambda: self.check_sa_credential("send stats", self.sa_property))
        self.send_to_sa_tooltip = TT.ToolTip(self.send_to_sa_btn, "Send your calculated statistics for the chosen "
                                                                  "month to the Statistik Amt.")
        self.options_separator = ttk.Separator(self.sa_options_frame, orient="horizontal")

        #  Pack Statistcs Amt options widgets
        self.sa_options_frame.grid(row=5, column=0, padx=20, sticky=tk.W+tk.E)
        self.number_beds_lbl.grid(row=0, column=0, padx=(0, 10), pady=2, sticky=tk.E)
        self.number_beds_entry.grid(row=0, column=1, columnspan=2, pady=2, sticky=tk.W)
        self.number_beds_entry.focus()
        self.closed_lbl.grid(row=1, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.closed_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 2))
        self.closed_lbl2.grid(row=1, column=2, columnspan=3, pady=(0, 2), sticky=tk.W)
        self.reopen_lbl.grid(row=2, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.reopen_combo_d.grid(row=2, column=1, padx=0, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_m.grid(row=2, column=2, padx=2, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_y.grid(row=2, column=3, padx=2, pady=(0, 2), sticky=tk.W)
        self.forced_closed_lbl.grid(row=3, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.forced_closed_combo.grid(row=3, column=1, sticky=tk.W, pady=(0, 2))
        self.forced_closed_lbl2.grid(row=3, column=2, columnspan=3, pady=(0, 2), sticky=tk.W)
        self.send_to_sa_btn.grid(row=4, column=1, columnspan=3, pady=(0, 10), sticky=tk.E)
        self.sa_options_warning_lbl.grid(row=4, column=0, sticky=tk.E, padx=10, pady=(0, 2))
        self.options_separator.grid(row=5, column=0, columnspan=6, pady=2, sticky=tk.W+tk.E)
        if self.sa_login_details.get(self.sa_property, {}).get("beds", 0) > 0:
            self.number_beds_var.set(self.sa_login_details[self.sa_property]["beds"])
        try:
            self.send_sa_progress_frame.grid_forget()
        except AttributeError:
            pass  # Does not exist yet

    def send_statistics(self, status, already_sent_continue=False):
        self.parent.update()
        self.sa_options_warning_var.set("")
        try:
            self.send_sa_progress_var.set("")
            self.send_sa_progress_frame.forget()
        except:
            pass
        if status == "good":
            if already_sent_continue:
                self.send_sa_progress_var.set("")
                self.send_sa_progress_bar.grid_forget()
                self.send_sa_yes_btn.grid_forget()
                self.send_sa_no_btn.grid_forget()
            try:
                self.beds = int(self.number_beds_entry.get().replace(",", "").replace(".", ""))
            except ValueError:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Number of beds must be an integer")
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
                return
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
                        self.send_sa_progress_frame.columnconfigure(2, weight=1)
                        self.send_sa_progress_bar = ttk.Progressbar(self.send_sa_progress_frame, orient="horizontal",
                                                                    mode="determinate")
                        self.send_sa_progress_var = tk.StringVar()
                        self.send_sa_progress_lbl = ttk.Label(self.send_sa_progress_frame, style="Options.TLabel", wraplength=wrap_length,
                                                              textvariable=self.send_sa_progress_var, foreground="green")
                        self.send_sa_yes_btn = ttk.Button(self.send_sa_progress_frame, style="Back.TButton", text="Yes",
                                                          command=lambda: self.send_statistics("good", True))
                        self.send_sa_no_btn = ttk.Button(self.send_sa_progress_frame, style="Back.TButton", text="No",
                                                         command=lambda: self.send_sa_progress_var.set("Program stopped."))
                        self.send_sa_separator = ttk.Separator(self.send_sa_progress_frame, orient="horizontal")

                        self.send_sa_progress_frame.grid(row=6, column=0, padx=20, sticky=tk.W+tk.E)

                        self.send_sa_progress_bar.grid(row=0, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
                        self.send_sa_progress_lbl.grid(row=1, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
                        self.send_sa_separator.grid(row=3, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
                elif int(self.beds) == 0:
                    self.send_to_sa_btn.configure(state=tk.ACTIVE)
                    self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                    self.sa_options_warning_var.set("Number of beds must be more than zero!")
            except TypeError:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Number of beds must be an integer")
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
            except ValueError:
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Number of beds must be an integer")
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Details incorrect, could not sign in")
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.bundesland_combobox.configure(state="readonly")
            self.sa_password_var.set("")
            self.sa_password_entry.focus()
            self.sa_change_details_btn.grid_forget()
            self.sa_save_login_btn.grid(row=5, column=3, pad=2, sticky=tk.E)
            self.calculate_btn.configure(state=tk.ACTIVE)
            self.calculate_warning_var.set("")
            self.calculate_progress_lbl.grid_forget()
            self.calculate_progress_bar.grid_forget()
            self.sa_change_details_flag = "yes"
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Statistics Amt website timed out and could not be reached,, please try "
                                            "again later.")

    def load_bar(self):
        try:
            message = self.download_queue.get(0)
            if message == "Finished!":
                self.download_lbl_var.set(message)
                self.channel_manager = "MyAllocator"
                self.parent.after(100, self.load_bar)
            elif message == "bookings.csv":
                self.bookings_file = message
            elif message == "timed out":
                self.ma_properties_warn_lbl.grid(row=9, column=1, columnspan=2, sticky=tk.W)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.ma_properties_warn_var.set("MyAllocator website timed out, please try again later")
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
            if message == "sa ok sa save details yes" or message == "sa ok sa save details no":
                self.sa_credential_ok("good")
                self.parent.after(100, self.check_sa_cred_queue)
            elif message[0] == "sa not ok sa save details yes":
                self.sa_credential_ok("bad yes")
            elif message[0] == "sa not ok sa save details no":
                self.sa_credential_ok(["bad no", message[1]])
            elif message[0] == "sa page timeout sa save details yes" or message == "sa page timeout sa save details yes":
                self.sa_credential_ok("failed")
            elif message[0] == "sa address bad sa save details":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("It seems you haven't saved your address on your Statistik Amt profile, please "
                                        "do so before continuing")
            elif message == "sa ok send stats":
                self.send_statistics("good")
            elif message[0] == "sa not ok send stats":
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
            elif message == "wrong csv":
                self.calculate_warning.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Could not calculate the statistics properly, please make sure you have"
                                               " chosen the correct 'csv' file and try again.")
                self.calculate_btn.configure(state=tk.ACTIVE)
            elif isinstance(message, list):
                self.statistics_results = message[0]
            else:
                self.calculate_progress_bar.step(message)
                self.parent.after(25, self.process_calculate_progress_bar)
        except queue.Empty:
            self.parent.after(100, self.process_calculate_progress_bar)

    def process_sa_send_queue(self):
        try:
            message = self.sa_send_queue.get(0)
            if message == "already sent":
                self.send_sa_progress_lbl.configure(foreground='red')
                self.send_sa_progress_var.set("You have already sent statistics for this month, would you like to send "
                                              "them again?")
                self.send_sa_yes_btn.grid(row=2, column=0, pady=2, sticky=tk.W)
                self.send_sa_no_btn.grid(row=2, column=1, padx=2, pady=2, sticky=tk.W)
            elif isinstance(message, int):
                self.send_sa_progress_bar.step(message)
                self.parent.after(10, self.process_sa_send_queue)
            elif isinstance(message, list):
                self.send_sa_progress_var.set("Statistics for {} successfully sent!".format(message[1]))
                import display_results
                display_results.ResultsWindow(self, message[2], message[1])
            elif message == "no date":
                self.send_sa_progress_bar.grid_forget()
                self.send_sa_progress_lbl.configure(foreground='red')
                self.sa_options_frame.grid_forget()
                self.calculate_btn.configure(state=tk.ACTIVE)
                self.send_sa_progress_var.set("Sorry, the Statistics Amt website is not allowing statistics to be "
                                              "submitted for the month you have chosen, please choose a different "
                                              "month and try again.")
            elif message == "timed out":
                self.send_sa_progress_lbl.configure(foreground='red')
                self.send_sa_progress_var.set("Statistics Amt website timed out and could not be reached, please try "
                                              "again later.")
            else:
                self.send_sa_progress_var.set(message)
                self.parent.after(10, self.process_sa_send_queue)
        except queue.Empty:
            self.parent.after(100, self.process_sa_send_queue)


def main():
    root = tk.Tk()
    root.wm_title("Statistik Rechner")
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
