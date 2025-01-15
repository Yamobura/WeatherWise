import urllib.request
import base64
import json
import requests
import openai
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Укажите источник фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API keys
openai.api_key = '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'
WEATHER_API_KEY = 'c4926db13750fa4cb3bdb6c84f4153f5'

# Stable Diffusion settings
webui_server_url = 'http://127.0.0.1:7860'
out_dir = 'api_out'

# Получение погоды по городу или координатам
@app.get("/weather")

def get_weather_overview(
    city: str = Query(None),  # Название города (если передано)
    lat: float = Query(None),  # Широта (если передана)
    lon: float = Query(None)   # Долгота (если передана)
):
    """
    Универсальный маршрут для обработки погоды:
    - Если передано `city`, ищем координаты через Geocoding API.
    - Если переданы `lat` и `lon`, определяем название города через Reverse Geocoding API.
    - Используем координаты для вызова One Call API.
    """
    # Проверяем, что переданы либо city, либо координаты
    if not city and (lat is None or lon is None):
        raise HTTPException(
            status_code=400,
            detail="Передайте либо название города (city), либо координаты (lat и lon)."
        )

    # Если передано название города, ищем координаты через Geocoding API
    if city:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
        geo_response = requests.get(geo_url)
        if geo_response.status_code != 200 or not geo_response.json():
            raise HTTPException(status_code=404, detail="Город не найден.")
        geo_data = geo_response.json()[0]
        lat, lon = geo_data["lat"], geo_data["lon"]

    # Если переданы координаты, определяем название города через Reverse Geocoding API
    elif lat is not None and lon is not None:
        reverse_geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={WEATHER_API_KEY}"
        reverse_geo_response = requests.get(reverse_geo_url)
        if reverse_geo_response.status_code != 200 or not reverse_geo_response.json():
            raise HTTPException(status_code=404, detail="Не удалось определить название города по координатам.")
        reverse_geo_data = reverse_geo_response.json()[0]
        city = reverse_geo_data["name"]+", "+reverse_geo_data["country"]

    # Вызываем One Call Overview API для получения сводки погоды
    overview_url = f"https://api.openweathermap.org/data/3.0/onecall/overview?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    overview_response = requests.get(overview_url)
    if overview_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Ошибка при вызове One Call API.")
    overview_data = overview_response.json().get("weather_overview")
    location_date = overview_response.json().get("date")

    user_input = f"Make a prompt for Stable Diffusion which describes outfit suggestion for these location and weather: {city}, {overview_data}"

    # Запрос к OpenAI Chat API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Или "gpt-3.5-turbo", если у вас нет доступа к gpt-4
            messages=[
                {"role": "system", "content": "You are an assistant that generates creative outfit suggestions based on weather data."},
                {"role": "user", "content": user_input},
            ],
        )

        chatgptprompt = response['choices'][0]['message']['content']
        base64_str = call_txt2img_api(chatgptprompt)

        # Возвращаем сгенерированный текст
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "date": location_date,
            "overview": overview_data,
            " ": chatgptprompt,
            "image": base64_str
        }
    
    except Exception as e:
        return f"Error generating prompt: {e}"
    


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))

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
        "prompt": generated_prompt,  # Используем сгенерированный промпт
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

    # Вызов API для генерации изображения
    response = call_api('sdapi/v1/txt2img', **payload)
    
    # Получаем изображения из ответа
    images = response.get('images', [])
    
    # Если изображения есть, конвертируем в Base64 и возвращаем
    images = response.get("images", [])
    if images:
        # Декодируем первое изображение
        image_base64 = images[0]
        return image_base64
    else:
        raise HTTPException(status_code=500, detail="Stable Diffusion не сгенерировал изображение.")

