// models/Game.js
const mongoose = require('mongoose');

const GameSchema = new mongoose.Schema({
    name: String,
    players: Number,
    price: Number,
    discount: Number,
    timestamp: Date
});

module.exports = mongoose.model('Game', GameSchema);
