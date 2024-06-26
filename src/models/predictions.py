import numpy as np
import os
import requests
import requests
import datetime
import pandas as pd 
from src import HF_TOKEN
from src.models.utils import API

crop_yields_data = os.path.dirname(__file__) + "/ml_models/crops_dataset/crop_yields_dataset.csv"


max_length = 100

DISEASE_MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/muAtarist/maize_disease_model"
MARKET_MODEL_ENDPOINT = "https://predict-kasxmzorbq-od.a.run.app/predict"

HEADERS = {"Authorization": "Bearer " + HF_TOKEN}

YEAR = datetime.date.today().year

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

        if probability < 0.6 and label.lower() in ["nofoliarsymptoms","unidentifieddisease"]:
            return API.identify([filename])
        
        # Format the string with the label and probability
        output = {"model": "disease prediction", "disease_probability": f"{probability:.3f}", "crop": "maize", "recommendations": []}
        # result = f"With {probability:.3f} probability, the disease is {label}."
        return output
    

    @staticmethod
    def market_prediction(request_data):
        average_temp_year, average_precip_year = API.get_yearly_weather_data(YEAR, request_data["area"])

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

        # if prediction > mean_yield - (0.75 * mean_yield):
        #     demand_prediction = 'LOW'
        # else:
        #     demand_prediction = 'HIGH'

        output = {"model": "market prediction", "supply_prediction": prediction, "average_supply": mean_yield, "threshold": 75, "crop": predicted_crop, "country": data["Area"]}
        # output = f"Demand for {predicted_crop} is likely going to be {demand_prediction} since supply prediction is {prediction} and past mean yield is {mean_yield}. [Assumption: Demand and supply are inversely proportional]"
        return output