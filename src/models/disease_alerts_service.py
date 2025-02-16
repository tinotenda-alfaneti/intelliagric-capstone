from src.config.db_config import database
from src.models.notification_service import Notifications

class DiseaseAlerts:
    
    @staticmethod
    def check_disease_predictions():
        predictions_ref = database.collection('disease-predictions')
        farms_ref = database.collection('farms')

        predictions_docs = predictions_ref.stream()
        farm_docs = farms_ref.stream()

        predictions = [doc.to_dict() for doc in predictions_docs]
        farms = {doc.id: doc.to_dict() for doc in farm_docs}

        disease_counts = {}
        for prediction in predictions:
            disease = prediction['disease']
            farm_id = prediction['farm_id']
            location = farms[farm_id]['location']

            if disease not in disease_counts:
                disease_counts[disease] = {}
            if location not in disease_counts[disease]:
                disease_counts[disease][location] = 0
            
            disease_counts[disease][location] += 1

        alerts = []
        for disease, locations in disease_counts.items():
            for location, count in locations.items():
                if count >= 5:
                    alerts.append({'disease': disease, 'location': location})

        Notifications.send_notifications(alerts, farms)
