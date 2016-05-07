# -*- coding: utf-8 -*-
import re
import os
import sys
import threading
import queue
from datetime import datetime
import locale
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox
from idlelib.ToolTip import ToolTip
from PIL import Image, ImageTk
import json
import myallocator
import hostelworld
import statistic_amt
import combobox_dicts
import calculate_statistics
from sa_options import *
from selenium import webdriver


"""
ma refers to MyAllocator
hw refers to Hostel World
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
            self.pointer = "hand2"
            os.popen("attrib +h .data_files").close()
            os.popen("attrib +h .icons").close()
            os.popen("attrib +h .images").close()
            os.popen("attrib +h .phantomjs").close()
        else:
            locale.setlocale(locale.LC_TIME, "de_DE.utf-8")
            warning_fs = "-size 10"
            upload_button_font = "-size 16"
            self.field_width = 30
            self.pointer = "pointinghand"

        self.bookings_file = ""
        self.channel_manager = "--Select Channel Manager--"
        self.temp_driver = None

        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.bind("<Configure>", self.update_idletasks())

        self.download_queue = queue.Queue()
        self.ma_cred_queue = queue.Queue()
        self.hw_cred_queue = queue.Queue()
        self.sa_cred_queue = queue.Queue()
        self.get_properties_queue = queue.Queue()
        self.hw_download_queue = queue.Queue()
        self.calculate_statistics_queue = queue.Queue()
        self.sa_send_queue = queue.Queue()

        self.ma_login_details = dict()
        if os.path.isfile(".data_files/.ma_login.json"):
            with open(".data_files/.ma_login.json") as ma_json:
                self.ma_login_details = json.load(ma_json)

        self.hw_login_details = dict()
        if os.path.isfile(".data_files/.hw_login.json"):
            with open(".data_files/.hw_login.json") as hw_json:
                self.hw_login_details = json.load(hw_json)

        self.sa_login_details = dict()
        if os.path.isfile(".data_files/.sa_login.json"):
            with open(".data_files/.sa_login.json") as sa_json:
                self.sa_login_details = json.load(sa_json)

        #  Determines how many SA logins have been used
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

        self.label_title = ttk.Style()
        self.label_title.configure("Title.TLabel", font="-size 14")
        self.warning_lbl_style = ttk.Style()
        self.warning_lbl_style.configure('Warning.TLabel', font=warning_fs, foreground='red')
        self.upload_style_buttons = ttk.Style()
        self.upload_style_buttons.configure("Upload.TButton", font=upload_button_font, padding=(0, 10, 0, 10))

        # Title widgets
        self.title_frame = ttk.Frame(self)
        self.title_frame.columnconfigure(0, weight=1)
        if sys.platform == 'win32':
            title_png = Image.open(".images/title_img.png")
            title_photo = ImageTk.PhotoImage(title_png)
        else:
            title_png = Image.open(".images/mac-title.png")
            title_photo = ImageTk.PhotoImage(title_png)
        self.title = ttk.Label(self.title_frame, image=title_photo)
        self.title.image = title_photo

        #  Upload Style widgets
        self.upload_style_frame = ttk.Frame(self)
        self.upload_style_frame.columnconfigure(0, weight=1)
        self.upload_style_frame.columnconfigure(1, weight=1)
        self.upload_style_frame.columnconfigure(2, weight=1)
        self.upload_style_title = ttk.Label(self.upload_style_frame, text="Upload with...", style="Title.TLabel")
        self.upload_style_separator = ttk.Separator(self.upload_style_frame, orient="horizontal")
        self.upload_myallocator_btn = ttk.Button(self.upload_style_frame,  style="Upload.TButton", text="MyAllocator",
                                                 cursor=self.pointer, command=self.setup_ma)
        self.upload_myallocator_tooltip = ToolTip(self.upload_myallocator_btn, "Provide MyAllocator login details "
                                                                               "to be able to\ndownload all "
                                                                               "bookings automatically.")
        self.upload_hostelworld_btn = ttk.Button(self.upload_style_frame, style="Upload.TButton", text="Hostel World",
                                                 cursor=self.pointer, command=self.setup_hw)
        self.upload_hostelworld_tooltip = ToolTip(self.upload_hostelworld_btn, "Provide Hostel World login details "
                                                                               "to be able to\ndownload bookings "
                                                                               "automatically.")
        self.upload_file_btn = ttk.Button(self.upload_style_frame, style="Upload.TButton", text="From file",
                                          cursor=self.pointer, command=self.upload_bookings)
        self.upload_file_tooltip = ToolTip(self.upload_file_btn, "Upload a 'csv' file of your bookings from your "
                                                                 "computer")
        bullet = "\u2022"
        #  MyAllocator login widgets
        self.ma_username = None
        self.ma_password = None
        self.ma_form_frame = ttk.Frame(self)
        self.ma_form_frame.columnconfigure(1, weight=1)
        self.ma_title_separator = ttk.Separator(self.ma_form_frame, orient="horizontal")
        self.ma_title_lbl = ttk.Label(self.ma_form_frame, style="Title.TLabel", text="MyAllocator login details")
        self.ma_username_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Username: ")
        self.ma_username_var = tk.StringVar()
        self.ma_username_entry = ttk.Entry(self.ma_form_frame, width=self.field_width,
                                           textvariable=self.ma_username_var)
        self.ma_password_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Password: ")
        self.ma_password_var = tk.StringVar()
        self.ma_password_entry = ttk.Entry(self.ma_form_frame, show=bullet, width=self.field_width,
                                           textvariable=self.ma_password_var)
        self.ma_password_entry.bind("<Return>", self.save_ma_login)
        self.ma_warning_var = tk.StringVar()
        self.ma_warning = ttk.Label(self.ma_form_frame, style="Warning.TLabel", textvariable=self.ma_warning_var)
        self.ma_form_separator = ttk.Separator(self.ma_form_frame, orient="horizontal")
        self.ma_save_login_btn = ttk.Button(self.ma_form_frame, text="Save login details",
                                            cursor=self.pointer, command=lambda: self.save_ma_login(None))
        self.ma_save_tooltip = ToolTip(self.ma_save_login_btn, "Save your MyAllocator login details for future use.")
        self.ma_get_properties_btn = ttk.Button(self.ma_form_frame, text="Continue/Fetch Properties",
                                                cursor=self.pointer,
                                                command=lambda: self.check_ma_credential("get properties"))
        self.ma_properties_tooltip = ToolTip(self.ma_get_properties_btn, "Retrieve your properties from your "
                                                                         "MyAllocator account.")
        self.ma_change_details_btn = ttk.Button(self.ma_form_frame, text="Change login details", cursor=self.pointer,
                                                command=self.ma_change_details)
        self.ma_change_details_tooltip = ToolTip(self.ma_change_details_btn, "Change your saved MyAllocator login "
                                                                             "details.")
        self.ma_back_btn = ttk.Button(self.ma_form_frame, text="Back", cursor=self.pointer, command=self.finish)

        #  MyAllocator properties widgets
        self.ma_properties = dict()
        self.ma_properties_lbl = ttk.Label(self.ma_form_frame, text="Property: ")
        self.ma_properties_combobox = ttk.Combobox(self.ma_form_frame, state="readonly")
        self.ma_download_btn = ttk.Button(self.ma_form_frame, text="Download Bookings", cursor=self.pointer,
                                          command=self.ma_download_bookings)
        self.ma_properties_separator = ttk.Separator(self.ma_form_frame, orient="horizontal")
        self.ma_properties_warn_var = tk.StringVar()
        self.ma_properties_warn_lbl = ttk.Label(self.ma_form_frame, style="Warning.TLabel",
                                                textvariable=self.ma_properties_warn_var)
        self.download_bar = ttk.Progressbar(self.ma_form_frame, orient="horizontal", mode="determinate")
        self.download_lbl_var = tk.StringVar()
        self.download_lbl = ttk.Label(self.ma_form_frame, textvariable=self.download_lbl_var)

        #  Upload Bookings widgets
        self.browse_files_frame = ttk.Frame(self)
        self.browse_files_frame.columnconfigure(1, weight=1)
        self.browse_files_title_lbl = ttk.Label(self.browse_files_frame, text="Bookings Upload", style="Title.TLabel")
        self.browse_files_title_separator = ttk.Separator(self.browse_files_frame, orient="horizontal")
        self.browse_files_btn = ttk.Button(self.browse_files_frame, text="Browse...", cursor=self.pointer,
                                           command=self.browse_csv)
        self.browse_files_tooltip = ToolTip(self.browse_files_btn, "Upload a 'csv' file of all your bookings "
                                                                   "(Can be downloaded from the channel manager you"
                                                                   " use.")
        self.browse_files_var = tk.StringVar()
        self.browse_files_lbl = ttk.Entry(self.browse_files_frame, width=self.field_width+5, cursor=self.pointer,
                                          textvariable=self.browse_files_var, state="readonly")
        self.browse_files_lbl.bind("<Button-1>", self.browse_csv)
        self.channel_lbl = ttk.Label(self.browse_files_frame, text="Channel Manager:")
        self.channel_combobox = ttk.Combobox(self.browse_files_frame, state="readonly", width=30,
                                             values=sorted(list(combobox_dicts.channel_managers.keys())))
        self.channel_combobox.bind("<<ComboboxSelected>>", self.channel_selected)
        self.browse_files_separator = ttk.Separator(self.browse_files_frame, orient="horizontal")
        self.browse_back_btn = ttk.Button(self.browse_files_frame, text="Back", cursor=self.pointer,
                                          command=self.finish)

        #  Statistik Amt login widgets
        self.sa_change_details_flag = "new"
        self.sa_property = None
        self.sa_user_id = None
        self.sa_password = None
        self.sa_bundesland = None
        self.sa_form_frame = ttk.Frame(self)
        self.sa_form_frame.columnconfigure(1, weight=1)
        self.sa_title_lbl = ttk.Label(self.sa_form_frame, style="Title.TLabel", text="Statistik Amt login details")
        self.sa_title_separator = ttk.Separator(self.sa_form_frame, orient="horizontal")
        self.sa_user_id_var = tk.StringVar()
        self.sa_user_id_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt ID nr: ")
        self.sa_user_id_entry = ttk.Entry(self.sa_form_frame, textvariable=self.sa_user_id_var, width=self.field_width)
        self.sa_password_var = tk.StringVar()
        self.sa_password_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt Password: ")
        self.sa_password_entry = ttk.Entry(self.sa_form_frame, show=bullet, width=self.field_width,
                                           textvariable=self.sa_password_var)
        self.sa_password_entry.bind("<Return>", self.save_sa_login)
        self.sa_user_id_options = [user_id for user_id in self.sa_login_details.keys() if "User ID" in user_id]
        self.sa_user_id_combobox = ttk.Combobox(self.sa_form_frame, state="readonly", values=self.sa_user_id_options)
        self.sa_user_id_combobox.bind("<<ComboboxSelected>>", self.load_from_combobox)
        self.sa_save_login_btn = ttk.Button(self.sa_form_frame, text="Save login details", cursor=self.pointer,
                                            command=lambda: self.save_sa_login(None))
        self.sa_save_login_tooltip = ToolTip(self.sa_save_login_btn, "Save your Statistik Amt login info for future"
                                                                     " use")
        self.sa_change_details_btn = ttk.Button(self.sa_form_frame, text="Change password", cursor=self.pointer)
        self.sa_change_details_tooltip = ToolTip(self.sa_change_details_btn, "Change your saved Statistik Amt "
                                                                             " password for this User ID.")
        self.sa_add_login_details_btn = ttk.Button(self.sa_form_frame, text="Add login details", cursor=self.pointer)
        self.sa_add_login_details_tooltip = ToolTip(self.sa_add_login_details_btn, "Add a new login User ID and "
                                                                                   "password for the Statistik Amt")
        self.sa_warning_var = tk.StringVar()
        self.sa_warning_lbl = ttk.Label(self.sa_form_frame, textvariable=self.sa_warning_var, style="Warning.TLabel")
        self.sa_bundesland_combobox_lbl = ttk.Label(self.sa_form_frame, text="Bundesland: ")
        self.sa_bundesland_combobox = ttk.Combobox(self.sa_form_frame, state="readonly",
                                                   value=list(combobox_dicts.bundeslaende.keys()))
        self.sa_bundesland_combobox.bind("<Return>", self.save_sa_login)
        self.sa_login_separator = ttk.Separator(self.sa_form_frame, orient="horizontal")

        #  Calculate statistics widgets
        self.statistics_results = None
        self.calculate_frame = ttk.Frame(self)
        self.calculate_frame.columnconfigure(0, weight=1)
        self.calculate_frame.columnconfigure(3, weight=1)
        self.date_lbl = ttk.Label(self.calculate_frame, text="Submission Month: ")
        self.month_combobox = ttk.Combobox(self.calculate_frame, state="readonly",
                                           values=list(combobox_dicts.months.keys()), width=12)
        self.year_combobox = ttk.Combobox(self.calculate_frame, state="readonly",
                                          values=sorted(list(combobox_dicts.years.keys())), width=7)
        self.calculate_btn = ttk.Button(self.calculate_frame, text="Calculate Statistics", cursor=self.pointer,
                                        command=self.calculate_statistics)
        self.calculate_warning_var = tk.StringVar()
        self.calculate_warning = ttk.Label(self.calculate_frame, style="Warning.TLabel",
                                           textvariable=self.calculate_warning_var)
        self.calculate_progress_bar = ttk.Progressbar(self.calculate_frame, orient="horizontal", mode="determinate")
        self.calculate_progress_lbl_var = tk.StringVar()
        self.calculate_progress_lbl = ttk.Label(self.calculate_frame, textvariable=self.calculate_progress_lbl_var)
        self.sa_calculate_separator = ttk.Separator(self.calculate_frame, orient="horizontal")

        # Hostel World widgets
        self.hw_hostel_number = None
        self.hw_username = None
        self.hw_password = None
        self.hw_form_frame = ttk.Frame(self)
        self.hw_form_frame.columnconfigure(2, weight=1)
        self.hw_login_title_lbl = ttk.Label(self.hw_form_frame, text="Hostel World Inbox details",
                                            style="Title.TLabel")
        self.hw_login_separator = ttk.Separator(self.hw_form_frame, orient=tk.HORIZONTAL)
        self.hw_hostel_number_lbl = ttk.Label(self.hw_form_frame, text="Hostel Number: ")
        self.hw_hostel_number_var = tk.StringVar()
        self.hw_hostel_number_entry = ttk.Entry(self.hw_form_frame, textvariable=self.hw_hostel_number_var,
                                                width=6)
        self.hw_username_lbl = ttk.Label(self.hw_form_frame, text="Username: ")
        self.hw_username_var = tk.StringVar()
        self.hw_username_entry = ttk.Entry(self.hw_form_frame, textvariable=self.hw_username_var,
                                           width=self.field_width)
        self.hw_password_lbl = ttk.Label(self.hw_form_frame, text="Password: ")
        self.hw_password_var = tk.StringVar()
        self.hw_password_entry = ttk.Entry(self.hw_form_frame, show=bullet, textvariable=self.hw_password_var,
                                           width=self.field_width)
        self.hw_password_entry.bind("<Return>", self.save_hw_login)
        self.hw_save_details_btn = ttk.Button(self.hw_form_frame, text="Save login details", cursor=self.pointer,
                                              command=lambda: self.save_hw_login(None))
        self.hw_save_details_tooltip = ToolTip(self.hw_save_details_btn, "Save your Hostel World login details for "
                                                                         "future use.")
        self.hw_change_details_btn = ttk.Button(self.hw_form_frame, text="Change login details", cursor=self.pointer,
                                                command=self.hw_change_details)
        self.hw_change_details_tooltip = ToolTip(self.hw_change_details_btn, "Change your saved Hostel World login"
                                                                             " details.")
        self.hw_back_btn = ttk.Button(self.hw_form_frame, text="Back", cursor=self.pointer, command=self.finish)
        self.hw_warning_var = tk.StringVar()
        self.hw_warning_lbl = ttk.Label(self.hw_form_frame, style="Warning.TLabel", textvariable=self.hw_warning_var)
        self.hw_form_separator = ttk.Separator(self.hw_form_frame, orient=tk.HORIZONTAL)

        self.hw_download_bar = ttk.Progressbar(self.calculate_frame, orient="horizontal", mode="determinate")
        self.hw_download_lbl_var = tk.StringVar()
        self.hw_download_lbl = ttk.Label(self.calculate_frame, textvariable=self.hw_download_lbl_var)

        #  Statistics Amt options Widgets
        self.beds = 0
        self.sa_options_frame = ttk.Frame(self)
        self.sa_options_frame.columnconfigure(4, weight=1)
        self.number_beds_var = tk.StringVar()
        self.number_beds_lbl = ttk.Label(self.sa_options_frame, text=beds, justify=tk.RIGHT)
        self.number_beds_entry = ttk.Entry(self.sa_options_frame, width=5, textvariable=self.number_beds_var)
        self.closed_lbl = ttk.Label(self.sa_options_frame, text=closed, justify=tk.RIGHT)
        self.closed_lbl2 = ttk.Label(self.sa_options_frame, font="-size 8", text=".dieses Berichtsmonats")
        self.closed_combo = ttk.Combobox(self.sa_options_frame, state="readonly",
                                         values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.reopen_lbl = ttk.Label(self.sa_options_frame, text=opened, justify=tk.RIGHT)
        self.reopen_frame = ttk.Frame(self.sa_options_frame)
        self.reopen_combo_d = ttk.Combobox(self.sa_options_frame, state="readonly",
                                           values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.reopen_combo_m = ttk.Combobox(self.sa_options_frame, state="readonly",
                                           values=list(combobox_dicts.month_num.keys()), width=4)
        self.reopen_combo_y = ttk.Combobox(self.sa_options_frame, state="readonly",
                                           values=sorted(list(combobox_dicts.options_years.keys())), width=5)
        self.forced_closed_lbl = ttk.Label(self.sa_options_frame, text=forced_close, justify=tk.RIGHT)
        self.forced_closed_combo = ttk.Combobox(self.sa_options_frame, state="readonly",
                                                values=list(combobox_dicts.days_in_month.keys()), width=4)
        self.forced_closed_lbl2 = ttk.Label(self.sa_options_frame, font="-size 8", text=".dieses Berichtsmonats")
        self.sa_options_warning_var = tk.StringVar()
        self.sa_options_warning_lbl = ttk.Label(self.sa_options_frame, style="Warning.TLabel",
                                                textvariable=self.sa_options_warning_var)
        self.send_to_sa_btn = ttk.Button(self.sa_options_frame, style="Upload.TButton", text="SEND",
                                         cursor=self.pointer,
                                         command=lambda: self.check_sa_options_form(self.sa_property))
        self.send_to_sa_tooltip = ToolTip(self.send_to_sa_btn, "Send your calculated statistics for the chosen "
                                                               "month to the Statistik Amt.")
        self.options_separator = ttk.Separator(self.sa_options_frame, orient="horizontal")

        #  Send Statistics widgets
        self.send_sa_progress_frame = ttk.Frame(self)
        self.send_sa_progress_frame.columnconfigure(2, weight=1)
        self.send_sa_progress_bar = ttk.Progressbar(self.send_sa_progress_frame, orient="horizontal",
                                                    mode="determinate")
        self.send_sa_progress_var = tk.StringVar()
        self.send_sa_progress_lbl = ttk.Label(self.send_sa_progress_frame, style="Options.TLabel",
                                              textvariable=self.send_sa_progress_var, foreground="green")
        self.send_sa_yes_btn = ttk.Button(self.send_sa_progress_frame, text="Yes", cursor=self.pointer,
                                          command=lambda: self.send_statistics("good", already_sent_continue=True))
        self.send_sa_no_btn = ttk.Button(self.send_sa_progress_frame, text="No", cursor=self.pointer,
                                         command=self.finish)
        self.send_sa_finish_btn = ttk.Button(self.send_sa_progress_frame, text="Finish", cursor=self.pointer,
                                             command=self.finish)
        self.send_sa_separator = ttk.Separator(self.send_sa_progress_frame, orient="horizontal")

        # Pack title widgets
        self.title_frame.grid(row=0, column=0)
        self.title.grid(row=0, column=0, sticky=tk.W+tk.E, padx=20)

        self.upload_style()

    def upload_style(self):
        #  Pack Upload Style widgets
        self.upload_style_frame.grid(row=1, column=0, padx=20, sticky=tk.W+tk.E)
        self.upload_style_title.grid(row=0, column=0, pady=2, sticky=tk.W)
        self.upload_style_separator.grid(row=1, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
        self.upload_myallocator_btn.grid(row=2, column=0, pady=10)
        self.upload_hostelworld_btn.grid(row=2, column=1, pady=10)
        self.upload_file_btn.grid(row=2, column=2, pady=10)
        if self.sa_logins_used > 3:
            tk.messagebox.showinfo("Too Many Logins Saved", "Sorry, you have saved too many login details for the "
                                                            "Statistik Amt (maximum is 3), please delete some or "
                                                            "contact grant.williams2986@gmail.com if you need to be "
                                                            "able to save more.", parent=self.parent)
            self.upload_myallocator_btn.configure(state=tk.DISABLED)
            self.upload_hostelworld_btn.configure(state=tk.DISABLED)
            self.upload_file_btn.configure(state=tk.DISABLED)
            return

        #  opens a PhantomJS driver so the user can allow the permissions earlier on, before saving user/pass details
        self.temp_driver = webdriver.PhantomJS(executable_path=".phantomjs/bin/phantomjs")
        self.temp_driver.quit()
        self.update_idletasks()

    def setup_ma(self):
        self.upload_style_frame.grid_forget()
        #  pack MyAllocator widgets
        self.ma_form_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=20)
        self.ma_title_lbl.grid(row=0, column=0, columnspan=3, pady=2, sticky=tk.W)
        self.ma_title_separator.grid(row=1, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.ma_username_lbl.grid(row=2, column=0, sticky=tk.E, padx=(0, 20), pady=2)
        self.ma_username_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.ma_password_lbl.grid(row=3, column=0, sticky=tk.E, padx=(0, 20), pady=2)
        self.ma_password_entry.grid(row=3, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.ma_warning.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=2)
        self.ma_form_separator.grid(row=6, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        #  if Login details already exist, fill the form
        if self.ma_login_details.get("ma_password", "") != "":
            self.ma_get_properties_btn.grid(row=5, column=1, pady=2, sticky=tk.E)
            self.ma_change_details_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_back_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
            self.ma_username_var.set(self.ma_login_details["ma_username"])
            self.ma_password_var.set(self.ma_login_details["ma_password"])
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
        else:
            self.ma_username_entry.focus()
            self.ma_save_login_btn.grid(row=5, column=1, pady=2, sticky=tk.E)
            self.ma_back_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
        self.update_idletasks()
        self.ma_warning.configure(wraplength=self.parent.winfo_width()*.6)

    def ma_change_details(self):
        self.ma_warning_var.set('')
        self.ma_username_entry.configure(state=tk.ACTIVE)
        self.ma_password_entry.configure(state=tk.ACTIVE)
        self.ma_password_var.set("")
        self.ma_password_entry.focus()
        self.ma_change_details_btn.grid_forget()
        self.ma_get_properties_btn.grid_forget()
        self.ma_save_login_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
        self.update_idletasks()

    def check_ma_credential(self, call_origin):
        self.ma_get_properties_btn.configure(state=tk.DISABLED)
        self.ma_change_details_btn.configure(state=tk.DISABLED)
        self.ma_back_btn.configure(state=tk.DISABLED)
        self.ma_save_login_btn.configure(state=tk.DISABLED)
        self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
        self.ma_warning_var.set("Trying to log into MyAllocator...")
        ma_cred_thread = threading.Thread(
            target=myallocator.check_cred, args=[self.ma_login_details, self.ma_cred_queue, call_origin])
        ma_cred_thread.daemon = True
        ma_cred_thread.start()
        self.update_idletasks()
        self.parent.after(100, self.check_ma_cred_queue)

    def save_ma_login(self, event):
        self.ma_username = self.ma_username_entry.get()
        self.ma_password = self.ma_password_entry.get()

        if self.ma_username != '' and self.ma_password != '':
            self.ma_login_details["ma_username"] = self.ma_username
            self.ma_login_details["ma_password"] = self.ma_password
            self.check_ma_credential("ma save details")
        elif self.ma_username == '' or self.ma_password == '':
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("One or more fields are empty!")
        self.update_idletasks()

    def ma_credential_ok(self, status):
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Login successful!")
            self.ma_save_login_btn.grid_forget()
            self.ma_back_btn.grid_forget()
            self.ma_change_details_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_get_properties_btn.grid(row=5, column=1, padx=10, pady=2, sticky=tk.E)
            self.ma_get_properties_btn.configure(state=tk.ACTIVE)
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
            with open(".data_files/.ma_login.json", "w", encoding='utf-8') as outfile:
                json.dump(self.ma_login_details, indent=4, sort_keys=True, fp=outfile)
            self.update_idletasks()
            self.get_properties("good")
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_login_details["ma_password"] = ""
            self.ma_save_login_btn.configure(state=tk.ACTIVE)
            self.ma_back_btn.configure(state=tk.ACTIVE)
            self.update_idletasks()

    def get_properties(self, status):
        self.ma_get_properties_btn.configure(state=tk.DISABLED)
        if status == "good":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
            self.ma_warning_var.set("Fetching property list from MyAllocator")
            self.ma_get_properties_btn.grid_forget()
            self.ma_change_details_btn.grid_forget()
            self.ma_back_btn.grid_forget()
            self.ma_username_entry.configure(state=tk.DISABLED)
            self.ma_password_entry.configure(state=tk.DISABLED)
            property_process = threading.Thread(target=myallocator.get_properties, args=[self.ma_login_details,
                                                                                         self.get_properties_queue])
            property_process.daemon = True
            property_process.start()
            self.update_idletasks()
            self.parent.after(100, self.check_get_properties_queue())
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_username_entry.configure(state=tk.ACTIVE)
            self.ma_password_entry.configure(state=tk.ACTIVE)
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_change_details_btn.grid_forget()
            self.ma_get_properties_btn.grid_forget()
            self.ma_save_login_btn.grid(row=5, column=2, pady=2, sticky=tk.E)
            self.ma_save_login_btn.configure(state=tk.ACTIVE)
            self.ma_back_btn.configure(state=tk.ACTIVE)
            self.update_idletasks()

    def load_properties(self):
        self.ma_warning_var.set("")
        with open(".data_files/properties.json") as properties_file:
            self.ma_properties = json.load(properties_file)
            self.ma_properties_combobox.configure(values=sorted(list(self.ma_properties.keys())))
            self.ma_properties_lbl.grid(row=7, column=0, padx=(0, 20), pady=2, sticky=tk.E)
            self.ma_properties_combobox.grid(row=7, column=1, padx=(0, 20), pady=2, sticky=tk.W)
            self.ma_download_btn.grid(row=7, column=3, pady=2, sticky=tk.E)
            self.ma_properties_combobox.current(0)
            self.ma_properties_separator.grid(row=10, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
            self.update_idletasks()

    def ma_download_bookings(self):
        self.ma_warning_var.set("")
        ma_property = self.ma_properties[self.ma_properties_combobox.get()][0]
        if ma_property != "" and self.download_lbl_var.get() in ["", "Finished!"]:
            self.ma_download_btn.configure(state=tk.DISABLED)
            self.ma_properties_combobox.configure(state=tk.DISABLED)
            self.sa_form_frame.grid_forget()
            self.calculate_frame.grid_forget()
            download_process = threading.Thread(target=myallocator.download_bookings_csv,
                                                args=(self.ma_login_details, ma_property, self.download_queue))
            download_process.daemon = True
            download_process.start()

            self.download_bar.grid(row=8, column=1, pady=2, sticky=tk.W+tk.E)
            self.download_lbl.grid(row=8, column=3, pady=2, sticky=tk.E)
            self.download_lbl_var.set("Downloading...")
            self.update_idletasks()
            self.parent.after(100, self.load_bar)
            self.setup_sa("myallocator")
        else:
            self.ma_properties_warn_lbl.grid(row=8, column=1, columnspan=2, sticky=tk.W)
            self.ma_properties_warn_lbl.configure(wraplength=self.winfo_width() * 0.35)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.ma_properties_warn_var.set("Please choose a property first.")
        self.update_idletasks()

    def upload_bookings(self):
        self.upload_style_frame.grid_forget()
        #  pack Upload Bookings widgets
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
        self.update_idletasks()

    def browse_csv(self, event=None):
        self.sa_form_frame.grid_forget()  # in case changing file names
        self.calculate_frame.grid_forget()  # in case changing file names
        self.bookings_file = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
        self.browse_files_var.set(self.bookings_file)
        if self.channel_combobox.get() != "--Select Channel Manager--" and self.browse_files_var.get() != "":
            self.setup_sa("file upload")

    def channel_selected(self, event):
        self.sa_form_frame.grid_forget()  # in case changing combobox items
        self.calculate_frame.grid_forget()  # in case changing combobox items
        self.channel_manager = self.channel_combobox.get()
        if self.browse_files_lbl.get() != "" and self.channel_combobox.get() != "--Select Channel Manager--":
            self.setup_sa("file upload")

    def setup_hw(self):
        self.upload_style_frame.grid_forget()
        # pack Hostel World widgets
        self.hw_form_frame.grid(row=1, column=0, padx=20, sticky=tk.W+tk.E)
        self.hw_login_title_lbl.grid(row=0, column=0, pady=2, columnspan=3, sticky=tk.W)
        self.hw_login_separator.grid(row=1, column=0, pady=2, columnspan=4, sticky=tk.W+tk.E)
        self.hw_hostel_number_lbl.grid(row=2, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.hw_hostel_number_entry.grid(row=2, column=1, pady=2, columnspan=2, sticky=tk.W)
        self.hw_username_lbl.grid(row=3, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.hw_username_entry.grid(row=3, column=1, pady=2, columnspan=2, sticky=tk.W)
        self.hw_password_lbl.grid(row=4, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.hw_password_entry.grid(row=4, column=1, columnspan=2, pady=2, sticky=tk.W)
        self.hw_warning_lbl.grid(row=5, column=1, columnspan=2, pady=2, sticky=tk.W+tk.E)
        self.hw_form_separator.grid(row=7, column=0, columnspan=4, sticky=tk.W+tk.E)
        if self.hw_login_details.get("hostel number", "") != "":
            self.hw_hostel_number_var.set(self.hw_login_details["hostel number"])
            self.hw_username_var.set(self.hw_login_details["username"])
            self.hw_password_var.set(self.hw_login_details["password"])
            self.hw_hostel_number_entry.configure(state=tk.DISABLED)
            self.hw_username_entry.configure(state=tk.DISABLED)
            self.hw_password_entry.configure(state=tk.DISABLED)
            self.hw_change_details_btn.grid(row=6, column=1, pady=2, sticky=tk.W)
            self.hw_back_btn.grid(row=6, column=2, pady=2, sticky=tk.W)
            self.setup_sa("hostelworld")
        else:
            self.hw_hostel_number_entry.focus()
            self.hw_save_details_btn.grid(row=6, column=1, pady=2, sticky=tk.W)
            self.hw_back_btn.grid(row=6, column=2, pady=2, sticky=tk.W)
        self.channel_manager = "Hostel World"
        self.bookings_file = "hw_bookings.csv"
        self.update_idletasks()
        self.hw_warning_lbl.configure(wraplength=self.parent.winfo_width()*0.7)

    def hw_change_details(self):
        self.sa_form_frame.grid_forget()  # in case already loaded when choosing to change details
        self.calculate_frame.grid_forget()  # in case already loaded when choosing to change details
        self.hw_hostel_number_entry.configure(state=tk.ACTIVE)
        self.hw_username_entry.configure(state=tk.ACTIVE)
        self.hw_password_entry.configure(state=tk.ACTIVE)
        self.hw_username_var.set("")
        self.hw_password_var.set("")
        self.hw_change_details_btn.grid_forget()
        self.hw_save_details_btn.grid(row=6, column=1, pady=2, sticky=tk.W)
        self.hw_save_details_btn.configure(state=tk.ACTIVE)
        self.hw_back_btn.configure(state=tk.ACTIVE)
        self.hw_username_entry.focus()
        self.update_idletasks()

    def check_hw_credential(self, call_origin):
        self.hw_save_details_btn.configure(state=tk.DISABLED)
        self.hw_back_btn.configure(state=tk.DISABLED)
        self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
        if call_origin == "hw save details":
            self.hw_warning_var.set("Trying to log into Hostel World Inbox...")
        else:
            self.calculate_warning_var.set("Trying to log into Hostel World Inbox...")
        hw_cred_thread = threading.Thread(
            target=hostelworld.check_cred, args=[self.hw_login_details, self.hw_cred_queue, call_origin])
        hw_cred_thread.daemon = True
        hw_cred_thread.start()
        self.update_idletasks()
        self.parent.after(100, self.check_hw_cred_queue)

    def save_hw_login(self, event):
        self.calculate_warning_var.set("")
        self.hw_hostel_number = self.hw_hostel_number_entry.get()
        self.hw_username = self.hw_username_entry.get()
        self.hw_password = self.hw_password_entry.get()

        if self.hw_hostel_number != '' and self.hw_username != '' and self.hw_password != '':
            self.hw_login_details["hostel number"] = self.hw_hostel_number
            self.hw_login_details["username"] = self.hw_username
            self.hw_login_details["password"] = self.hw_password
            self.check_hw_credential("hw save details")
        else:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.hw_warning_var.set("One or more fields are empty!")

    def hw_credential_ok(self, status):
        if "good" in status:
            self.warning_lbl_style.configure("Warning.TLabel", foreground='green')
            if "expire" in status:
                days = re.findall(r'\d+', status)
                self.hw_warning_var.set("Login successful! (note: your Hostel World password will expire in {} "
                                        "days)".format(days[0]))
            else:
                self.hw_warning_var.set("Login successful!")
            self.hw_save_details_btn.grid_forget()
            self.hw_change_details_btn.grid(row=6, column=1, pady=2, sticky=tk.W)
            self.hw_back_btn.configure(state=tk.ACTIVE)
            self.hw_hostel_number_entry.configure(state=tk.DISABLED)
            self.hw_username_entry.configure(state=tk.DISABLED)
            self.hw_password_entry.configure(state=tk.DISABLED)
            with open(".data_files/.hw_login.json", 'w', encoding='utf-8') as outfile:
                json.dump(self.hw_login_details, indent=4, sort_keys=True, fp=outfile)
                self.update_idletasks()
                self.setup_sa("hostelworld")
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.hw_warning_var.set("Details incorrect, could not sign in.")
            self.hw_hostel_number_entry.configure(state=tk.ACTIVE)
            self.hw_username_entry.configure(state=tk.ACTIVE)
            self.hw_password_entry.configure(state=tk.ACTIVE)
            self.hw_save_details_btn.configure(state=tk.ACTIVE)
            self.hw_back_btn.configure(state=tk.ACTIVE)
            self.hw_hostel_number_var.set("")
            self.hw_username_var.set("")
            self.hw_password_var.set("")
            self.hw_hostel_number_entry.focus()
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.hw_warning_var.set("Hostel World site timed out, please try again later.")
        self.update_idletasks()

    def hw_get_bookings(self, status):
        if "good" in status:
            if "pass expire" in status:
                tk.messagebox.showinfo("Password Expire", "Your Hostel World password will expire in {} days, please "
                                                          "log into your Hostel World Inbox to save a new "
                                                          "one.".format(re.findall(r'\d+', status)[0]),
                                       parent=self.parent)
            month_chosen = self.month_combobox.get()
            year_chosen = self.year_combobox.get()
            date_obj = datetime.strptime("{}-{}".format(year_chosen, month_chosen), "%Y-%B")

            hw_get_bookings_thread = threading.Thread(target=hostelworld.get_bookings,
                                                      args=[self.hw_login_details, date_obj, self.hw_download_queue])
            hw_get_bookings_thread.daemon = True
            hw_get_bookings_thread.start()

            self.hw_download_bar.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2)
            self.hw_download_lbl.grid(row=1, column=3, sticky=tk.E, padx=20)
            self.hw_download_lbl_var.set("Downloading Bookings...")
            self.update_idletasks()
            self.parent.after(100, self.check_hw_download_queue())
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.hw_warning_var.set("Details incorrect, could not sign in.")
            self.calculate_warning_var.set("Details incorrect, could not sign in.")
            self.hw_hostel_number_entry.configure(state=tk.ACTIVE)
            self.hw_username_entry.configure(state=tk.ACTIVE)
            self.hw_password_entry.configure(state=tk.ACTIVE)
            self.hw_save_details_btn.configure(state=tk.ACTIVE)
            self.hw_back_btn.configure(state=tk.ACTIVE)
            self.hw_hostel_number_var.set("")
            self.hw_username_var.set("")
            self.hw_password_var.set("")
            self.hw_hostel_number_entry.focus()
            self.hw_change_details_btn.grid_forget()
            self.hw_save_details_btn.grid(row=6, column=1, pady=2, sticky=tk.W)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.sa_bundesland_combobox.configure(state=tk.ACTIVE)
            self.sa_add_login_details_btn.configure(state=tk.ACTIVE)
            self.sa_change_details_btn.configure(state=tk.ACTIVE)
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Hostel World site timed out, please try again later.")
        self.update_idletasks()

    #  'Upload Bookings' can mean Upload bookings or from Hostel World
    def setup_sa(self, origin, sa_property="Upload Bookings"):
        if origin == "myallocator":
            self.sa_property = self.ma_properties_combobox.get()
        else:
            self.sa_property = sa_property

        #  pack Statistik Amt widgets
        self.sa_form_frame.grid(row=3, column=0, padx=20, sticky=tk.W+tk.E)
        self.sa_title_lbl.grid(row=0, column=0, columnspan=4, pady=2, sticky=tk.W)
        self.sa_title_separator.grid(row=1, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.sa_user_id_lbl.grid(row=2, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        if self.sa_property == "Upload Bookings":
            #  if no details are save yet, provide normal entry widget for saving
            if len(list(user_id for user_id in self.sa_login_details.keys() if "User ID" in user_id)) == 0:
                self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
                self.sa_user_id_entry.focus()
                self.sa_save_login_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
            #  otherwise provide a combobox with already saved details
            else:
                self.sa_user_id_combobox.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
                self.sa_add_login_details_btn.grid(row=5, column=2, sticky=tk.E, pady=2)
                origin = "file upload"
        else:
            self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
            origin = "myallocator"
        self.sa_password_lbl.grid(row=3, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.sa_password_entry.grid(row=3, column=1, columnspan=3, pady=2, sticky=tk.W+tk.E)
        self.sa_bundesland_combobox_lbl.grid(row=4, column=0, padx=(0, 20), pady=2, sticky=tk.E)
        self.sa_bundesland_combobox.grid(row=4, column=1, columnspan=3, pady=2, sticky=tk.W)
        self.sa_warning_lbl.grid(row=5, column=1, pady=2, sticky=tk.W)
        self.sa_bundesland_combobox.current(0)
        #  if no details are saved yet, just provide a Save button
        if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
            if self.sa_property != "Upload Bookings":
                self.sa_save_login_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
        #  otherwise fill in the form for them with the details they've save before
        else:
            self.sa_user_id_var.set(self.sa_login_details[self.sa_property]["sa_user_id"])
            self.sa_password_var.set(self.sa_login_details[self.sa_property]["sa_password"])
            self.sa_bundesland_combobox.current(
                combobox_dicts.bundeslaende[self.sa_login_details[self.sa_property]["bundesland"]][1])
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.sa_bundesland_combobox.configure(state=tk.DISABLED)
            self.sa_change_details_btn.grid(row=5, column=3, pady=2, sticky=tk.E)

        self.sa_login_separator.grid(row=6, column=0, columnspan=4, pady=2, sticky=tk.W+tk.E)
        self.calculate_frame.grid(row=4, column=0, sticky=tk.W+tk.E)
        self.date_lbl.grid(row=0, column=0, padx=20, pady=2, sticky=tk.E)
        self.month_combobox.grid(row=0, column=1, padx=(0, 5), pady=2, sticky=tk.W)
        self.month_combobox.current(0)
        self.year_combobox.grid(row=0, column=2, padx=(0, 10), pady=2, sticky=tk.E)
        self.year_combobox.current(0)
        self.calculate_btn.grid(row=0, column=3, padx=20, pady=2, sticky=tk.E)
        self.calculate_warning.grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=2)
        self.sa_calculate_separator.grid(row=3, column=0, columnspan=4, padx=20, pady=2, sticky=tk.W+tk.E)
        self.sa_add_login_details_btn.configure(command=lambda: self.change_sa_login(origin, "", "new"))
        self.sa_change_details_btn.configure(command=lambda: self.change_sa_login(origin, self.sa_property))
        self.update_idletasks()
        self.sa_warning_lbl.configure(wraplength=self.parent.winfo_width() / 4)
        self.calculate_warning.configure(wraplength=self.parent.winfo_width()*0.3)

    def load_from_combobox(self, event):
        self.sa_password_var.set(self.sa_login_details[self.sa_user_id_combobox.get()]["sa_password"])
        self.sa_bundesland_combobox.current(
            combobox_dicts.bundeslaende[self.sa_login_details[self.sa_user_id_combobox.get()]["bundesland"]][1])
        self.sa_property = self.sa_user_id_combobox.get()
        self.sa_add_login_details_btn.grid(row=5, column=2, sticky=tk.E, pady=2)
        self.sa_change_details_btn.grid(row=5, column=3, sticky=tk.E, pady=2)
        self.sa_save_login_btn.grid_forget()
        self.sa_password_entry.configure(state=tk.DISABLED)
        self.sa_bundesland_combobox.configure(state=tk.DISABLED)
        self.update_idletasks()

    def check_sa_credential(self, call_origin, ma_property):
        time_now = datetime.now().time()
        eleven = datetime.strptime("22:55", "%H:%M").time()
        twelve_thirty = datetime.strptime("00:35", "%H:%M").time()
        if eleven <= time_now <= twelve_thirty:
            if call_origin == "sa save details update" or call_origin == "sa save details new":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_warning_var.set("Statistics Amt website is not available between 23:00 - 00:30")
            elif call_origin == "send stats":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Statistics Amt website is not available between 23:00 - 00:30")
        else:
            if call_origin == "sa save details update" or call_origin == "sa save details new":
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_warning_var.set("Signing into Statistics Amt site...")
            elif call_origin == "send stats":
                self.send_to_sa_btn.configure(state=tk.DISABLED)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='green')
                self.sa_options_warning_var.set("Signing into Statistics Amt site...")
            sa_cred_thread = threading.Thread(
                target=statistic_amt.check_cred, args=[
                    self.sa_login_details, self.sa_cred_queue, call_origin, ma_property])
            sa_cred_thread.daemon = True
            sa_cred_thread.start()
            self.parent.after(100, self.check_sa_cred_queue)

    def save_sa_login(self, event):
        self.sa_add_login_details_btn.grid_forget()
        if self.sa_user_id_entry.get() != "":
            self.sa_user_id = self.sa_user_id_entry.get()
        else:
            self.sa_user_id = self.sa_user_id_combobox.get().replace("User ID ", "")
        self.sa_password = self.sa_password_entry.get()
        self.sa_bundesland = combobox_dicts.bundeslaende[self.sa_bundesland_combobox.get()][0]
        self.calculate_warning_var.set("")

        if self.sa_user_id != "" and self.sa_password != "":
            if self.sa_bundesland != "":
                if self.sa_property == "Upload Bookings":
                    self.sa_property = "User ID {}".format(self.sa_user_id)
                    if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
                        if self.sa_logins_used < 3:
                            self.sa_login_details[self.sa_property] = {}
                            self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                            self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                            self.sa_login_details[self.sa_property]["bundesland"] = self.sa_bundesland
                            self.sa_login_details[self.sa_property]["beds"] = 0
                        else:
                            tk.messagebox.showinfo("Maximum Logins Used", "Sorry, you have already saved "
                                                                          "the maximum amount of logins (3).  "
                                                                          "If you need to add more, please contact "
                                                                          "grant.williams2986@gmail.com",
                                                   parent=self.parent)
                            return
                    else:
                        self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                        self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                        self.sa_login_details[self.sa_property]["bundesland"] = self.sa_bundesland
                        self.sa_login_details[self.sa_property]["beds"] = 0
                elif self.sa_property != "Upload Bookings":
                    #  create new dict entry if does not exist yet
                    if self.sa_login_details.get(self.sa_property, {}).get("sa_user_id", "") == "":
                        if self.sa_logins_used < 3:
                            self.sa_login_details[self.sa_property] = {}
                            self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                            self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                            self.sa_login_details[self.sa_property]["bundesland"] = self.sa_bundesland
                            self.sa_login_details[self.sa_property]["beds"] = 0
                        else:
                            tk.messagebox.showinfo("Maximum Logins Used", "Sorry, you have already saved "
                                                                          "the maximum amount of logins (3).  "
                                                                          "If you need to add more, please contact "
                                                                          "grant.williams2986@gmail.com",
                                                   parent=self.parent)
                            return
                    # otherwise just update the dict entry
                    else:
                        self.sa_login_details[self.sa_property]["sa_user_id"] = self.sa_user_id
                        self.sa_login_details[self.sa_property]["sa_password"] = self.sa_password
                        self.sa_login_details[self.sa_property]["bundesland"] = self.sa_bundesland
                        self.sa_login_details[self.sa_property]["beds"] = 0
                self.check_sa_credential("sa save details {}".format(self.sa_change_details_flag), self.sa_property)
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
            self.sa_change_details_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
            self.sa_change_details_btn.configure(state=tk.ACTIVE)
            self.sa_save_login_btn.grid_forget()
            self.sa_user_id_entry.configure(state=tk.DISABLED)
            self.sa_password_entry.configure(state=tk.DISABLED)
            self.sa_bundesland_combobox.configure(state=tk.DISABLED)
            with open(".data_files/.sa_login.json", 'w', encoding="utf-8") as outfile:
                    json.dump(self.sa_login_details, indent=4, sort_keys=True, fp=outfile)
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Statistics Amt website timed out, please try again later")
        elif status[0] == "bad new":
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.sa_bundesland_combobox.configure(state="readonly")
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Details incorrect, could not sign in")
            self.sa_user_id_var.set("")
            self.sa_user_id_entry.focus()
            self.sa_password_var.set("")
            self.sa_bundesland_combobox.current(0)
            del self.sa_login_details[status[1]]
        elif status == "bad update":
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.sa_bundesland_combobox.configure(state="readonly")
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_warning_var.set("Details incorrect, could not sign in")
            self.sa_password_var.set("")
            self.sa_password_entry.focus()

    def change_sa_login(self, origin, sa_property, flag="update"):
        self.sa_change_details_flag = flag
        if origin == "file upload" and flag == "update":
            self.sa_user_id_options = [user_id for user_id in self.sa_login_details.keys() if "User ID" in user_id]
            self.sa_user_id_combobox.configure(values=self.sa_user_id_options)
            self.sa_user_id_combobox.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
            self.sa_user_id_combobox.current(self.sa_user_id_options.index(sa_property))
        self.sa_user_id_entry.configure(state=tk.ACTIVE)
        self.sa_password_var.set("")
        self.sa_password_entry.configure(state=tk.ACTIVE)
        self.sa_password_entry.focus()
        self.sa_bundesland_combobox.configure(state="readonly")
        self.sa_change_details_btn.grid_forget()
        self.sa_save_login_btn.grid(row=5, column=3, sticky=tk.E, pady=2)
        if flag == "new":
            self.sa_property = ""
            self.sa_user_id_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
            self.sa_user_id_combobox.grid_forget()
            self.sa_add_login_details_btn.grid_forget()
            self.sa_user_id_entry.focus()

    def calculate_statistics(self, hw_bookings_downloaded=False):
        self.send_sa_progress_frame.grid_forget()  # in case coming from SEND to SA error
        self.sa_change_details_btn.configure(state=tk.DISABLED)
        self.sa_add_login_details_btn.configure(state=tk.DISABLED)
        self.calculate_warning_var.set("")
        self.browse_back_btn.configure(state=tk.DISABLED)
        self.sa_warning_var.set("")
        self.statistics_results = None  # resets results if doing multiple calculations
        today_date = datetime.strptime(str(datetime.now())[:7], "%Y-%m")
        month_chosen = combobox_dicts.months[self.month_combobox.get()]
        year_chosen = self.year_combobox.get()

        try:
            chosen_date_obj = datetime.strptime("{}-{}".format(year_chosen, month_chosen), "%Y-%m")
        except ValueError:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please choose a date first.")
            return

        try:
            chosen_date_obj < today_date
        except TypeError:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please choose a date first.")
            return

        save_button_visible = self.sa_save_login_btn.winfo_ismapped()
        if not save_button_visible:
            if chosen_date_obj < today_date:
                if self.channel_manager == "Hostel World":
                    self.hw_warning_var.set("")
                    if not hw_bookings_downloaded:
                        self.hw_change_details_btn.configure(state=tk.DISABLED)
                        self.hw_back_btn.configure(state=tk.DISABLED)
                        self.calculate_btn.configure(state=tk.DISABLED)
                        hw_calculate_thread = threading.Thread(target=self.check_hw_credential,
                                                               args=["calculate stats"])
                        hw_calculate_thread.daemon = True
                        hw_calculate_thread.start()
                        return
                if os.path.isfile(self.bookings_file):
                    if self.channel_manager != "--Select Channel Manager--":
                        self.calculate_btn.configure(state=tk.DISABLED)
                        calculate_thread = threading.Thread(target=calculate_statistics.calculate,
                                                            args=[month_chosen, year_chosen, self.bookings_file,
                                                                  self.calculate_statistics_queue,
                                                                  self.channel_manager])
                        calculate_thread.daemon = True
                        calculate_thread.start()
                        self.calculate_progress_bar.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=2)
                        self.calculate_progress_lbl.grid(row=1, column=3, sticky=tk.E, padx=20)
                        self.calculate_progress_lbl_var.set("Calculating...")
                        self.parent.after(100, self.process_calculate_progress_bar)
                    else:
                        self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                        self.calculate_warning_var.set("Please choose your channel manager first.")
                else:
                    self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
                    self.calculate_warning.configure(wraplength=self.parent.winfo_width()*0.3)
                    self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                    self.calculate_warning_var.set("Wait for bookings to finish downloading.")
            else:
                self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.calculate_warning.configure(wraplength=self.parent.winfo_width()*0.3)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Please choose a date in the past.")
        else:
            self.calculate_warning.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
            self.calculate_warning.configure(wraplength=self.parent.winfo_width()*0.3)
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.calculate_warning_var.set("Please fill in login details above first")

    def setup_sa_options(self):
        self.update_idletasks()
        wrap_length = self.parent.winfo_width() * 0.7

        #  Pack Statistics Amt options widgets
        self.sa_options_frame.grid(row=5, column=0, padx=20, sticky=tk.W+tk.E)
        self.number_beds_lbl.grid(row=0, column=0, padx=(0, 10), pady=2, sticky=tk.E)
        self.number_beds_lbl.configure(wraplength=wrap_length)
        self.number_beds_entry.grid(row=0, column=1, columnspan=2, pady=2, sticky=tk.W)
        self.number_beds_entry.focus()
        self.closed_lbl.grid(row=1, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.closed_lbl.configure(wraplength=wrap_length)
        self.closed_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 2))
        self.closed_lbl2.grid(row=1, column=2, columnspan=3, pady=(0, 2), sticky=tk.W)
        self.reopen_lbl.grid(row=2, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.reopen_lbl.configure(wraplength=wrap_length)
        self.reopen_combo_d.grid(row=2, column=1, padx=0, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_m.grid(row=2, column=2, padx=2, pady=(0, 2), sticky=tk.W)
        self.reopen_combo_y.grid(row=2, column=3, padx=2, pady=(0, 2), sticky=tk.W)
        self.forced_closed_lbl.grid(row=3, column=0, padx=(0, 10), pady=(0, 2), sticky=tk.E)
        self.forced_closed_lbl.configure(wraplength=wrap_length)
        self.forced_closed_combo.grid(row=3, column=1, sticky=tk.W, pady=(0, 2))
        self.forced_closed_lbl2.grid(row=3, column=2, columnspan=3, pady=(0, 2), sticky=tk.W)
        self.send_to_sa_btn.grid(row=4, column=1, columnspan=3, pady=(0, 10), sticky=tk.E)
        self.send_to_sa_btn.configure(state=tk.ACTIVE)
        self.sa_options_warning_lbl.grid(row=4, column=0, sticky=tk.E, padx=10, pady=(0, 2))
        self.options_separator.grid(row=5, column=0, columnspan=6, pady=2, sticky=tk.W+tk.E)
        if self.sa_login_details.get(self.sa_property, {}).get("beds", 0) > 0:
            self.number_beds_var.set(self.sa_login_details[self.sa_property]["beds"])
        self.send_sa_progress_frame.grid_forget()  # in case coming from 'Yes' resend statistics
        self.update_idletasks()

    def check_sa_options_form(self, sa_property):
        try:
            self.beds = int(self.number_beds_entry.get().replace(",", "").replace(".", ""))
        except ValueError:
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Number of beds must be an integer")
            self.send_to_sa_btn.configure(state=tk.ACTIVE)
            return
        reopen_date = None
        no_reopen_date_chosen = False
        try:
            reopen_date = datetime.strptime("{}-{}-{}".format(self.reopen_combo_d.get(), self.reopen_combo_m.get(),
                                                              self.reopen_combo_y.get()), '%d-%m-%Y')
        except ValueError:
            if self.reopen_combo_d.get() != '' or self.reopen_combo_m.get() != '' or self.reopen_combo_y.get() != '':
                self.sa_options_warning_var.set("Please choose a complete date! TT.MM.JJJJ")
                return
            else:
                no_reopen_date_chosen = True
        if reopen_date is not None:
            if reopen_date < datetime.today():
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Reopen date must be in the future")
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
                return
        if no_reopen_date_chosen:
            self.check_sa_credential("send stats", sa_property)

    def send_statistics(self, status, already_sent_continue=False):
        self.send_sa_progress_lbl.configure(foreground='green')
        self.sa_options_warning_var.set("")
        self.send_sa_progress_var.set("")  # in case coming from 'Yes' resend statistics
        self.send_sa_progress_frame.grid_forget()  # in case coming from 'Yes' resend statistics
        if status == "good":
            if already_sent_continue:
                self.send_sa_progress_var.set("")
                self.send_sa_progress_bar.grid_forget()
                self.send_sa_yes_btn.grid_forget()
                self.send_sa_no_btn.grid_forget()
            sa_options_dict = {
                "beds": self.beds,
                "closed on": self.closed_combo.get(),
                "open on": "{}.{}.{}".format(self.reopen_combo_d.get(), self.reopen_combo_m.get(),
                                             self.reopen_combo_y.get()),
                "force closure": self.forced_closed_combo.get(),
                "sub month": "{} {}".format(self.month_combobox.get(), self.year_combobox.get())
            }
            self.sa_login_details[self.sa_property]["beds"] = self.beds
            if self.beds > 0:
                with open(".data_files/.sa_login.json", 'w', encoding='utf-8') as outfile:
                    json.dump(self.sa_login_details, indent=4, sort_keys=True, fp=outfile)

                    send_stats_thread = threading.Thread(
                        target=statistic_amt.send, args=[self.sa_login_details, sa_options_dict, self.sa_send_queue,
                                                         self.sa_property, self.statistics_results,
                                                         already_sent_continue])
                    send_stats_thread.daemon = True
                    send_stats_thread.start()
                    self.parent.after(100, self.process_sa_send_queue)

                    self.send_sa_progress_frame.grid(row=6, column=0, padx=20, sticky=tk.W+tk.E)
                    self.send_sa_progress_bar.grid(row=0, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
                    self.update_idletasks()
                    self.send_sa_progress_lbl.grid(row=1, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
                    self.send_sa_progress_lbl.configure(wraplength=self.winfo_width() - 40)
                    self.send_sa_separator.grid(row=3, column=0, columnspan=3, pady=2, sticky=tk.W+tk.E)
            elif self.beds == 0:
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.sa_options_warning_var.set("Number of beds must be more than zero!")
        elif status == "bad":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Details incorrect, could not sign in")
            self.sa_user_id_entry.configure(state=tk.ACTIVE)
            self.sa_password_entry.configure(state=tk.ACTIVE)
            self.sa_change_details_btn.configure(state=tk.ACTIVE)
            self.sa_bundesland_combobox.configure(state="readonly")
            self.sa_password_var.set("")
            self.sa_password_entry.focus()
            self.sa_change_details_btn.grid_forget()
            self.sa_save_login_btn.grid(row=5, column=3, pady=2, sticky=tk.E)
            self.sa_change_details_flag = "update"
            self.send_to_sa_btn.configure(state=tk.ACTIVE)
            self.update_idletasks()
        elif status == "failed":
            self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
            self.sa_options_warning_var.set("Statistics Amt website timed out and could not be reached, please try "
                                            "again later.")

    def finish(self):
        self.__init__(self.parent)

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
                self.ma_properties_warn_lbl.configure(wraplength=self.winfo_width() * 0.35)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.ma_properties_warn_var.set("MyAllocator website timed out, please try again later")
            elif message == "connection lost":
                self.ma_properties_warn_lbl.grid(row=9, column=1, columnspan=2, sticky=tk.W)
                self.ma_properties_warn_lbl.configure(wraplength=self.winfo_width() * 0.35)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.ma_properties_warn_var.set("Connection was lost while downloading, please check your internet "
                                                "connection and try again.")
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

    def check_get_properties_queue(self):
        try:
            message = self.get_properties_queue.get(0)
            if message == "Finished":
                self.load_properties()
        except queue.Empty:
            self.parent.after(100, self.check_get_properties_queue)

    def check_hw_cred_queue(self):
        try:
            message = self.hw_cred_queue.get(0)
            if message == "hw ok hw save details":
                self.hw_credential_ok("good")
            elif message == "hw not ok hw save details":
                self.hw_credential_ok("bad")
            elif message == "hw page timeout hw save details":
                self.hw_credential_ok("failed")
            elif message[0] == "hw pass expire hw save details":
                self.hw_credential_ok("good pass expire {}".format(message[1]))
            elif message == "hw ok calculate stats":
                self.hw_get_bookings("good")
            elif message == "hw not ok calculate stats":
                self.hw_get_bookings("bad")
            elif message == "hw page timeout calculate stats":
                self.hw_get_bookings("failed")
            elif message[0] == "hw pass expire calculate stats":
                self.hw_get_bookings("good pass expire {}".format(message[1]))
            else:
                self.hw_warning_var.set(message)
        except queue.Empty:
            self.parent.after(100, self.check_hw_cred_queue)

    def check_hw_download_queue(self):
        try:
            message = self.hw_download_queue.get(0)
            if message == "Finished":
                self.bookings_file = "hw_bookings.csv"
                self.channel_manager = "Hostel World"
                self.calculate_warning_var.set("")
                self.hw_download_lbl.grid_forget()
                self.hw_download_bar.grid_forget()
                self.calculate_statistics(hw_bookings_downloaded=True)
            elif isinstance(message, int):
                self.hw_download_bar.step(message)
                self.parent.after(100, self.check_hw_download_queue)
            else:
                self.calculate_warning_var.set(message)
                self.parent.after(100, self.check_hw_download_queue)
        except queue.Empty:
            self.parent.after(100, self.check_hw_download_queue)

    def check_sa_cred_queue(self):
        try:
            message = self.sa_cred_queue.get(0)
            if message == "sa ok sa save details update" or message == "sa ok sa save details new":
                self.sa_credential_ok("good")
                self.parent.after(100, self.check_sa_cred_queue)
            elif message[0] == "sa not ok sa save details update":
                self.sa_credential_ok("bad update")
            elif message[0] == "sa not ok sa save details new":
                self.sa_credential_ok(["bad new", message[1]])
            elif message == "sa page timeout sa save details update" or \
                    message == "sa page timeout sa save details new":
                self.sa_credential_ok("failed")
            elif message == "sa address bad sa save details":
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
            elif message == "wrong csv/channel":
                self.calculate_warning.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
                self.calculate_warning.configure(wraplength=self.parent.winfo_width()*0.3)
                self.warning_lbl_style.configure('Warning.TLabel', foreground='red')
                self.calculate_warning_var.set("Could not calculate the statistics properly, please make sure you have"
                                               " chosen the correct channel manager above and the correct 'csv' file "
                                               "and try again.")
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
                self.send_sa_no_btn.grid(row=2, column=1, pady=2, sticky=tk.W)
            elif message == "assertion error":
                self.send_sa_progress_lbl.configure(foreground='red')
                self.send_sa_progress_var.set("Sorry! Something went wrong and the statistics could not be entered "
                                              "correctly, please check the options above and try again.")
                self.send_to_sa_btn.configure(state=tk.ACTIVE)
            elif isinstance(message, int):
                self.send_sa_progress_bar.step(message)
                self.parent.after(10, self.process_sa_send_queue)
            elif isinstance(message, list):
                os.remove(self.bookings_file)
                self.send_sa_progress_var.set("Statistics for {} successfully sent!".format(message[1]))
                import display_results
                display_results.display_results(self, message[2], message[1])
                self.send_sa_finish_btn.grid(row=2, column=0, pady=2, sticky=tk.W)
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
    if sys.platform == "win32":
        root.wm_iconbitmap(default=".icons/statistik-rechner-red.ico")
    root.resizable(0, 0)
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
