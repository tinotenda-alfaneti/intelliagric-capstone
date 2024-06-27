import os
import requests
import requests
import datetime
from src import HF_TOKEN
from src import WEATHER_API_KEY
import base64
from src import KINDWISE_API_KEY

crop_yields_data = os.path.dirname(__file__) + "/ml_models/crops_dataset/crop_yields_dataset.csv"

max_length = 100

DISEASE_MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/muAtarist/maize_disease_model"
MARKET_MODEL_ENDPOINT = "https://predict-kasxmzorbq-od.a.run.app/predict"

HEADERS = {"Authorization": "Bearer " + HF_TOKEN}

YEAR = datetime.date.today().year

# encode image to base64, API needs this
def encode_file(file_name):
    with open(file_name, "rb") as file:
        return base64.b64encode(file.read()).decode("ascii")
    
def encode_file_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("ascii")
    else:
        raise Exception("Failed to download image")

class API:

    def __init__():
        pass

    @staticmethod
    def get_yearly_weather_data(year, area):
        lon, lat = API.get_country_coordinates(area)

        base_url = f'https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}'
        start_date = datetime.date(year, 6, 1)
        end_date = datetime.date(year, 6, 5)
        delta = datetime.timedelta(days=1)
        current_date = start_date
        daily_temps = []
        daily_precip = []

        while current_date <= end_date:
            formatted_date = current_date.strftime("%Y-%m-%d")
            url = f"{base_url}&date={formatted_date}&appid={WEATHER_API_KEY}"
            response = requests.get(url)
            data = response.json()

            try:
                min_temp_fahrenheit = data["temperature"]["min"]
                max_temp_fahrenheit = data["temperature"]["max"]
                precip = data["precipitation"]["total"] * 24

                # Convert temperatures to Celsius
                min_temp_celsius = min_temp_fahrenheit - 273.15
                max_temp_celsius = max_temp_fahrenheit - 273.15
                average_temp_celsius = (min_temp_celsius + max_temp_celsius) / 2

                daily_temps.append(average_temp_celsius)
                if precip is not None and isinstance(precip, (int, float)) and precip >= 0:
                    daily_precip.append(precip)

            except (KeyError, TypeError, ValueError) as e:
                print(f"Skipping data for {formatted_date} due to error: {e}")
            current_date += delta

        # Calculate the average temperature and precipitation for the year
        if daily_temps and daily_precip:
            average_temp_year = sum(daily_temps) / len(daily_temps)
            average_precip_year = sum(daily_precip) / len(daily_precip)
        else:
            average_temp_year = None
            average_precip_year = None
        
        if average_temp_year is not None and average_precip_year is not None:
            print(f"Average Temperature for the year: {average_temp_year:.2f} °C")
            print(f"Average Precipitation for the year: {average_precip_year:.2f} mm")
        else:
            print("No valid data available for the year.")

        return average_temp_year, average_precip_year

    
    @staticmethod
    def get_country_coordinates(country_name):
        # Construct the URL for the weather API
        url = f'https://api.openweathermap.org/data/2.5/weather?q={country_name}&appid={WEATHER_API_KEY}'
        
        response = requests.get(url)
        data = response.json()
        
        # Extract the coordinates
        try:
            lon = data['coord']['lon']
            lat = data['coord']['lat']
            return lon, lat
        except KeyError:
            print("Error: Unable to retrieve coordinates for the specified country.")
            return None, None
        
    @staticmethod
    def fetch_weather_data(country):
        weather_api_url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': country,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(weather_api_url, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data['weather'][0]['description']
        else:
            return 'Weather data not available' 

    @staticmethod
    def identify(file_names, flag=1):

        if flag == 0:
            images = [encode_file_url(img) for img in file_names]
        else:
            images = [encode_file(img) for img in file_names]
   
        payload = {
            "images": images,
            "similar_images": True,
            #TODO: add lat and lon coordinates here
            # "latitude": lat,
            # "longitude": lon,
        }

        params = {
            "details": "common_names,gbif_id,eppo_code,type",
        }
        headers = {
            "Content-Type": "application/json",
            "Api-Key": KINDWISE_API_KEY,
        }

        response = requests.post(
            "https://crop.kindwise.com/api/v1/identification", # API url
            params=params,
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201, f"{response.status_code}: {response.text}"
        return response.json()