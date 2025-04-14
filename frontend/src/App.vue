<script>
import { ref } from "vue";

export default {
  setup() {
    const cityName = ref(""); // Название города
    const locationData = ref(null); // Данные о местоположении
    const locationError = ref(""); // Ошибка геолокации
    const weatherOverview = ref(null); // Обзор погоды
    const generatedImage = ref(null); // Сгенерированное изображение
    const backendBaseUrl = "http://127.0.0.1:8000"; // Адрес вашего FastAPI сервера
    const isLoading = ref(false);
    const locationCity = ref("");
    const locationDate = ref("");
    const promptForSD = ref("");
    const filteredCities = ref([]);
    const isPromptVisible = ref(false);

    const geonamesBaseUrl = "http://api.geonames.org/searchJSON"; // URL API
    const username = "yamobura"; // Ваш логин GeoNames

    // Запрос к GeoNames API для получения городов
    const fetchCities = async () => {
      if (!cityName.value) {
        filteredCities.value = [];
        return;
      }

      const url = `${geonamesBaseUrl}?q=${encodeURIComponent(
        cityName.value
      )}&maxRows=10&featureClass=P&orderby=population&username=${username}`;

      try {
        const response = await fetch(url);
        const data = await response.json();

        // Обновляем список городов
        filteredCities.value = data.geonames.map(
          (item) => `${item.name}, ${item.countryCode}` // Формат "City, CountryCode"
        );
      } catch (error) {
        console.error("Ошибка получения данных GeoNames:", error);
      }
    };

    // Обработка выбора города из выпадающего списка
    const selectCity = (city) => {
      // Extract only the city name before the comma
      const cityNameOnly = city.split(",")[0].trim();
      cityName.value = cityNameOnly;
      filteredCities.value = []; // Очистить список после выбора
    };

    const getCoordinates = () => {
      if (!navigator.geolocation) {
        locationError.value = "Geolocation is not supported by your browser.";
        return;
      }
      isLoading.value = true;
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          locationData.value = { latitude, longitude };
          await getWeatherOverview(latitude, longitude); // Запрос погоды по координатам
        },
        (error) => {
          locationError.value = "Unable to retrieve location.";
          console.error(error);
          isLoading.value = false;
        }
      );
    };

    // Метод для определения текущего местоположения
    const getWeatherOverview = async (lat = null, lon = null) => {
      isLoading.value = true;
      try {
        const params =
          lat && lon ? `lat=${lat}&lon=${lon}` : `city=${cityName.value}`;
        const response = await fetch(`${backendBaseUrl}/weather?${params}`);
        const data = await response.json();
        handleWeatherResponse(data);
      } catch (error) {
        console.error("Error fetching weather data:", error);
      } finally {
        isLoading.value = false;
      }
    };

    // Обработка ответа от бэкэнда
    const handleWeatherResponse = async (data) => {
      if (data.error) {
        console.error("Backend error:", data.error);
        return;
      }
      weatherOverview.value = data.overview;
      locationCity.value = data.city;
      locationDate.value = data.date;
    };

    // Генерация изображения через Stable Diffusion
    const generateImage = async () => {
      try {
        const response = await fetch(
          `${backendBaseUrl}/imagegeneration?chatgptprompt=${encodeURIComponent(
            promptForSD.value
          )}`
        );
        const data = await response.json();
        generatedImage.value = `data:image/png;base64,${data.generatedimage}`;
      } catch (error) {
        console.error("Error generating image:", error);
        throw error;
      }
    };

    // Поиск города вручную
    const findCity = async () => {
      if (!cityName.value) return;
      isLoading.value = true;
      try {
        // Get weather data
        await getWeatherOverview();

        // Get ChatGPT prompt
        await getChatGptPrompt();

        // Generate image
        await generateImage();

        // Show all content
        isPromptVisible.value = true;
      } catch (error) {
        console.error("Error in findCity:", error);
      } finally {
        isLoading.value = false;
      }
    };

    // Генерация промпта через ChatGPT
    const getChatGptPrompt = async () => {
      try {
        const response = await fetch(
          `${backendBaseUrl}/chatgpt?city=${encodeURIComponent(
            locationCity.value
          )}&overview_data=${encodeURIComponent(weatherOverview.value)}`
        );
        const data = await response.json();
        promptForSD.value = data.chatgptprompt;
      } catch (error) {
        console.error("Error generating prompt:", error);
        throw error;
      }
    };

    return {
      cityName,
      locationData,
      locationError,
      weatherOverview,
      promptForSD,
      generatedImage,
      locationCity,
      locationDate,
      isLoading,
      getCoordinates,
      findCity,
      getChatGptPrompt,
      generateImage,
      filteredCities,
      fetchCities,
      selectCity,
      isPromptVisible,
    };
  },
};
</script>

<template>
  <div class="main mx-auto min-h-screen flex flex-col items-center">
    <header class="w-full py-4 text-center">
      <h1>WeatherWise</h1>
    </header>

    <div class="flex flex-col items-center mt-32 flex-grow">
      <h1 class="mb-6">
        Let us know your location to generate an outfit suggestion
      </h1>

      <form @submit.prevent="findCity" class="flex items-center">
        <div class="relative w-full">
          <input
            v-model="cityName"
            type="text"
            placeholder="Enter city name"
            @input="fetchCities"
            class="border p-2 pl-4 pr-32 rounded"
          />

          <!-- Выпадающий список -->
          <ul v-if="filteredCities.length" class="dropdown">
            <li
              v-for="(city, index) in filteredCities"
              :key="index"
              @click="selectCity(city)"
              class="dropdown-item"
            >
              {{ city }}
            </li>
          </ul>
          <button
            type="button"
            @click="getLocation"
            class="absolute right-3 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-1 shadow mr-3"
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

      <div>
        <div v-if="isLoading" class="loading-spinner">
          <div class="spinner"></div>
          <p>Generating your weather-appropriate outfit...</p>
        </div>

        <div v-else>
          <!-- Дата и город -->
          <div v-if="locationCity && locationDate" class="text-center mt-6">
            <div><span>Today:</span> {{ locationDate }}</div>
            <div><span>Location:</span> {{ locationCity }}</div>
          </div>

          <!-- Обзор погоды -->
          <div v-if="weatherOverview" class="flex bg-white max-w-4xl mt-6">
            <div class="ml-3 mb-6">
              <div class="weather-overview mt-6 text-center pb-6">
                <h2 class="text-lg font-bold mb-2">Weather Overview</h2>
                <p>{{ weatherOverview }}</p>
              </div>

              <div
                v-if="promptForSD && isPromptVisible"
                class="promptforSD mt-6 text-center cursor-pointer"
              >
                <h2 class="text-lg font-bold mb-2">Outfit Suggestion</h2>
                <p>{{ promptForSD }}</p>
              </div>
            </div>

            <!-- Картинка -->
            <div
              v-if="generatedImage"
              class="generated-image mt-6 mr-3 ml-3 text-center"
            >
              <h2 class="text-lg font-bold mb-2">Generated Outfit</h2>
              <img
                :src="generatedImage"
                alt="Generated Outfit"
                class="max-w-xs rounded shadow"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
