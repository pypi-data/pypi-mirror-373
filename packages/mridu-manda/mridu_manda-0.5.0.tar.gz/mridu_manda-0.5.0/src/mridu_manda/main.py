import requests
import time
import os
from mridu_manda import setup_mridumanda


def main():
    setup_mridumanda.setup()
    
    print("Welcome to MriduManda")
    print("Fetching city...")
    city = get_city()
    path_to_api = os.path.join(os.path.expanduser("~"), ".mridumanda", "api.txt")
    api = None
    
    with open (path_to_api, "r") as file:
        line = file.readline()
        
        if ":" in line:
            key, value = line.strip().split(":", 1)
            api = value
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"
    response = requests.get(url)
    
    time.sleep(1)
    os.system('clear')
    
    if response.status_code == 200:
        weather_data = response.json()
        print(f"City \t\t : {city.title()}")
        print(f"Weather \t : {weather_data['weather'][0]['description'].title()}")
        print(f"Temperature \t : {weather_data['main']['temp']}°C")
        print(f"Feels like \t : {weather_data['main']['feels_like']}°C")
        print(f"Humidity \t : {weather_data['main']['humidity']}%")
        
    else:
        print("Error:", response.status_code)
        
def get_city():
    ipinfo_data = requests.get("https://www.ipinfo.io/json")
    city = ipinfo_data.json().get('city')
    
    return city
