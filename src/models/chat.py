from src.models.prompts import CHATTING_PROMPT_V1, REFINING_PROMPT_V1, ANALYSING_PROMPT_V0, FARM_OVERVIEW_PROMPT_V0
from src.config.apis_config import client

CHAT_PROMPT = [
            {
                "role": "system",
                "content": CHATTING_PROMPT_V1
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
        
        ###Instructions
        {REFINING_PROMPT_V1}
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

                {ANALYSING_PROMPT_V0}  
            """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content
        
    @staticmethod
    def farm_overview(farm_info):

        prompt = f"""
                Based on the following farm information, provide an analysis, insights and recommendations for a small-scale farmer in Africa.

                Farm Information: {farm_info}

                {FARM_OVERVIEW_PROMPT_V0}

            """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content
        