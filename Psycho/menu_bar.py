import tkinter as tk
from settings import settings as ws


class MenuBar:
    def __init__(self, master, home_btn, english_btn, settings_btn):
        self.master = master
        self.btn_width = ws.menu_btn_width
        self.btn_clr = ws.menu_btn_clr
        self.root = tk.Frame(master=master, bg=ws.menu_bar_bg, width=ws.menu_bar_width, height=ws.menu_bar_height, bd=5)
        self.buttons = []

        self.btn_home = self.create_button(text='Home', command=home_btn)
        self.btn_add = self.create_button(text='+ Add new', command=self.add_button)
        self.btn_english = self.create_button(text='English', command=english_btn)
        self.btn_settings = self.create_button(text='Settings', command=settings_btn)
        self.label_credit = tk.Label(self.root, text='Created by <Naty Mina>', font=('Courier', 10))

    def create_button(self, text, command):
        button = tk.Button(self.root, text=text, bg=ws.menu_btn_clr,
                           relief=tk.FLAT, borderwidth=1, command=command, activebackground='grey',
                           font=('Courier', 14))
        self.buttons.append(button)
        return button

    def apply(self):
        self.root.place(relwidth=0.28, relheight=1)
        self.btn_home.place(relwidth=0.9, relheight=0.1,relx=0.05, rely=0.05)
        self.btn_english.place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.15)
        self.btn_settings.place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.25)
        self.btn_add.place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.35)
        self.label_credit.place(relwidth=0.9, relheight=0.02, relx=0.05, rely=0.98)

    def add_button(self):
        pass