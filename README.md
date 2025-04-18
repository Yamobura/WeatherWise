# WeatherWise

WeatherWise is a web application that provides weather-appropriate outfit suggestions based on current weather conditions. It combines weather data with AI-powered outfit recommendations and generates visual representations of suggested outfits.


## Tech Stack

### Frontend

- Vue.js
- Tailwind CSS

### Backend

- FastAPI
- OpenAI API (GPT-4)
- Stable Diffusion
- OpenWeatherMap API

## Prerequisites

- Python 3.8+
- Node.js and npm
- Stable Diffusion Web UI by AUTOMATIC1111 (https://github.com/AUTOMATIC1111/stable-diffusion-webui)
  model: CyberRealistic Pony v7 (https://civitai.com/models/443821?modelVersionId=507888)

- API keys for:
  - OpenAI (https://platform.openai.com/docs/overview)
  - OpenWeatherMap (https://home.openweathermap.org/api_keys)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Yamobura/WeatherWise.git
cd WeatherWise
```

2. Set up the backend:

```bash
cd backend
python -m venv venv
# On Windows Command Prompt:
.\venv\Scripts\activate.bat
# On Unix or MacOS:
source venv/bin/activate

pip install -r requirements.txt
```

3. Set up the frontend:

```bash
cd frontend
npm install
```

4. Configure API keys:
   - Create `backend/app/config.py` with your API keys:
   ```python
   OPENAI_API_KEY = 'your-openai-api-key'
   WEATHER_API_KEY = 'your-weather-api-key'
   WEBUI_SERVER_URL = 'http://127.0.0.1:7860'
   ```

## Running the Application

1. Start the Stable Diffusion Web UI:

```bash
cd stable-diffusion-webui
webui.bat --api
```

2. Start the backend server:

```bash
cd backend
uvicorn app.main:app --reload
```

3. Start the frontend development server:

```bash
cd frontend
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Usage

1. Enter a city name or use your current location
2. The app will fetch current weather conditions
3. Based on the weather, you'll receive:
   - A detailed weather overview
   - An AI-generated outfit suggestion
   - A visual representation of the suggested outfit

## API Endpoints

- `GET /weather` - Get weather data for a location
- `GET /chatgpt` - Generate outfit suggestions
- `GET /imagegeneration` - Generate outfit visualization
