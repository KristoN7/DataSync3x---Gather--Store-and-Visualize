// controller.js (fragment)

const express = require('express');
const { MongoClient } = require('mongodb');

const app = express();
app.use(express.json());

const uri = 'mongodb://localhost:27017'; // ustaw swój URI MongoDB
const client = new MongoClient(uri);
let collection;

async function connectDB() {
  await client.connect();
  const db = client.db('bdi_js');
  collection = db.collection('games');
}
connectDB().catch(console.error);

// Endpoint do przyjmowania danych od kolektora
app.post('/api/games', async (req, res) => {
  const newGames = req.body; // oczekujemy tablicy obiektów

  if (!Array.isArray(newGames)) {
    return res.status(400).send('Invalid data format, expected array');
  }

  try {
    // Usuwamy całą kolekcję
    await collection.deleteMany({});

    // Dodajemy nowe dane
    if (newGames.length > 0) {
      await collection.insertMany(newGames);
    }

    res.status(200).send({ message: 'Dane zaktualizowane' });
  } catch (err) {
    console.error(err);
    res.status(500).send('Błąd serwera');
  }
});

// Endpoint do pobierania danych (dla GUI)
app.get('/api/games', async (req, res) => {
  try {
    const games = await collection.find({}).toArray();
    res.json(games);
  } catch (err) {
    res.status(500).send('Błąd pobierania danych');
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Kontroler działa na porcie ${PORT}`);
});
