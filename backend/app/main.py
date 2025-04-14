import urllib.request
import json
import requests
import openai
from typing import Dict
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], #frontend host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_data: Dict[str, Dict] = {}

# API keys
openai.api_key = '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'
WEATHER_API_KEY = 'c4926db13750fa4cb3bdb6c84f4153f5'

# Stable Diffusion settings
webui_server_url = 'http://127.0.0.1:7860'
out_dir = 'api_out'

@app.get("/weather")
def get_weather_overview(
    city: str = Query(None),  
    lat: float = Query(None),  
    lon: float = Query(None)   
):
    """
    Exctract weather data from Openweathermap
    """
    # Check location prompt
    if not city and (lat is None or lon is None):
        raise HTTPException(
            status_code=400,
            detail="Prompt city name or coordinates."
        )

    if city:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        if geo_response.status_code != 200 or not geo_response.json():
            raise HTTPException(status_code=404, detail="Город не найден.")
        geo_data = geo_response.json()[0]
        lat, lon = geo_data["lat"], geo_data["lon"]

    # Find city name by coordinates with Reverse Geocoding API
    elif lat is not None and lon is not None:
        reverse_geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={WEATHER_API_KEY}"
        reverse_geo_response = requests.get(reverse_geo_url)
        if reverse_geo_response.status_code != 200 or not reverse_geo_response.json():
            raise HTTPException(status_code=404, detail="Could not retrieve city by coordinates.")
        reverse_geo_data = reverse_geo_response.json()[0]
        city = reverse_geo_data["name"]+", "+reverse_geo_data["country"]

    # Call One Call Overview API to get weather overview
    overview_url = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    overview_response = requests.get(overview_url)
    if overview_response.status_code != 200:
        raise HTTPException(status_code=500, detail="One Call API call error.")
    overview_data = overview_response.json().get("weather_overview")
    location_date = overview_response.json().get("date")

    return {
        "city": city,
        "date": location_date,
        "overview": overview_data
        }
   
@app.get("/chatgpt")
def generate_prompt(city: str, overview_data: str):
    """
    Generate a promt for Stable diffusion with Chat GPT
    """
    user_input = f"{city}, {overview_data} Describe an outfit suitable for a woman with this location and weather data to create a prompt for Stable Diffusion. Only precise description of the outfit items, no additional explanations. Also consider if there are any dressing cultural rules in this region."

    # Call OpenAI Chat API
    try:
        client = OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that generates creative outfit suggestions based on weather data."},
                {"role": "user", "content": user_input},
            ],
        )

        chatgptprompt = response.choices[0].message.content
        return {"chatgptprompt": chatgptprompt}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации текста: {e}")

@app.get("/imagegeneration")
def generate_image(chatgptprompt: str):
    """
    Image generation with Stable Diffusion API
    """

    # Вызов API Stable Diffusion
    try:
        base64_image = call_txt2img_api(chatgptprompt)
        return {"generatedimage": base64_image}
    
    except Exception as e:
        return f"Error generating prompt: {e}"

def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))

def call_txt2img_api(generated_prompt):
    payload = {
        "prompt": generated_prompt, 
        "negative_prompt": "",
        "seed": 1,
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "sampler_name": "DPM++ 2M",
        "n_iter": 1,
        "batch_size": 1,
    }

    # API call for image creating
    response = call_api('sdapi/v1/txt2img', **payload)

    images = response.get("images", [])
    if images:
        image_base64 = images[0]
        return image_base64
    else:
        raise HTTPException(status_code=500, detail="Error with image generation.")

