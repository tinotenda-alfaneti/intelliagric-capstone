import base64
import json
from pathlib import Path
from SECRET import API_KEY

import requests

BASE_DIR = Path(__file__).parent

# encode image to base64, API needs this
def encode_file(file_name):
    with open(file_name, "rb") as file:
        return base64.b64encode(file.read()).decode("ascii")


# crop disease prediction - identify the crop then the insect
# lat, lon: geographic coordinate, increases the identification accuracy
def identify(file_names, lat, lon):
   
    payload = {
        "images": [encode_file(img) for img in file_names],
        "latitude": lat,
        "longitude": lon,
        "similar_images": True,
    }

    params = {
        "details": "common_names,gbif_id,eppo_code,type",
    }
    headers = {
        "Content-Type": "application/json",
        "Api-Key": API_KEY,
    }

    response = requests.post(
        "https://crop.kindwise.com/api/v1/identification", # API url
        params=params,
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201, f"{response.status_code}: {response.text}"
    return response.json()


if __name__ == "__main__":

    identification = identify(
        [
            BASE_DIR / "images" / "example.jpg",
        ],
        lat=49.1951239,
        lon=16.6077111
    )

    print(json.dumps(identification, indent=4))
    
    for suggestion in identification['result']['crop']['suggestions']:
        print(suggestion["probability"], suggestion['name'])
        
    print()

    for suggestion in identification['result']['disease']['suggestions']:
        print(suggestion["probability"], suggestion['name'])