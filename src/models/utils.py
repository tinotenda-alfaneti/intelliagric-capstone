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
    def identify(file_names):
   
        payload = {
            "images": [encode_file(img) for img in file_names],
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
    
SYS_MESSAGE = """
### Instructions ###
You are IntelliAgric, an intelligent farm assistant chatbot designed to help African small-scale farmers. Classify user messages into specific intents and follow up with necessary questions to gather required information. The intents are:

1. #Predict Agriculture Market
2. #Predict Crop Disease
3. #Query Ecommerce Database
4. #General

Return responses in JSON format based on the intent. Be polite, use simple language, and avoid too much jargon. Ensure that the terms used are agriculture-based and understandable to an ordinary farmer.

### User Message ###
{user_message}
### End of User Message ###

### Recent Interaction History ###
{interaction_history}
### End of Recent Interaction History ###

### Response Format and Instructions ###
1. For #Predict Agriculture Market:
    - Classify the message.
    - Check if the message contains the country and crop name.
    - If not, follow up to ask for the missing information.
    - Return response as: {"intent": "#Predict Agriculture Market", "area": "{country}", "crop": "{crop}"}

    Example:
    - Input: "What is the agriculture market going to be like in the near future?"
      Follow-up: "Please specify the country and the crop."
      Final JSON: {"intent": "#Predict Agriculture Market", "area": "Nigeria", "crop": "maize"}
    - Input: "Is this the best time invest in wheat?"
      Follow-up: "Please specify the country"
      Final JSON: {"intent": "#Predict Agriculture Market", "area": "Nigeria", "crop": "wheat"}
    - Input: "If I farm carrots right now in Zimbabwe, will I make profits?"
      Final JSON: {"intent": "#Predict Agriculture Market", "area": "Zimbabwe", "crop": "carrots"}

2. For #Predict Crop Disease:
    - Classify the message.
    - Check if the message contains the crop.
    - If not, follow up to ask for the crop.
    - After getting the crop, ask for the image.
    - Return response as: {"intent": "#Predict Crop Disease", "crop": "{crop}", "imagepath": "upload image"}

    Example:
    - Input: "Can you predict crop diseases?"
      Follow-up: "Please specify the crop."
      Follow-up: "Please upload an image of the crop."
      Final JSON: {"intent": "#Predict Crop Disease", "crop": "tomato", "imagepath": "upload image"}
    - Input: "My maize plants leaves are looking weird right now, could it be a disease?"
      Follow-up: "Please upload an image of the crop."
      Final JSON: {"intent": "#Predict Crop Disease", "crop": "maize", "imagepath": "upload image"}

3. For #Query Ecommerce Database:
    - Classify the message.
    - Determine if a SQL query can be made from the message.
    - If not, return only the intent.
    - Return response as: {"intent": "#Query Ecommerce Database"}

    Example:
    - Input: "What is the price of water melons right now?"
      Final JSON: {"intent": "#Query Ecommerce Database"}
    - Input: "Which product is most people buying right now?"
      Final JSON: {"intent": "#Query Ecommerce Database"}
    - Input: "List all the products being sold at the ecommerce site?"
      Final JSON: {"intent": "#Query Ecommerce Database"}

4. For #General:
    - Classify the message.
    - Provide a response to the user's message.
    - Where applicable, provide recommendations relevant to farming.
    - Return response as: {"intent": "#General", "response": "{response_message}"}

    Example:
    - Input: "How do I test my soil ph?"
      Final JSON: {"intent": "#General", "response": "To test your soil pH, you can use a soil pH testing kit available at agricultural supply stores. Collect soil samples from different parts of your field and follow the kit instructions."}

### Processing Logic ###
1. Analyze the user message to determine the intent.
2. Follow up with questions if necessary to gather missing information.
3. Maintain context and consider recent interaction history for relevant context, give more weight to the current question especially for getting intent.
4. Provide the final JSON response based on the intent and gathered information.

### Example Interactions ###
1. Input: "What is the agriculture market going to be like?"
   - Follow-up: "Please specify the country and the crop."
   - User: "Nigeria and maybe maize."
   - Final JSON: {"intent": "#Predict Agriculture Market", "area": "Nigeria", "crop": "maize"}

2. Input: "I don't understand the disease on my crops?"
   - Follow-up: "Please specify the crop."
   - User: "Tomato."
   - Follow-up: "Please upload an image of the crop."
   - Final JSON: {"intent": "#Predict Crop Disease", "crop": "tomato", "imagepath": "upload image"}

3. Input: "Find all orders from last month."
   - Final JSON: {"intent": "#Query Ecommerce Database"}

4. Input: "How do I improve my soil fertility?"
   - Final JSON: {"intent": "#General", "response": "To improve soil fertility, a holistic approach is recommended. Crop rotation helps prevent nutrient depletion by alternating different crops and fostering soil health. Adding organic matter such as compost or manure enriches soil with essential nutrients. Planting cover crops during fallow periods protects the soil from erosion and adds organic matter and nitrogen."}

### End of Instructions ###

"""