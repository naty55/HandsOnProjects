import tkinter as tk


class Window:
    root = tk.Tk()
    root.geometry('1080x700')

    def __init__(self, title, labels, buttons):
        self.init_title = title
        self.init_labels = labels
        self.init_buttons = buttons

        self.title = title
        self.labels = labels
        self.buttons = buttons

        # Arrays to contain all buttons and labels objects
        self.control_labels = []
        self.control_buttons = []

        self.setup()

    def setup(self):
        self.root.title(self.title)

        for label in self.labels:
            lab_obj = tk.Label(self.root, text=label)
            lab_obj.pack()
            self.control_labels.append(lab_obj)
        for button in self.buttons:
            command = self.get_command(button)
            but_obj = tk.Button(self.root, text=button,command=command)
            but_obj.pack()
            self.control_buttons.append(but_obj)

    def destroy_all(self):
        for lab in self.control_labels:
            lab.destroy()
        for but in self.control_buttons:
            but.destroy()
        self.control_buttons = []
        self.control_labels = []

    def english(self):
        self.destroy_all()
        self.labels = ['English is Fun']
        self.buttons = ['Home Page']
        self.title = 'English'

        self.setup()

    def home_page(self):
        self.destroy_all()
        self.__init__(self.init_title, self.init_labels, self.init_buttons)

    def get_command(self, button):
        button = button.lower()
        command = None
        if button == 'english':
            command = self.english
        elif button == 'home page':
            command = self.home_page