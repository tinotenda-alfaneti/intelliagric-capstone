import joblib
import numpy as np
import os
import requests
import requests
import datetime
import pandas as pd 
from src import HF_TOKEN
from src import WEATHER_API_KEY

crop_yields_data = os.path.dirname(__file__) + "/ml_models/crops_dataset/crop_yields_dataset.csv"


max_length = 100

DISEASE_MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/muAtarist/maize_disease_model"
MARKET_MODEL_ENDPOINT = "https://predict-kasxmzorbq-od.a.run.app/predict"

HEADERS = {"Authorization": "Bearer " + HF_TOKEN}

YEAR = datetime.date.today().year

def _get_country_coordinates(country_name):
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

def _get_yearly_weather_data(year, area):
    lon, lat = _get_country_coordinates(area)

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
        # print(data)

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

class Predict:

    def __init__():
        pass

    @staticmethod
    def convert(o):
        if isinstance(o, np.generic):
            return o.item()
        raise TypeError
    
    @staticmethod
    def maize_disease_prediction(filename):
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(DISEASE_MODEL_ENDPOINT, headers=HEADERS, data=data).json()
        try:
            highest_prob = max(response, key=lambda x: x['score'])
        except Exception as e:
            print(f"Failed to get prediction. Error: {e}")
            return f"Failed to get prediction. Error: {e}"
        
        # Extract the label and score
        label = highest_prob['label']
        probability = highest_prob['score']
        
        # Format the string with the label and probability
        result = f"With {probability:.3f} probability, the disease is {label}."
        return result
    

    @staticmethod
    def market_prediction(request_data):
        average_temp_year, average_precip_year = _get_yearly_weather_data(YEAR, request_data["area"])

        data = {
            "Area": request_data["area"],
            "Item": request_data["item"],
            "average_rain_fall_mm_per_year": average_precip_year,
            "avg_temp": average_temp_year
        }

        print("Average Temp:", data['avg_temp'])
        print("Average Precip:", data["average_rain_fall_mm_per_year"])

        dataset = pd.read_csv(crop_yields_data)

        try:
            response = requests.post(MARKET_MODEL_ENDPOINT, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get prediction. Error: {e}")
            return

        prediction = response.json().get('prediction', None)
        if prediction is None:
            print("Prediction key not found in the response")
            return

        print(f"Prediction: {prediction}")

        df = pd.DataFrame(dataset)
        result = df.groupby(['Item'])['hg/ha_yield'].agg(['mean', 'min', 'max']).reset_index()

        predicted_crop = data['Item']
        mean_yield = result[result['Item'] == predicted_crop]['mean'].values[0]

        if prediction > mean_yield - (0.75 * mean_yield):
            demand_prediction = 'LOW'
        else:
            demand_prediction = 'HIGH'

        return f"Demand for {predicted_crop} is likely going to be {demand_prediction} since supply prediction is {prediction} and past mean yield is {mean_yield}. [Assumption: Demand and supply are inversely proportional]"