import tkinter as tk
from settings import settings as ws
from menu_bar import MenuBar
from pages import MainFrame, DefaultEnglishPage, AddWord, QuizPage, Page, SettingsPage

"""
import win32gui, win32con

The_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(The_program_to_hide , win32con.SW_HIDE)
"""


class App:
    """ class to describe the whole pages on the app and control events handling """

    def __init__(self, window):
        """
        initialize the app to its starting point (default welcome page and menu bar on its side
        :param window: tk.root
        """
        self.main_frame = MainFrame(window)
        self.main_frame.master.bind("<BackSpace>", lambda event: self.go_back())
        self.main_frame.back_o["command"] = self.go_back
        self.menu_bar = MenuBar(window, self.set_home_page, self.set_english_page, self.set_settings_page)

        self.menu_bar.apply()
        self.main_frame.apply()
        self.set_home_page()

    def set_home_page(self):
        """
        Clean previous pages and create home page and render it to the screen
        :return: None
        """
        self.refresh()
        body = Page(self.main_frame.frame)
        body.add_object(tk.Label, text='HI welcome to Learning Log', font=body.font, width=50)
        body.apply()
        self.main_frame.update(body.name)

    def set_english_page(self):
        """
        Clean previous pages and create default english page and render it to the screen
        :return: None
        """
        self.refresh()
        body = DefaultEnglishPage(self.main_frame.frame)
        body.btn_pra.config(command=self.set_quiz_page)
        body.btn_add.config(command=self.set_new_word_page)
        self.main_frame.update(body.name)

    def set_new_word_page(self):
        """
        Clean previous pages and create new_word page (used for adding new learned word)
        and render it to the screen
        :return: None
        """
        self.refresh()
        body = AddWord(self.main_frame.frame)
        # let the user use the enter key for saving the new word
        self.main_frame.master.bind('<Return>', body.keypress_handler)
        # unbind backspace in order to avoid confusion with go back to last page
        self.main_frame.master.unbind('<BackSpace>')
        self.main_frame.update(body.name)

    def set_quiz_page(self):
        """
        Clean previous pages and create quiz page and render it to screen
        :return: None
        """
        self.refresh()
        body = QuizPage(self.main_frame.frame)
        self.main_frame.update(body.name)

    def set_settings_page(self):
        """
        Clean previous pages and create settings page and render it to the screen
        :return: None
        """
        self.refresh()
        body = SettingsPage(self.main_frame.frame)
        self.main_frame.update(body.name)

    def go_back(self):
        last_page = self.main_frame.last_page
        if last_page == "Home":
            self.set_home_page()
        if last_page == "DefaultEnglishPage":
            self.set_english_page()
        if last_page == "QuizPage":
            self.set_quiz_page()

    def refresh(self):

        self.main_frame.clean_page()

        # unbind and rebind events which might be bind or unbind
        # for function for other pages that doesn't exist
        self.main_frame.master.unbind('<Return>')
        self.main_frame.master.bind("<BackSpace>", lambda event: self.go_back())


window = tk.Tk()
window.title(ws.title)
window.geometry(ws.win_size)
app = App(window)
window.mainloop()
