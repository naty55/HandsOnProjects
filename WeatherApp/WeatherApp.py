import tkinter as tk
import requests
from customize_widgets import *

HEIGHT = 700
WIDTH = 800


def set_settings_page():
    sett_frame = tk.Frame(root, bg='#ddddee', bd=10)
    sett_frame.place(relwidth=1, relheight=1)

    default_city_label = tk.Label(sett_frame, text='Default city: ', font=settings_font)
    default_city_label.place(rely=0.1, relx=0.15, relwidth=0.25, relheight=0.05)
    default_city_entry = tk.Entry(sett_frame, font=settings_font, bg='#eeffdd')
    default_city_entry.place(rely=0.1, relx=0.45, relwidth=0.25, relheight=0.05)

    set_dark_mode_label = tk.Label(sett_frame, text='Dark Mode', font=settings_font)
    set_dark_mode_label.place(rely=0.2, relx=0.15, relwidth=0.25, relheight=0.05)
    set_dark_mode_button = Button(sett_frame, text='Off', font=settings_font)
    set_dark_mode_button.place(rely=0.2, relx=0.45, relwidth=0.25, relheight=0.05)

    button_back = Button(sett_frame, text='Back', command=lambda: sett_frame.destroy())
    button_back.place(relx=0.5, rely=0.7, anchor='n')


def weather_to_text(weather):
    try:
        name = weather['name']
        desc = weather['weather'][0]['description']
        temp = round(weather['main']['temp'])
        feels_like = round(weather['main']['feels_like'])

        weather_str = f'Name: {name}\nDescription: {desc}\nTemp: {temp} °C\nFeels like: {feels_like}'

    except:
        weather_str = "Sorry!\nThere was a problem\ngetting this information!"

    return weather_str


def get_weather(city):
    weather_key = 'e5ff933059a94af2c4ba4e553f21c682'
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'APPID': weather_key,
              'q': city,
              'units': 'Metric' }
    response = requests.get(url, params=params)
    text = weather_to_text(response.json())

    label['text'] = text


root = tk.Tk()
root.title('WeatherApp')
root.maxsize(1200, 700)

default_font  = ('Courier', 18)
settings_font = ('Courier', 16)
welcome_txt = 'Hi!\nWelcome to my weather app'
space_between = 0.05/3

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

background_image = tk.PhotoImage(file='images/landscape.png')
background_label = tk.Label(image=background_image)
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg='#80c1ff', bd=5)
frame.place(relx=0.5, rely=0.1, relwidth=0.8, relheight=0.1, anchor='n')

entry = tk.Entry(frame, font=default_font)
entry.place(relx=space_between, rely=0.05, relwidth=0.65, relheight=0.9)

button = Button(frame, text='Get Weather', font=default_font, command=lambda: get_weather(entry.get()))
button.place(relx=(2 * space_between + 0.65), rely=0.05, relwidth=0.3, relheight=0.9)

lower_frame = tk.Frame(root, bg='#80c1ff', bd=5)
lower_frame.place(relx=0.5, rely=0.25, relwidth=0.8, relheight=0.6, anchor='n')

label = tk.Label(lower_frame, text=welcome_txt, font=default_font, anchor='nw', justify='left')
label.place(relwidth=1, relheight=1)

settings_icon = tk.PhotoImage(file='./images/settings_icon.png')
settings_button = Button(root, image=settings_icon, justify='center', command=set_settings_page)
settings_button.place(rely=0.01, relx=0.01, relwidth=0.065, relheight=0.065)

root.mainloop()
