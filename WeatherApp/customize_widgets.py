import tkinter as tk


class Button(tk.Button):
    def __init__(self, master, **k):
        super().__init__(master, k)
        self.config(relief='flat')

