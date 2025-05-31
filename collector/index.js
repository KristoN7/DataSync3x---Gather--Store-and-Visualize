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
