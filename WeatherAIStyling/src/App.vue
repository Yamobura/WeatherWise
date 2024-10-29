<script>
import { ref, watch } from "vue";

export default {
  setup() {
    const cityName = ref(""); // Название города
    const locationData = ref(null); // Данные о местоположении
    const locationError = ref(""); // Ошибка геолокации
    const weatherData = ref(null); // Данные о погоде
    const suggestions = ref([]); // Подсказки для автозаполнения

    // Метод для получения геолокации
    const getLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          successCallback,
          errorCallback
        );
      } else {
        locationError.value = "Геолокация не поддерживается вашим браузером.";
      }
    };

    // Успешный обратный вызов геолокации
    const successCallback = (position) => {
      locationData.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      };
      getWeatherByLocation(position.coords.latitude, position.coords.longitude);
    };

    // Обработка ошибок геолокации
    const errorCallback = (error) => {
      switch (error.code) {
        case error.PERMISSION_DENIED:
          locationError.value = "Доступ к геолокации отклонен.";
          break;
        case error.POSITION_UNAVAILABLE:
          locationError.value = "Информация о местоположении недоступна.";
          break;
        case error.TIMEOUT:
          locationError.value = "Запрос геолокации истек.";
          break;
        default:
          locationError.value = "Произошла неизвестная ошибка.";
          break;
      }
    };

    // Метод для получения погоды по названию города
    const getWeatherByCity = (city) => {
      const apiKey = "c4926db13750fa4cb3bdb6c84f4153f5"; // Замените на свой API-ключ OpenWeatherMap
      const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric&lang=ru`;

      fetch(url)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Город не найден");
          }
          return response.json();
        })
        .then((data) => {
          weatherData.value = data;
          locationError.value = ""; // Очистить предыдущие ошибки

          // Сохраняем координаты города
          locationData.value = {
            latitude: data.coord.lat,
            longitude: data.coord.lon,
          };

          suggestions.value = [];
        })
        .catch((error) => {
          locationError.value =
            "Ошибка получения данных о погоде: " + error.message;
          weatherData.value = null; // Очистить предыдущие данные о погоде
          console.error(error);
        });
    };

    // Метод для получения погоды по координатам
    const getWeatherByLocation = (latitude, longitude) => {
      const apiKey = "c4926db13750fa4cb3bdb6c84f4153f5"; // Замените на свой API-ключ OpenWeatherMap
      const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric&lang=ru`;

      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          weatherData.value = data;
        })
        .catch((error) => {
          locationError.value = "Ошибка получения данных о погоде.";
          console.error(error);
        });
    };

    // Метод для поиска города
    const findCity = () => {
      if (cityName.value) {
        getWeatherByCity(cityName.value); // Получить погоду по названию города
      } else {
        alert("Пожалуйста, введите название города.");
      }
    };

    // Метод для получения подсказок городов
    const fetchCitySuggestions = async () => {
      if (cityName.value.length > 0) {
        const username = "yamobura"; // Замените на свой Geonames username
        const url = `http://api.geonames.org/searchJSON?name_startsWith=${cityName.value}&maxRows=10&username=${username}`;

        try {
          const response = await fetch(url);
          if (!response.ok) {
            throw new Error("Ошибка сети");
          }
          const data = await response.json();
          console.log(data); // Логирование ответа API
          if (data.geonames) {
            // Сохраняем как название города, так и страну
            suggestions.value = data.geonames.map((place) => ({
              name: place.name,
              country: place.countryCode,
            }));
          }
        } catch (error) {
          console.error("Ошибка при получении данных о городах:", error);
        }
      } else {
        suggestions.value = [];
      }
    };

    // Метод для выбора города из подсказок
    const selectCity = (city) => {
      cityName.value = city.name; // Устанавливаем название города
      suggestions.value = []; // Очищаем подсказки
      findCity(); // Находим погоду для выбранного города
    };

    // Установка наблюдателя на cityName для получения подсказок
    watch(cityName, (newValue) => {
      if (newValue.length > 0) {
        fetchCitySuggestions();
      } else {
        suggestions.value = [];
      }
    });

    return {
      cityName,
      locationData,
      locationError,
      weatherData,
      suggestions,
      getLocation,
      findCity,
      fetchCitySuggestions,
      selectCity,
    };
  },
};
</script>

<template>
  <div class="container mx-auto min-h-screen flex flex-col items-center">
    <header class="w-full py-4 text-center">
      <h1>WeatherWise</h1>
    </header>

    <div class="flex flex-col items-center justify-center flex-grow">
      <h1 class="mb-4">Let's find the location</h1>
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
