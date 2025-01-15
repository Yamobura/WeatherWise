<script>
import { ref } from "vue";

export default {
  setup() {
    const cityName = ref(""); // Название города
    const locationData = ref(null); // Данные о местоположении
    const locationError = ref(""); // Ошибка геолокации
    const weatherOverview = ref(null); // Обзор погоды
    const generatedImage = ref(null); // Сгенерированное изображение
    const backendBaseUrl = "http://127.0.0.1:8000/"; // Адрес вашего FastAPI сервера
    const isLoading = ref(false);
    const locationCity = ref("");
    const locationDate = ref("");
    const propmtforSD = ref("");
    const filteredCities = ref([]);

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
      cityName.value = city;
      filteredCities.value = []; // Очистить список после выбора
    };


    // Метод для определения текущего местоположения
    const getLocation = async () => {
      if (navigator.geolocation) {
        isLoading.value = true;
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const { latitude, longitude } = position.coords;
            locationData.value = { latitude, longitude };

            try {
          // Отправляем координаты на бэкэнд
          const response = await fetch(
            `${backendBaseUrl}weather?lat=${latitude}&lon=${longitude}`
          );
          const data = await response.json();
          handleBackendResponse(data);
        } catch (error) {
          console.error("Ошибка получения данных:", error);
        } finally {
          isLoading.value = false; // Завершаем загрузку
        }
      },
      (error) => {
        locationError.value = "Ошибка определения геолокации.";
        console.error(error);
        isLoading.value = false; // Завершаем загрузку в случае ошибки
      }
    );
  } else {
    locationError.value = "Геолокация не поддерживается вашим браузером.";
  }
    };

    // Метод для поиска города
    const findCity = async () => {
  if (!cityName.value) return;

  isLoading.value = true; // Начало загрузки
  try {
    const response = await fetch(
      `${backendBaseUrl}weather?city=${encodeURIComponent(cityName.value)}`
    );
    const data = await response.json();
    handleBackendResponse(data);
  } catch (error) {
    console.error("Ошибка получения данных:", error);
  } finally {
    isLoading.value = false; // Завершаем загрузку
  }
};

    // Обработка ответа от бэкэнда
    const handleBackendResponse = (data) => {
      if (data.error) {
        console.error("Ошибка от бэкэнда:", data.error);
        return;
      }
      weatherOverview.value = data.overview; // Обзор погоды
      generatedImage.value = `data:image/png;base64,${data.image}`; // Картинка
      locationCity.value = data.city;
      locationDate.value = data.date;
      propmtforSD.value = data.stable_diffusion_prompt;
    };

    return {
      cityName,
      locationData,
      locationError,
      weatherOverview,
      generatedImage,
      location,
      propmtforSD,
      getLocation,
      findCity,
      locationCity,
      locationDate,
      isLoading,
      filteredCities,
      fetchCities,
      selectCity,
      findCity
    };
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
      v-model="cityName"
      type="text"
      placeholder="Enter city name"
      @input="fetchCities"
      class="border p-2 rounded"
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

      <div>
  <div v-if="isLoading" class="loading-spinner">
    <p>Loading...</p>
  </div>

  <div v-else>
    <!-- Дата и город -->
    <div v-if="locationCity && locationDate">
      <div><span>Today:</span> {{ locationDate }}</div>
      <div><span>Location:</span> {{ locationCity }}</div>
    </div>

    <!-- Обзор погоды -->
    <div v-if="weatherOverview" class="weather-overview mt-6 text-center">
      <h2 class="text-lg font-bold mb-2">Weather Overview</h2>
      <p>{{ weatherOverview }}</p>
    </div>

    <!-- Картинка -->
    <div v-if="generatedImage" class="generated-image mt-6">
      <h2 class="text-lg font-bold mb-2">Generated Image</h2>
      <img :src="generatedImage" alt="Generated Image" class="max-w-md rounded shadow" />
    </div>

    <!-- Ошибка -->
    <div v-if="locationError" class="error mt-4 text-red-500">
      {{ locationError }}
    </div>
  </div>
</div>


       

     

      
    </div>
  </div>
</template>
