from src import web_api
import json
import numpy as np
from flask import request
from src.models.predictions import Predict
from src.models.predictions import soil_label_dict, crop_label_name_dict


'''
Example of input data:
{
    "N":"90",
    "P":"69",
    "K":"90",
    "temperature":"20.879744",
    "humidity":"2.002744",
    "ph":"6.502985",
    "rainfall":"202.935536"
}
'''
@web_api.route("/predict_crop", methods=["GET", "POST"])
def predictcrop():
    try:
        if request.method == "POST":
            form_values = json.loads(request.data)
            column_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
            input_data = np.asarray([float(form_values[key].strip()) for key in form_values]).reshape(
                1, -1
            )
            
            prediction_data = Predict.crop_prediction(input_data)
            json_obj = json.dumps(prediction_data, default=Predict.convert)
            return json_obj
    except:
        return json.dumps({"error":"Please Enter Valid Data"}, default=Predict.convert)

'''
Example of input data:
{
    "Temparature":"34",
    "Humidity":"65",
    "Moisture":"62",
    "soil_type":"Black",
    "crop_type":"Cotton",
    "Nitrogen":"7",
    "Potassium":"9",
    "Phosphorous":"30"
}
'''
@web_api.route("/predict_fertilizer", methods=["GET", "POST"])
def predictfertilizer():
    try:
        if request.method == "POST":
            form_values = json.loads(request.data)
            column_names = [
                "Temparature",
                "Humidity",
                "Moisture",
                "soil_type",
                "crop_type",
                "Nitrogen",
                "Potassium",
                "Phosphorous",
            ]

            for key in form_values:
                form_values[key] = form_values[key].strip()

            form_values["soil_type"] = soil_label_dict[form_values["soil_type"]]
            form_values["crop_type"] = crop_label_name_dict[form_values["crop_type"]]
            # print(form_values)
            input_data = np.asarray([float(str(form_values[key]).strip()) for key in form_values]).reshape(
                1, -1
            )
            print(input_data)
            prediction_data = Predict.fertilizer_prediction(input_data)
            json_obj = json.dumps(prediction_data, default=Predict.convert)
            return json_obj
    except:
        return json.dumps({"error":"Please Enter Valid Data"}, default=Predict.convert)
