<script setup>
import { ref, onMounted } from 'vue';

const message = ref('Chargement...');

console.log(import.meta.env.VITE_API_URL);

onMounted(async () => {
  try {
    const response = await fetch(import.meta.env.VITE_API_URL + "/");
    const data = await response.json();
    message.value = data.message;
  } catch (error) {
    console.error("Erreur API:", error);
    message.value = "Erreur de connexion au backend";
  }
});
</script>

<template>
  <h1>{{ message }}</h1>
</template>

<style scoped>
h1 {
  text-align: center;
  margin-top: 50px;
}
</style>
