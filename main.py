import flet
from flet import *
import requests
import datetime
from dotenv import load_dotenv
import os
import json
import time as tm
import google.generativeai as genai
from datetime import datetime
import time
import flet as ft
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64
import urllib
import matplotlib.pyplot as plt
from flet import Image
def get_time_based_on_ip():
    # Get public IP address
    public_ip = requests.get('https://api.ipify.org').text

    # Get location data based on IP address
    location_data = requests.get(f'http://ip-api.com/json/{public_ip}').json()

    # Get the timezone from the location data
    timezone = location_data['timezone']

    # Get the current time in that timezone
    time_data = requests.get(f'http://worldtimeapi.org/api/timezone/{timezone}').json()

    # Convert the datetime string into a datetime object
    current_time = datetime.fromisoformat(time_data['datetime'].replace('Z', '+00:00'))

    if current_time.hour>=19 or current_time.hour<=5:
        return "night"
    else:
        return "day"

# Use the function
time = get_time_based_on_ip()
print(time)

load_dotenv('.env')

#Importing the module for Google's Gemini Pro Ai model
api_key = os.getenv('API_KEY')

if api_key is None:
    raise Exception("API_KEY is not set in the environment variables")
os.environ['GOOGLE_API_KEY'] = api_key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-pro')

#Open weather api key
weather_api_key ="95a00349c5073a6d26b966d3d00e45d5"

# Get location data
location_response = requests.get('http://ip-api.com/json/')
location_data = location_response.json()
latitude = location_data['lat']
longitude = location_data['lon']
city = location_data['city']
state = location_data['region']

# Get weather forecast data
_current = requests.get(f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric")
weather_data = _current.json()

# Get air quality data
_air_quality = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={weather_api_key}")
air_quality_data = _air_quality.json()

if 'weather' in weather_data and len(weather_data['weather']) > 0:
    weather = weather_data['weather'][0]['description'].lower()
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    temperature = weather_data['main']['temp']
    # Get the air quality index from the air quality data
    air_quality = air_quality_data['list'][0]['main']['aqi']
else:
    print("No weather data available")
    weather = ""

days=[
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
    "Sat",
    "Sun",
]
print(weather)
# Add this function to your existing code
def get_uv(lat, lon, api_key):
    # Get UV index
    uv_url = f"http://api.openweathermap.org/data/2.5/uvi/forecast?lat={lat}&lon={lon}&appid={api_key}&cnt=5"
    uv_response = requests.get(uv_url)
    uv_data = uv_response.json()

    # Create a dictionary to hold the date and UV index
    uv_indices = {}

    for item in uv_data:
        # Convert timestamp to date
        date = datetime.fromtimestamp(item['date']).date()
        uv_indices[date] = item['value']

    return uv_indices

# Call the function with latitude, longitude, and your API key
uv_indices = get_uv(latitude, longitude, weather_api_key)

# Call the function with latitude, longitude, and your API key
uv_plot = get_uv(latitude, longitude, weather_api_key)


from google.api_core.exceptions import FailedPrecondition

def generate_content(weather):
    # Generate a suitable prompt based on the weather data
    prompt = f"The weather in {city} city is {weather}. What should I do? (Give me under 20 words)"
    try:
        response = model.generate_content(prompt)
        # Return the plain text response
        return response.text
    except FailedPrecondition:
        return 'No suggestions'
def generate_contents(temperatures):
    # Generate a suitable prompt based on the weather data
    suggestions = []
    for day_of_week, avg_temp in temperatures.items():
        prompt = f"The average temperature in {city} city on {day_of_week} is expected to be {avg_temp}°C. What should I do? (Give me under 20 words)"
        response = model.generate_content(prompt)
        # Append the plain text response to the list of suggestions
        suggestions.append(f"For {day_of_week}: {response.text}")
    return suggestions

def show_loading_screen(page: ft.Page):
    # Display your loading screen here
    page.add(ft.Text("Loading..."))
    tm.sleep(3)  # Wait for 3 seconds
    page.clear()  # Clear the loading screen

def main(page: Page):
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
        "Open Sans": "fonts/OpenSans-Regular.ttf",
        "Montserrat": "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap",
        "Kalam": "fonts/Kalam-Light.ttf",
    }
    page.horizontal_alignment='center'
    page.vertical_alignment='center'
    def _expand(e):
        if e.data=="true":
            _c.content.controls[1].height=560
            _c.content.controls[1].update()
            # Wait for 5 seconds before reverting back to the original size
            tm.sleep(5)
            _c.content.controls[1].height=660*0.25
            _c.content.controls[1].update()
    
    def _current_temp():
        #Open weather api
        _current_temp = int(weather_data['main']['temp'])
        return [_current_temp]
    
    #Extra details
    def _current_extra():
        _extra_info = []
        _extra = [
            [
                int(_current.json()["visibility"]/1000),
                "Km",
                "Visibility",
                "./assets/visibility.gif"
            ],
            [
                round(_current.json()["main"]["pressure"]*0.03,2),
                "inHg",
                "Pressure",
                "./assets/barometer.gif"
            ],
            [
            datetime.fromtimestamp(
                _current.json()["sys"]["sunset"]
            ).strftime("%I:%M %p"),
            "",
            "Sunset",
            "./assets/sunset.gif",
            ],
            [
            datetime.fromtimestamp(
                _current.json()["sys"]["sunrise"]
            ).strftime("%I:%M %p"),
            "",
            "Sunrise",
            "./assets/sunrise.gif",
            ],
        ]
        for data in _extra:
            _extra_info.append(
                Container(
                    bgcolor="white10",
                    border_radius=12,
                    alignment=alignment.center,
                    content=Column(
                        alignment='center',
                        spacing=25,
                        controls=[
                            Container(
                                alignment=alignment.center,
                                content=Image(
                                    src=data[3],
                                    color="white",
                                ),
                                width=32,
                                height=32,
                            ),
                            Text(f"{data[0]} {data[1]}", color="white", font_family="Kalam"),  # Set the font to "Kalam"
                            Text(data[2], color="white", font_family="Kalam"),  # Set the font to "Kalam"
                        ]
                    )
                )
            )
        return _extra_info

    def _top():
        _today = _current_temp()

        _today_extra = GridView(
            max_extent=150,
            expand=1,
            run_spacing=5,
            spacing=5,
            runs_count=2
        )

        for info in _current_extra():
            _today_extra.controls.append(info)

        if weather in ["clear sky", "few clouds"]:
            image_source = f"./assets/{weather}_{time}.gif"
        else:
            image_source = f"./assets/{weather}.gif"

        row_controls = [
            Column(
                controls=[
                    Container(
                        width=70,
                        height=70,
                        image_src=f"./assets/humid.gif"  
                    ),
                    Text("Humidity", font_family="Kalam", size=15),
                    Text(str(humidity)+" %", font_family="Kalam", size=15)
                ]
            ),
            Column(
                controls=[
                    Container(
                        width=70,
                        height=70,
                        image_src=f"./assets/air.gif"  
                    ),
                    Text("Air Quality", font_family="Kalam", size=15),
                    Text(str(air_quality), font_family="Kalam", size=15)
                ]
            ),
            Column(
                alignment='center',
                controls=[
                    Container(
                        width=70,
                        height=70,
                        image_src=f"./assets/wind.gif"  
                    ),
                    Text("Wind", font_family="Kalam", size=15),
                    Text(str(int(wind_speed))+" kmph", font_family="Kalam", size=15)
                ]
            )
        ]

        row = Row(
            alignment='center',
            spacing=30,
            controls=row_controls
        )

        top = Container(
            width=330,
            height=660 * 0.25,
            gradient=LinearGradient(
                begin=alignment.bottom_left,
                end=alignment.top_right,
                colors=["lightblue600","lightblue900"] if time == "day" else ["grey600", "grey900"],
            ),
            border_radius=35,
            animate=animation.Animation(duration=350,curve='decelerate'),
            on_hover=lambda e: _expand(e),
            padding=15,
            content=Column(
                alignment='start',
                spacing=10,
                controls=[
                    Row(
                        alignment='center',
                        controls=[
                            Text((city+","+state),
                                size=16,
                                weight="w500",
                                font_family="Kalam"
                            )
                        ],
                    ),
                    Container(padding=padding.only(bottom=5)),
                    Row(
                        alignment='center',
                        spacing=30,
                        controls=[
                            Container(
                                width=90,
                                height=90,
                                image_src=image_source
                            ),
                            Text(str(_today[0]) + "°C",
                                font_family="Kalam",
                                size=50)
                        ]
                    ),
                    _today_extra,
                    row,
                    Container(
                        padding=padding.only(top=20),
                        content=Text(
                            generate_content(weather),
                            font_family="Kalam",
                            size=15
                        )
                    )
                ]
            )
        )
        return top

    
    #Bottom data
    def _bot_data():
        _bot_data = []

        # Add column names to _bot_data
        _bot_data.append(
            Row(
                spacing=5,
                alignment='spaceBetween',
                controls=[
                    Text("DAY", font_family="Kalam", size=15),
                    Text("TEMP", font_family="Kalam", size=15),
                    Text("UV", font_family="Kalam", size=15)
                ]
            )
        )

        # Get weather forecast data
        forecast_response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric")
        forecast_data = forecast_response.json()
        forecast_list = forecast_data['list']

        # Initialize dictionary to hold date:temperature pairs
        forecast_dict = {}

        # Call the get_uv function and get the uv_indices
        uv_indices = get_uv(latitude, longitude, weather_api_key)

        for item in forecast_list:
            # Convert timestamp to date
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in forecast_dict:
                forecast_dict[date] = []

            # Append temperature to list of temperatures for this date
            forecast_dict[date].append(item['main']['temp'])

        # Calculate average temperature for each day
        for date, temps in forecast_dict.items():
            avg_temp = sum(temps) / len(temps)
            day_of_week = date.strftime('%A')
            uv_index = uv_indices.get(date, 'No data')  # Get the UV index for the day, or 'No data' if not available
            _bot_data.append(
                Row(
                    spacing=5,
                    alignment='spaceBetween',
                    controls=[
                        Text(day_of_week, font_family="Kalam", size=15),
                        Text(f" {round(avg_temp)}°C", font_family="Kalam", size=15),
                        Text(f"{uv_index}", font_family="Kalam", size=15)
                    ]
                )
            )
        return _bot_data




    #Bottom weather forecast
    def _bottom():
        _bot_column=Column(
            alignment='center',
            horizontal_alignment="center",
            spacing=25,
        )
        
        for data in _bot_data():
            _bot_column.controls.append(data)

        bottom=Container(
            padding=padding.only(top=200,left=20,right=20,bottom=20),
            content=_bot_column,  # Use the grid as the content
        )
        return bottom

    #Defining the container
    _c=Container(
        width=310,
        height=660,
        border_radius=35,
        bgcolor='black',
        padding=10,
        content=Stack(
            width=300,height=550,
            controls=[
                _bottom(),
                _top()
            ]
        )
    )
    page.add(_c)

if __name__ == '__main__':
     flet.app(target=main, assets_dir="assets")