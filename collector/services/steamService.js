// services/steamService.js
const axios = require('axios');

async function fetchTopGames() {
  try {
    const response = await axios.get('https://steamspy.com/api.php?request=top100in2weeks');
    const data = response.data;

    const gamesArray = Object.values(data).slice(0, 100);

    return gamesArray.map(game => {
      const price = game.price / 100;
      const positive = Number(game.positive);
      const negative = Number(game.negative);
      
      return {
        name: game.name,
        players: parsePlayers(game.owners),
        price: price,
        discount: Number(game.discount),
        paymentModel: getPaymentModel(price),
        onSale: getDiscountStatus(Number(game.discount)),
        category: determineCategory(positive, negative)
      };
    });
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

function getPaymentModel(price) {
  return price === 0 ? "Free" : "Paid";
}

function getDiscountStatus(discount) {
  return discount > 0 ? "Tak" : "Nie";
}
function determineCategory(positive, negative) {
  if (negative === 0) negative = 1; // żeby nie dzielić przez zero
  const ratio = positive / negative;

  if (positive > 500000 && ratio > 10) return "Popularna";
  if (positive > 100000 && ratio > 5) return "Dobra";
  if (positive > 10000 && ratio > 2) return "Średnia";
  return "Słaba";
}

module.exports = { fetchTopGames };
