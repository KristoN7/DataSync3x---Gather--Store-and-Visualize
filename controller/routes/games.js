// routes/games.js
const express = require('express');
const router = express.Router();
const Game = require('../models/Game');

// GET all
router.get('/', async (req, res) => {
    const games = await Game.find();
    res.json(games);
});

// POST /api/games — obsługuje wiele gier
router.post('/', async (req, res) => {
    try {
        const games = req.body;

        // Walidacja — czy to tablica
        if (!Array.isArray(games)) {
            return res.status(400).json({ error: 'Oczekiwano tablicy gier' });
        }

        // Ustaw timestamp na teraz dla każdej gry
        const timestamp = new Date();
        const gamesWithTimestamp = games.map(game => ({ ...game, timestamp }));

        // Zapisz do MongoDB
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
