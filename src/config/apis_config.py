import os
from dotenv import load_dotenv
import openai

# load private keys from dotenv
load_dotenv('.env')
INFOBIP_KEY=os.getenv('INFOBIP_KEY')
INFOBIP_BASE_URL=os.getenv('INFOBIP_BASE_URL')
EMAIL_BOUNDARY=os.getenv('EMAIL_BOUNDARY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


client = openai.OpenAI(api_key=OPENAI_API_KEY)
