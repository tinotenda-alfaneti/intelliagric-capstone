import requests
from SECRET import HF_TOKEN

API_URL = "https://api-inference.huggingface.co/models/muAtarist/maize_disease_model"
headers = {"Authorization": "Bearer " + HF_TOKEN}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data).json()
    highest_prob = max(response, key=lambda x: x['score'])
    
    # Extract the label and score
    label = highest_prob['label']
    probability = highest_prob['score']
    
    # Format the string with the label and probability
    result = f"With {probability:.3f} probability, the disease is {label}."
    return result

output = query("images/example.jpg")
print(output)