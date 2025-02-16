from src.config.config import Config
from src.models.firebase import Firebase
from datetime import datetime

class DataCollection:

    def __init__():
        pass

    @staticmethod
    def save_disease_prediction(img, prediction, disease):

        prediction_type = 'disease-prediction'
        img_url = Firebase.upload_image(img)
        prediction_info = {"image": img_url, "prediction": prediction, "disease":disease}
        farm_info = Firebase.get_farm_info(Config.AUTH_TOKEN)

        if "error" in farm_info:
            Firebase.add_prediction(prediction_info, prediction_type)
            return {'saved': 'farm not found'}
        
        prediction_info.update(farm_info)
        Firebase.add_prediction(prediction_info, prediction_type)
        return {'saved': 'farm found'}
    
    @staticmethod
    def save_market_prediction(area, item, prediction):

        prediction_type = 'market-prediction'
        curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prediction_info = {"area": area, "crop": item, "datetime": curr_datetime, "prediction": prediction}
        farm_info = Firebase.get_farm_info(Config.AUTH_TOKEN)

        if "error" in farm_info:
            Firebase.add_prediction(prediction_info, prediction_type)
            return {'saved': 'farm not found'}
        
        prediction_info.update(farm_info)
        Firebase.add_prediction(prediction_info, prediction_type)
        return {'saved': 'farm found'}