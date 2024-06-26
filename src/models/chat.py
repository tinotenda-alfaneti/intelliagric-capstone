from src import client, database, web_api
from src.models.utils import INITIAL_STAGE_PROMPT
import json

REFINING_PROMPT = """
            You are an assistant named IntelliAgric for an African agriculture farmer. A user has asked a question, and a specialized model for either maize disease prediction or agriculture market prediction has provided the following data. Your task is to analyze and refine the response to be clear and helpful, provide recommendations, and ensure it fits naturally into the ongoing conversation. Your responses should be geared towards Africa and easy to understand. Break down all complex ideas and concepts. The responses should not just be informative but also include recommendations and practical solutions.

            Examples:

            User: If I plant maize today, will it be profitable after harvesting?
            Model Data: Demand will be high and supply will be high for maize.
            Refined Response: According to our prediction, the demand for maize will be high, making it potentially profitable to plant maize today. However, with high supply, market competition might also be strong. Watch out for diseases like gray leaf spot, as conditions will be favorable for it. Is there anything else you would like to know about market prices?

            User: My maize plants have yellow spots. What should I do?
            Model Data: The plants are more likely affected by maize leaf blight.
            Refined Response: Your maize plants are likely affected by maize leaf blight. It's recommended to apply a fungicide such as [Fungicide Name] commonly available in Africa. Ensure you follow the application instructions carefully. Please let me know if you need further assistance.

            User: Is it a good time to invest in farming?
            Model Data: The market is favorable for investing in certain crops.
            Refined Response: The current market conditions are favorable for investing in certain crops. To provide specific advice, could you please tell me which crop you are considering for your investment?

            User: I have noticed irregular patterns on my maize leaves. What should I do?
            Model Data: The symptoms indicate a potential fungal infection.
            Refined Response: The irregular patterns on your maize leaves may indicate a fungal infection. It is advisable to upload an image of the affected leaves so I can provide a more accurate diagnosis. In the meantime, ensure your maize field has good air circulation and consider applying a fungicide.

            By following these guidelines, you can provide clear, actionable, and helpful responses that fit naturally into the ongoing conversation.

        """

CHAT_PROMPT = [
            {
                "role": "system",
                "content": INITIAL_STAGE_PROMPT
            }
        ]

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 150

class Chat:

    def __init__():
        pass

    @staticmethod
    def get_intent_and_response(conversations):
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversations,
            temperature=0,
            max_tokens=MAX_TOKENS
        )
        
        return response.choices[0].message.content

    @staticmethod
    def refine_response(user_input, model_data):
        prompt = f"""
        
        User: {user_input}
        Model Data: {model_data}
        Refined Response:
        """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content
    
    @staticmethod
    def soil_analysis(data):

        prompt = f"""
                Based on the following soil data, provide an analysis and recommendations for a small-scale farmer in Africa.

                Soil Data:
                - Moisture: {data.get('mois')}
                - NPK (Nitrogen, Phosphorus, Potassium): {data.get('npk')}
                - Temperature: {data.get('temp')}
                - pH: {data.get('ph')}

                Your task is to analyze this data and offer practical, easy-to-understand advice. Make sure your recommendations are specific to small-scale farmers in Africa. Break down any complex ideas and provide actionable steps that the farmer can take to improve their soil health and crop yield.

                Examples:

                1. If the moisture level is low:
                "The soil moisture level is currently low. It is important to implement irrigation practices such as drip irrigation to maintain adequate moisture levels. Mulching can also help retain soil moisture."

                2. If the NPK levels are imbalanced:
                "The NPK levels indicate that the soil is deficient in Nitrogen but has sufficient Phosphorus and Potassium. Consider using a Nitrogen-rich fertilizer, such as urea or composted manure, to boost Nitrogen levels. Rotate crops with legumes like beans or peas, which fix Nitrogen in the soil."

                3. If the temperature is too high:
                "The current soil temperature is quite high, which can stress the crops. Planting shade-tolerant crops or using shade nets can help protect the plants. Mulching can also help to moderate soil temperature."

                4. If the pH level is too low (acidic):
                "The soil pH is too low, making it acidic. To raise the pH to a more neutral level, consider applying agricultural lime (calcium carbonate). Regularly test the soil to monitor changes in pH."

                5. If the pH level is too high (alkaline):
                "The soil pH is too high, making it alkaline. To lower the pH, you can apply sulfur or gypsum. Adding organic matter such as compost can also help balance the pH over time."

                Make sure to provide recommendations that are easy to implement and cost-effective for small-scale farmers. Encourage sustainable practices that improve soil health over the long term.

            """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content
    
    @staticmethod
    def save_chat(message):

        try:
            db = database.collection(f'history-{web_api.config["AUTH_TOKEN"]}')

            db.add(message)

            print(f'Document added with ID: {db[1].id}')
        
            return json.dumps({"Success":"Data Added Successfully"})
        except:
            return json.dumps({"error":"Please Enter Valid Data"}, default=TypeError)