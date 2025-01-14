
<script>
import { ref, watch } from "vue";

export default {
  setup() {
    const cityName = ref(""); // Название города
    const locationData = ref(null); // Данные о местоположении
    const locationError = ref(""); // Ошибка геолокации
    const weatherData = ref(null); // Данные о погоде
    const suggestions = ref([]); // Подсказки для автозаполнения

    const backendBaseUrl = "http://127.0.0.1:8000/"; // Адрес вашего FastAPI сервера

    // Метод для определения текущего местоположения
    const getLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            locationData.value = { latitude, longitude };

          },
          (error) => {
            locationError.value = "Ошибка определения геолокации.";
            console.error(error);
          }
        );
      } else {
        locationError.value = "Геолокация не поддерживается вашим браузером.";
      }
    };

    async function getWeatherByCity(city) {
    const response = await fetch(`http://127.0.0.1:8000/weather?city=${city}`);
    const data = await response.json();
    return data;
}

// Отправка координат для получения погоды
async function getWeatherByCoords(lat, lon) {
    const response = await fetch(`http://127.0.0.1:8000/weather?lat=${lat}&lon=${lon}`);
    const data = await response.json();
    return data;
}

// Отправка промпта для генерации изображения
async function generateImage(prompt) {
    const response = await fetch("http://127.0.0.1:8000/generate-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
    });
    const data = await response.json();
    return data.image;
}


    return {
      cityName,
      locationData,
      locationError,
      weatherData,
      suggestions,
      getLocation,
/*       getWeatherByCity,
 */    };
  },
};
</script>



<template>
  <div class="main container mx-auto min-h-screen flex flex-col items-center">
    <header class="w-full py-4 text-center">
      <h1>WeatherWise</h1>
    </header>

    <div class="flex flex-col items-center justify-center flex-grow">
      <h1 class="mb-4">Let us know your location to generate an outfit suggestion</h1>
      <form @submit.prevent="findCity" class="flex items-center">
        <div class="relative w-full">
          <input
            type="text"
            v-model="cityName"
            placeholder="Enter city name"
            class="border border-gray-400 focus:border-blue-500 focus:outline-none p-2 pl-10 pr-10 rounded w-full"
          />
          <button
            type="button"
            @click="getLocation"
            class="absolute right-3 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-1 shadow"
          >
            <img
              src="./assets/location.png"
              alt="Use current location"
              class="w-5 h-5"
            />
          </button>
        </div>
        <button
          type="submit"
          class="bg-white text-gray-800 flex items-center pr-6 pl-2 py-2 rounded ml-2 shadow"
        >
          <img
            src="./assets/magnifying-glass.png"
            alt="Search"
            class="w-4 h-4 mr-2"
          />
          Search
        </button>
      </form>

      <!-- Suggestions list with translated content -->
      <ul
        v-if="suggestions.length > 0"
        class="absolute z-10 bg-white border border-gray-400 rounded w-64 mt-1"
      >
        <li
          v-for="(city, index) in suggestions"
          :key="index"
          @click="selectCity(city)"
          class="p-2 cursor-pointer hover:bg-gray-200"
        >
          {{ city.name }}, {{ city.country }}
          <!-- Display city name and country -->
        </li>
      </ul>

      <div v-if="locationError" class="error">{{ locationError }}</div>
      <div v-if="locationData">
        Your location: Latitude: {{ locationData.latitude }}, Longitude:
        {{ locationData.longitude }}
      </div>
      <div v-if="weatherData">
        <p>Your city: {{ weatherData.name }}</p>
        <p>Temperature: {{ weatherData.main.temp }}°C</p>
        <p>Humidity: {{ weatherData.main.humidity }}%</p>
        <p>Wind Speed: {{ weatherData.wind.speed }} m/s</p>
        <p>Cloudiness: {{ weatherData.clouds.all }}%</p>
        <p>Weather Code: {{ weatherData.weather[0].id }}</p>
        <p v-if="weatherData.rain">
          Precipitation: {{ weatherData.rain["1h"] }} mm (last hour)
        </p>
        <p v-if="weatherData.rain">
          Precipitation: {{ weatherData.rain["24h"] }} mm (last 24 hours)
        </p>
      </div>
    </div>
  </div>
</template>