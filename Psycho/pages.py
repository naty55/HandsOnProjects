""" In this module all the templates for the GUI """
import tkinter as tk
from settings import settings as ws
from dict_control import dict_words
from random import randrange
from score import Track
from PIL import ImageTk, Image
from  time import time


class Page:
    def __init__(self, master):
        self.master = master
        self.name = "Home"
        self.bg = ws.body_bg
        self.width = ws.body_width
        self.height = ws.body_height
        self.font = ws.default_font
        self.frame = tk.Frame(master=self.master, bg=self.bg, width=self.width, height=self.height)
        self.objects = []

    def apply(self, side=tk.LEFT, fill=tk.BOTH):
        for object_ in self.objects[::-1]:
            object_.pack(side=tk.TOP, padx=2, pady=2)
        self.frame.place(relwidth=1, relheight=0.95, rely=0.05)

    def add_object(self, object_, text='', width=None, height=None, bg=None, command=None, font=None, image=None):
        if not font:
            font = self.font
        if object_ is tk.Entry:
            current = object_(master=self.frame, width=width, font=font)
        else:
            current = object_(self.frame, text=text, width=width, height=height, font=font, command=command, image=image, relief='flat', bg=bg)

        self.objects.append(current)
        return current

    def clean_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class MainFrame(Page):
    def __init__(self, master):
        super().__init__(master)
        self.name = 'MainFrame'
        self.current_page = 'Home'
        self.last_page = []
        self.back_icon = tk.PhotoImage(file='./images/go_back_icon.png')
        self.back_o = self.add_object(tk.Button, image=self.back_icon)

    def update(self, page):
        self.last_page = self.current_page
        self.current_page = page
        if self.current_page != "Home":
            self.back_o = self.add_object(tk.Button)

    def apply(self, side='left', fill='both'):
        for object_ in self.objects[::-1]:
            object_.place(relx=0.01, rely=0.005)
        self.frame.place(relx=0.28, relwidth=0.72, relheight=1)

    def clean_page(self):
        for widget in self.frame.winfo_children():
            if "!frame" in widget.winfo_name():
                widget.destroy()


class DefaultEnglishPage(Page):
    """ Describe The Default template for the english section in the app"""

    def __init__(self, master):
        super().__init__(master)
        self.name = 'DefaultEnglishPage'
        self.recently_words = dict_words.get_recent_words()
        self.btn_pra = self.add_object(tk.Button, text='Practice', width=50)
        self.btn_add = self.add_object(tk.Button, text='Add new', width=50)
        self.recently_words_handler()
        self.apply()

    def recently_words_handler(self):
        text = '\nRecently Words\n' + '=' * 30 + '\n'
        for word, trans in self.recently_words.items():
            text += word.capitalize().strip() + '\t' + trans.strip() + '\n'

        self.add_object(tk.Label, text=text, width=50)


class AddWord(Page):
    """ Describe template form for adding new word to the list"""
    def __init__(self, master):
        super().__init__(master)
        self.name = 'AddWord'
        self.new_word_label = self.add_object(tk.Label, text='new word')
        self.new_word_entry = self.add_object(tk.Entry)
        self.trans_label = self.add_object(tk.Label, text='Translation', width=15, height=2)
        self.trans_entry = self.add_object(tk.Entry)
        self.save_button = self.add_object(tk.Button, text='save', width=50, command=self.save)
        self.apply()

    def apply(self):
        self.frame.place(relwidth=1, relheight=0.95, rely=0.05)
        self.new_word_label.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.05)
        self.new_word_entry.place(relx=0.4, rely=0.3, relwidth=0.2, relheight=0.05)
        self.trans_label.place(relx=0.2, rely=0.4, relwidth=0.2, relheight=0.05)
        self.trans_entry.place(relx=0.4, rely=0.4, relwidth=0.2, relheight=0.05)
        self.save_button.place(relx=0.3, rely=0.5, relwidth=0.2, relheight=0.05)

    def save(self):
        new_tran = self.trans_entry.get().strip().capitalize()
        new_word = self.new_word_entry.get().strip()
        if new_word and new_tran:
            dict_words.add_entry({new_word: new_tran})

    def keypress_handler(self, event):
        if event.keysym == 'Return':
            self.save()


class QuizPage(Page):
    """ Describe a template for quiz page and handle scoring"""

    def __init__(self, master):
        super().__init__(master)
        self.name = "QuizPage"
        self.dict_words = dict_words.get_dict()
        self.word_list = list(self.dict_words.keys())
        self.track = Track()

        self.score_o = self.add_object(tk.Label, width=15)
        # create objects list for answers
        self.answers_o = self.create_answers_o()
        self.word_o = self.add_object(tk.Label)
        self.next_btn = None

        # Config objects
        self.new_quest()

        self.apply()

    def gen_answers(self):
        """
        Generate rand answers and make sure you have the right inside and you don't have
        the same answer twice
        """
        answers = [None for i in range(4)]
        answers[randrange(0, 4)] = self.dict_words[self.r_word]
        for i, an in enumerate(answers):
            while not an:
                answer = self.dict_words[self.gen_rand_word()]
                if answer not in answers:
                    an = answer
                    answers[i] = an

        return answers

    def gen_rand_word(self):
        """Return a random word from the dict and make sure it had
        nod not been asked at least in the 10 question before"""

        r_index = randrange(len(self.word_list))
        r_word = self.word_list[r_index]
        return r_word if r_word not in self.track.last_questioned else self.gen_rand_word()

    def create_answers_o(self):
        """ Create 4 button tkinter objects for answers """
        answers = []
        for answer in range(4):
            object_ = self.add_object(tk.Button, width=50)
            object_.config(command=lambda answer=answer, object_=object_: self.check_answer(answer, object_))
            answers.append(object_)
        return answers

    def check_answer(self, object_):
        """ Check answer and return feedback """
        if self.dict_words[self.r_word] == object_['text']:
            fail = None
            self.update_you(object_, 'green')

        else:
            fail = self.r_word
            self.update_you(object_, 'red')

        self.track.update(self.r_word, fail=fail)

    def update_you(self, object_, color):
        """ Return proper feedback to user either the answer is correct or not
            and the create next button which is the trigger to next question"""

        # after answered disable all answers buttons
        for o in self.answers_o:
            o['state'] = tk.DISABLED
            o['disabledforeground'] = 'black'

        object_['bg'] = color
        self.next_btn = self.add_object(tk.Button, text='Next->', bg=color, width=50, command=self.new_quest)
        self.next_btn.pack()

    def new_quest(self):
        """
        Config the page and all objects
        for answers and the question  """

        # Generate rand question and rand answers
        self.r_word = self.gen_rand_word()
        self.answers = self.gen_answers()

        # config question object with the proper text and the question
        text = f"What is the right translation ?\n{'=' * 30}\n{self.r_word}"
        self.word_o.config(text=text)

        # Config answers objects
        for i, o in enumerate(self.answers_o):
            answer = self.answers[i]
            o.config(text=answer, bg='white', state=tk.NORMAL,
                     command=lambda object_=o: self.check_answer(object_))
        # Update Score
        self.score_o.config(text=f'Your score: {self.track.score}\nYour avg.: {self.track.get_average_success()}')

        # Check for next_button if exists and if so destroy it
        if self.next_btn:
            self.next_btn.destroy()


class SettingsPage:
    def __init__(self, master):
        self.name = 'Settings'
        self.i = ImageTk.PhotoImage(Image.open("./images/view.jpg"))
        self.f = tk.Frame(master=master, bg='gray')
        self.l = tk.Label(master=self.f, image=self.i)

        self.f.place(relwidth=1, relheight=0.9)
        self.l.place(rely=0, relx=0)

        self.o = tk.Label(master=self.f, bg='red', bd=0)
        self.o.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.1)
        self.updater = 0
        self.o.after(100, lambda: self.update_you())

    def update_you(self):
        self.updater += 1
        self.g = tk.Label(self.o, bg='green', bd=0)
        if self.updater > 100:
            self.o['bg'] = 'green'
            return
        self.g.place(relx=0, rely=0, relheight=1, relwidth=self.updater/100)
        self.o.after(100, lambda: self.update_you())

