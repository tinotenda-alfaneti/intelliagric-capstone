import joblib
import numpy as np
import os
import tensorflow
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel

#TODO: INSTEAD OF USING THESE DUMMY MODELS, LOAD REAL ENDPOINTS OR SAVE REAL MODELS
# Load the fine-tuned model
model = TFGPT2LMHeadModel.from_pretrained(os.path.dirname(__file__) + "/fine-tuned-gpt2")

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")

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

class Predict:

    def __init__():
        pass

    @staticmethod
    def convert(o):
        if isinstance(o, np.generic):
            return o.item()
        raise TypeError

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

        print(all_probs)

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
    
    @staticmethod
    def generate_answer(prompt):
        # Encode the prompt
        input_ids = tokenizer.encode(prompt, return_tensors="tf")

        # Generate text using the model
        output = model.generate(
            input_ids=input_ids,
            max_length=max_length,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
        )

        # Decode the generated text
        generated_text = tokenizer.decode(output[0])

        return generated_text