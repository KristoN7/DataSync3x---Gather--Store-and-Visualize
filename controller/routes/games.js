// routes/games.js
const express = require('express');
const router = express.Router();
const Game = require('../models/Game');

// GET all
router.get('/', async (req, res) => {
    const games = await Game.find();
    res.json(games); //zwraca listę gier jako JSON
});

// POST /api/games — obsługuje wiele gier
router.post('/', async (req, res) => {
    try {
        const games = req.body;

        if (!Array.isArray(games)) {
            return res.status(400).json({ error: 'Oczekiwano tablicy gier' });
        }
        const timestamp = new Date(); //data dodania gry do bazy danych
        const gamesWithTimestamp = games.map(game => ({ ...game, timestamp }));

        //MongoDB Insert
        await Game.insertMany(gamesWithTimestamp);

        res.status(201).json({ message: 'Gry zapisane do bazy danych' });
    } catch (err) {
        console.error('Błąd podczas zapisu gier:', err);
        res.status(500).json({ error: 'Błąd zapisu danych' });
    }
});


// DELETE all
router.delete('/', async (req, res) => {
    await Game.deleteMany({});
    res.json({ message: "Wszystkie gry usunięte" });
});

module.exports = router;
