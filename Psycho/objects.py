import tkinter as tk

class TkinterObject:
    def __init__(self, master, object_type, x, y, width=None, height=None, text='', font=None, anchor=None):
        self.type = object_type
        self.master = master
        self.object = self.create()
    def create(self):
        self.type()
    def apply(self):
        self.object.place(x=self.x, y=self.y)
