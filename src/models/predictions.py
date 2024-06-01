import joblib
import numpy as np
import os
import requests
from src import HF_TOKEN

#TODO: INSTEAD OF USING THESE DUMMY MODELS, LOAD REAL ENDPOINTS OR SAVE REAL MODELS


#TODO: Clean up the path to models looks messy right now

# Loading all Crop Recommendation Models
crop_rf_pipeline = joblib.load(os.path.dirname(__file__) + "/ml_models/crop_recommendation/rf_pipeline.pkl")
crop_knn_pipeline = joblib.load(os.path.dirname(__file__) + "/ml_models/crop_recommendation/knn_pipeline.pkl")
crop_label_dict = joblib.load(os.path.dirname(__file__) + "/ml_models/crop_recommendation/label_dictionary.pkl")


# Loading all Fertilizer Recommendation Models
fertilizer_rf_pipeline = joblib.load(os.path.dirname(__file__) + "/ml_models/fertilizer_recommendation/rf_pipeline.pkl")
fertilizer_svm_pipeline = joblib.load(os.path.dirname(__file__) + "/ml_models/fertilizer_recommendation/svm_pipeline.pkl")
fertilizer_label_dict = joblib.load(os.path.dirname(__file__) + "/ml_models/fertilizer_recommendation/fertname_dict.pkl")
soiltype_label_dict = joblib.load(os.path.dirname(__file__) + "/ml_models/fertilizer_recommendation/soiltype_dict.pkl")
croptype_label_dict = joblib.load(os.path.dirname(__file__) + "/ml_models/fertilizer_recommendation/croptype_dict.pkl")

max_length = 100

crop_label_name_dict = {}
for crop_value in croptype_label_dict:
    crop_label_name_dict[croptype_label_dict[crop_value]] = crop_value

soil_label_dict = {}
for soil_value in soiltype_label_dict:
    soil_label_dict[soiltype_label_dict[soil_value]] = soil_value

DISEASE_MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/muAtarist/maize_disease_model"
MARKET_PREDICTION_ENDPOINT = "https://predict-kasxmzorbq-od.a.run.app/predict"

HEADERS = {"Authorization": "Bearer " + HF_TOKEN}

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
        highest_prob = max(response, key=lambda x: x['score'])
        
        # Extract the label and score
        label = highest_prob['label']
        probability = highest_prob['score']
        
        # Format the string with the label and probability
        result = f"With {probability:.3f} probability, the disease is {label}."
        return result
    
    @staticmethod
    def market_prediction(request_data):

        response = requests.post(url=MARKET_PREDICTION_ENDPOINT, data=request_data).json()

        #TODO: The model should give the actual response or the mean crop value instead of us calculating from scratch again
        if response['prediction'] > 10000:
            return "Supply of will be high, therefore demand is likely going to be low and the prices will be lower."
        elif response['prediction'] < 10000:
            return "Supply will be low, therefore demand is likely going to be high and the prices will be higher."
        else:
            return "Supply and demand are likely to be equal and the prices will be the same."



    @staticmethod
    def crop_prediction(input_data):
        prediction_data = {
            "rf_model_prediction": crop_label_dict[crop_rf_pipeline.predict(input_data)[0]],
            "rf_model_probability": max(crop_rf_pipeline.predict_proba(input_data)[0])
            * 100,
            "knn_model_prediction": crop_label_dict[
                crop_knn_pipeline.predict(input_data)[0]
            ],
            "knn_model_probability": max(crop_knn_pipeline.predict_proba(input_data)[0])
            * 100,
        }

        all_predictions = [
                prediction_data["rf_model_prediction"],
                prediction_data["knn_model_prediction"],
            ]
        
        

        all_probs = [
                prediction_data["rf_model_probability"],
                prediction_data["knn_model_probability"],
            ]

        if len(set(all_predictions)) == len(all_predictions):
            prediction_data["final_prediction"] = all_predictions[all_probs.index(max(all_probs))]
        else:
            prediction_data["final_prediction"] = max(set(all_predictions), key=all_predictions.count)

        
        return prediction_data

    @staticmethod
    def fertilizer_prediction(input_data):
        prediction_data = {
            "rf_model_prediction": fertilizer_label_dict[
                fertilizer_rf_pipeline.predict(input_data)[0]
            ],
            "rf_model_probability": max(fertilizer_rf_pipeline.predict_proba(input_data)[0])
            * 100,
            "svm_model_prediction": fertilizer_label_dict[
                fertilizer_svm_pipeline.predict(input_data)[0]
            ],
            "svm_model_probability": max(
                fertilizer_svm_pipeline.predict_proba(input_data)[0]
            )
            * 100,
        }

        all_predictions = [
                prediction_data["rf_model_prediction"],
                prediction_data["svm_model_prediction"],
            ]

        all_probs = [
                prediction_data["rf_model_probability"],
                prediction_data["svm_model_probability"],
            ]

        if len(set(all_predictions)) == len(all_predictions):
            prediction_data["final_prediction"] = all_predictions[all_probs.index(max(all_probs))]
        else:
            prediction_data["final_prediction"] = max(set(all_predictions), key=all_predictions.count)

        return prediction_data