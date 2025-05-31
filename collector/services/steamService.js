// services/steamService.js
const axios = require('axios');

async function fetchTopGames() {
  try {
    const response = await axios.get('https://steamspy.com/api.php?request=top100in2weeks');
    const data = response.data;

    const gamesArray = Object.values(data).slice(0, 100);

    return gamesArray.map(game => ({
      name: game.name,
      players: parsePlayers(game.owners),
      price: game.price / 100,
      discount: game.discount
    }));
  } catch (error) {
    console.error('Błąd pobierania danych ze SteamSpy:', error.message);
    return [];
  }
}

function parsePlayers(ownersString) {
  //"10,000,000 .. 20,000,000"
  const match = ownersString.match(/([\d,]+)/);
  if (!match) return 0;

  return parseInt(match[1].replace(/,/g, ''), 10);
}

module.exports = { fetchTopGames };
