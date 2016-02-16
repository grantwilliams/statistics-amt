import os
import sys
import threading
import queue
import multiprocessing
import tkinter as tk
from tkinter import ttk
import json
import myallocator


"""
ma refers to MyAllocator
sa refers to Statistik Amt
"""


class MainWindow(ttk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)

        self.download_queue = multiprocessing.Queue()
        self.message_queue = multiprocessing.Queue()

        self.ma_login_details = dict()
        if os.path.isfile("data_files/ma_login.json"):
            with open("data_files/ma_login.json") as ma_json:
                self.ma_login_details = json.load(ma_json)

        self.theme = ttk.Style()
        self.theme.theme_create("dark_theme", parent="clam", settings={
            "TFrame": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}},
            "TLabel": {"configure": {"background": "#242424", "foreground": "#0FF1F0", "font": ("Helvetica Neue", 12),
                                     "padx": 20}},
            "TButton": {"configure": {"background": "#242424", "foreground": "#0FF1F0", "font": ("Helvetica Neue", 12),
                                      "relief": "raised", "padding": 2
                                      }},
            "TCheckbutton": {"configure": {"background": "#242424", "foreground": "#0FF1F0",
                                           "font": ("Helvetica Neue", 10)}},
            "TEntry": {"configure": {"background": "#242424", "foreground": "#242424", "font": ("Helvetica Neue", 12)}},
            "Horizontal.TProgressbar": {"configure": {"background": "#242424", "foreground": "#0FF1F0"}}
        })
        self.theme.theme_use("dark_theme")

        self.label_title = ttk.Style()
        self.label_title.configure("title.TLabel", font=("Helvetica Neue", 16))
        self.warning_lbl_style = ttk.Style()
        self.warning_lbl_style.configure('Warning.TLabel', font=("Helvetica Neue", 10), foreground="red")

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill=tk.X)
        self.title = ttk.Label(self.title_frame, text="Statistics")
        self.title.pack(side=tk.TOP, pady=10)
        self.setup_ma("main")

    def setup_ma(self, origin):
        bullet = "\u2022"
        #  MyAllocator login widgets
        self.ma_title_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ma_form_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ma_title_frame = ttk.Frame(self)
        self.ma_title_lbl = ttk.Label(self.ma_title_frame, style="title.TLabel", text="MyAllocator login details")
        self.ma_form_frame = ttk.Frame(self)
        self.ma_username_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Username: ")
        self.ma_username_var = tk.StringVar()
        self.ma_username_entry = ttk.Entry(self.ma_form_frame, width=30, textvariable=self.ma_username_var,
                                           state=tk.DISABLED)
        self.ma_password_lbl = ttk.Label(self.ma_form_frame, text="MyAllocator Password: ")
        self.ma_password_var = tk.StringVar()
        self.ma_password_entry = ttk.Entry(self.ma_form_frame, show=bullet, width=30, textvariable=self.ma_password_var)
        self.ma_password_confirm_lbl = ttk.Label(self.ma_form_frame, text="Confirm Password: ")
        self.ma_password_confirm_var = tk.StringVar()
        self.ma_password_confirm_entry = ttk.Entry(self.ma_form_frame, show=bullet, width=30,
                                                   textvariable=self.ma_password_confirm_var)
        self.ma_button_frame = ttk.Frame(self)
        self.ma_save_login_btn = ttk.Button(self.ma_button_frame, text="Save login details",
                                            command=lambda: self.save_ma_login("save_login"))
        self.ma_get_properties_btn = ttk.Button(self.ma_button_frame, text="Get Properties",
                                                command=self.get_properties)
        self.ma_change_detials_btn = ttk.Button(self.ma_button_frame, text="Change login details",
                                                command=self.ma_change_details)
        self.ma_warning_var = tk.StringVar()
        self.ma_warning = ttk.Label(self.ma_form_frame, style="Warning.TLabel", textvariable=self.ma_warning_var)

        #  pack MyAllocator widgets
        self.ma_title_frame.pack(fill=tk.X)
        self.ma_title_lbl.pack(side=tk.LEFT, padx=20)
        self.ma_title_separator.pack(fill=tk.X, padx=20, pady=2)
        self.ma_form_frame.pack(fill=tk.X)
        self.ma_username_lbl.grid(row=0, column=0, sticky=tk.E, padx=20, pady=2)
        self.ma_username_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.ma_username_var.set(self.ma_login_details["ma_username"])
        self.ma_password_lbl.grid(row=1, column=0, sticky=tk.E, padx=20, pady=2)
        self.ma_password_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.ma_password_entry.focus()
        self.ma_password_var.set(self.ma_login_details["ma_password"])
        self.ma_password_confirm_lbl.grid(row=2, column=0, sticky=tk.E, padx=20, pady=2)
        self.ma_password_confirm_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.ma_password_confirm_var.set(self.ma_login_details["ma_password"])
        self.ma_button_frame.pack(fill=tk.X)
        self.ma_warning.grid(row=4, column=1, sticky=tk.W, pady=2)
        self.ma_form_separator.pack(fill=tk.X, padx=20, pady=2)
        if self.ma_login_details["ma_password"] != "":
            self.ma_change_detials_btn.pack(side=tk.RIGHT, padx=(5, 20))
            self.ma_get_properties_btn.pack(side=tk.RIGHT, pady=2)
            self.ma_password_entry.configure(state=tk.DISABLED)
            self.ma_password_confirm_entry.configure(state=tk.DISABLED)
        else:
            self.ma_save_login_btn.pack(side=tk.RIGHT, padx=20, pady=2)

    def ma_change_details(self):
        self.ma_password_entry.configure(state=tk.ACTIVE)
        self.ma_password_var.set("")
        self.ma_password_entry.focus()
        self.ma_password_confirm_entry.configure(state=tk.ACTIVE)
        self.ma_password_confirm_var.set("")
        self.ma_change_detials_btn.forget()
        self.ma_get_properties_btn.forget()
        self.ma_save_login_btn.pack(side=tk.RIGHT, padx=20, pady=2)

    #  tries to sign into MA
    def check_ma_cred(self, login_details):
        return myallocator.check_cred(login_details)

    def save_ma_login(self, origin):
        self.ma_username = self.ma_username_entry.get()
        self.ma_password = self.ma_password_entry.get()
        self.ma_password_confirm = self.ma_password_confirm_entry.get()

        if origin == "save_login":
            if self.ma_password == self.ma_password_confirm and self.ma_username != '' and self.ma_password != '':
                self.ma_warning_var.set("")
                self.ma_login_details["ma_username"] = self.ma_username
                self.ma_login_details["ma_password"] = self.ma_password
                with open("data_files/ma_login.json", "w") as outfile:
                    json.dump(self.ma_login_details, outfile)

                # tries to login to MA with credentials given, and checks whether it was successful
                if myallocator.check_cred(self.ma_login_details):
                    self.ma_save_login_btn.forget()
                    self.ma_change_detials_btn.pack(side=tk.RIGHT, padx=(5, 20))
                    self.ma_get_properties_btn.pack(side=tk.RIGHT, pady=2)
                    self.ma_password_entry.configure(state=tk.DISABLED)
                    self.ma_password_confirm_entry.configure(state=tk.DISABLED)
                else:
                    self.ma_warning_var.set("Password incorrect, could not sign in.")
                    self.ma_password_var.set("")
                    self.ma_password_confirm_var.set("")
                    self.ma_password_entry.focus()
            elif self.ma_username == '' or self.ma_password == '' or self.ma_password_confirm == '':
                self.ma_warning_var.set("One or more fields are empty!")
            elif self.ma_password != self.ma_password_confirm:
                self.ma_warning_var.set("Passwords do not match, please try again.")

    def get_properties(self):
        load_properties = False
        if myallocator.check_cred(self.ma_login_details):
            self.ma_button_frame.destroy()
            self.ma_password_entry.configure(state=tk.DISABLED)
            self.ma_password_confirm_entry.configure(state=tk.DISABLED)
            property_process = multiprocessing.Process(target=myallocator.get_properties, args=(self.ma_login_details,))
            property_process.daemon = True
            property_process.start()
            load_properties = True
        else:
            self.ma_warning_var.set("Password incorrect, could not sign in.")
            self.ma_password_entry.configure(state=tk.ACTIVE)
            self.ma_password_var.set("")
            self.ma_password_entry.focus()
            self.ma_password_confirm_entry.configure(state=tk.ACTIVE)
            self.ma_password_confirm_var.set("")
            self.ma_change_detials_btn.forget()
            self.ma_get_properties_btn.forget()
            self.ma_save_login_btn.pack(side=tk.RIGHT, padx=20, pady=2)

        self.ma_properties = dict()
        with open("data_files/properties.json") as propfile:
            self.ma_properties = json.load(propfile)
        if load_properties:
            self.ma_properties_frame = ttk.Frame(self)
            self.ma_properties_lbl = ttk.Label(self.ma_properties_frame, text="Property: ")
            self.ma_properties_combobox = ttk.Combobox(self.ma_properties_frame,
                                                       values=sorted(list(self.ma_properties.keys())),
                                                       text="--Select Property--")
            self.ma_properties_btn = ttk.Button(self.ma_properties_frame, text="Download Bookings",
                                                command=self.download_bookings)
            self.ma_properties_serparator = ttk.Separator(self, orient=tk.HORIZONTAL)
            self.ma_properties_frame.pack(fill=tk.X)
            self.ma_properties_lbl.grid(row=0, column=0, sticky=tk.E, padx=20, pady=2)
            self.ma_properties_combobox.grid(row=0, column=1, sticky=tk.W, pady=2)
            self.ma_properties_btn.grid(row=0, column=2, sticky=tk.E, padx=20, pady=2)
            self.ma_properties_combobox.current(0)
            self.ma_properties_serparator.pack(fill=tk.X, padx=20, pady=2)

    def download_bookings(self):
        property = self.ma_properties[self.ma_properties_combobox.get()]
        if property != "":
            self.ma_properties_btn.configure(state=tk.DISABLED)
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
                                                    text="Please choose a property first.")
            self.ma_properties_warn_lbl.grid(row=1, column=1, columnspan=2, sticky=tk.W)

    def setup_sa(self):
        bullet = "\u2022"
        bundeslaende = {}
        #  Statistik Amt login widgets
        self.sa_title_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.sa_form_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.sa_title_frame = ttk.Frame(self)
        self.sa_title_lbl = ttk.Label(self.sa_title_frame, style="title.TLabel", text="Statistik Amt login details")
        self.sa_form_frame = ttk.Frame(self)
        self.sa_user_id_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt ID nr: ")
        self.sa_user_id_entry = ttk.Entry(self.sa_form_frame, width=30)
        self.sa_password_lbl = ttk.Label(self.sa_form_frame, text="Statistik Amt Password: ")
        self.sa_password_entry = ttk.Entry(self.sa_form_frame, show=bullet, width=30)
        self.sa_password_confirm_lbl = ttk.Label(self.sa_form_frame, text="Confirm Password: ")
        self.sa_password_confirm_entry = ttk.Entry(self.sa_form_frame, show=bullet, width=30)

        self.sa_separator = ttk.Separator(self.sa_form_frame, orient=tk.HORIZONTAL)
        self.bundesland_value = tk.StringVar()
        self.bundesland_combobox_lbl = ttk.Label(self.sa_form_frame, text="Bundesland: ")
        self.bundesland_combobox = ttk.Combobox(self.sa_form_frame, textvariable=self.bundesland_value)
        self.month_lbl = ttk.Label(self.sa_form_frame, text="Submission Month: ")
        self.month_value = tk.StringVar()
        self.year_value = tk.StringVar()
        self.month_combobox = ttk.Combobox(self.sa_form_frame, textvariable=self.month_value)
        self.year_combobox = ttk.Combobox(self.sa_form_frame, textvariable=self.year_value)

        self.number_beds_lbl = ttk.Label(self.sa_form_frame, text="Number of Beds: ")
        self.number_beds_entry = ttk.Entry(self.sa_form_frame, width=10)

        #  pack Statistik Amt widgets
        self.sa_title_frame.pack(fill=tk.X)
        self.sa_title_lbl.pack(side=tk.LEFT, padx=20)
        self.sa_title_separator.pack(fill=tk.X, padx=20, pady=2)
        self.sa_form_frame.pack(fill=tk.X)
        self.sa_user_id_lbl.grid(row=0, column=0,sticky=tk.E, padx=20, pady=2)
        self.sa_user_id_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.sa_password_lbl.grid(row=1, column=0, sticky=tk.E, padx=20, pady=2)
        self.sa_password_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.sa_password_confirm_lbl.grid(row=2, column=0, sticky=tk.E, padx=20, pady=2)
        self.sa_password_confirm_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=2)

    def load_bar(self):
        try:
            message = self.download_queue.get(0)
            if message == "Finished!":
                self.download_lbl_var.set(message)
                self.parent.after(100, self.load_bar)
            if 3 > len(str(message)) > 0:
                if message <= 80:
                    self.download_bar.step(20)
                    self.parent.after(100, self.load_bar)
                else:
                    self.download_bar.step(19)
        except queue.Empty:
            self.parent.after(100, self.load_bar)



def main():
    root = tk.Tk()
    # root.geometry("600x600+500+100")
    # root.minsize(height=600, width=600)
    # root.maxsize(height=600, width=600)
    root.wm_title("Setup")
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
