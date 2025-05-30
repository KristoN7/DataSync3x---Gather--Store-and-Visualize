// index.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { fetchTopGames } = require('./services/steamService');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3002;

app.use(cors());
app.use(bodyParser.json());

// Endpoint do pobrania danych z API i przesłania do kontrolera
app.post('/collect', async (req, res) => {
    try {
        const games = await fetchTopGames();
        
        // zapis do pliku z timestampem
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filePath = path.join(__dirname, 'data', `steam-${timestamp}.json`);
        fs.writeFileSync(filePath, JSON.stringify(games, null, 2));

        // wysyłka do kontrolera
        await sendToController(games);

        res.json({ message: 'Dane pobrane i przesłane do kontrolera.' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Błąd podczas zbierania danych' });
    }
});

// funkcja pomocnicza do wysłania danych do kontrolera
async function sendToController(games) {
    const axios = require('axios');
    await axios.post('http://localhost:3001/api/games', games);
}

app.listen(PORT, () => {
    console.log(`Collector działa na porcie ${PORT}`);
});

const axios = require('axios');

// Przykład funkcji pobierającej dane z SteamSpy
async function fetchSteamGames() {
  try {
    const response = await axios.get('https://steamspy.com/api.php?request=top100in2weeks');
    const data = response.data;

    // Zamień obiekt na tablicę
    const gamesArray = Object.values(data).slice(0, 50); // top 50

    const transformedData = gamesArray.map(game => ({
      name: game.name,
      players: game.owners, // liczba właścicieli (jako przybliżenie popularności)
      price: game.price / 100, // cena w USD
      discount: game.discount // % zniżki
    }));

    return transformedData;
  } catch (error) {
    console.error('Błąd pobierania danych ze SteamSpy:', error.message);
    return [];
  }
}

async function start() {
  const gamesData = await fetchSteamGames();

  if (gamesData.length > 0) {
    await sendToController(gamesData);
  }
}
