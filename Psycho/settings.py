class Settings:
    def __init__(self):
        # Set the menu bar settings
        self.menu_bar_bg = 'seashell2'
        self.menu_bar_width, self.menu_bar_height = 360, 700
        self.menu_btn_width = 25
        self.menu_btn_height = 2
        self.menu_btn_pad = 2
        self.menu_btn_clr = 'seashell3'

        # Set the general window settings
        self.win_size = '1200x700'
        self.title = 'Psycho Project'
        self.default_font = ('Courier', 14)

        # Set body settings
        self.body_bg = '#80aaff'
        self.body_width, self.body_height = 1006, 700


settings = Settings()

