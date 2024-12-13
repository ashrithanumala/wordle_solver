// src/main.tsx
import './index.css';  // Import Tailwind CSS styles

// Function to set up the Wordle game
const setupWordleGame = () => {
  const app = document.getElementById('app')!;
  const gameDiv = document.createElement('div');
  gameDiv.classList.add('game');
  gameDiv.innerHTML = `
    <h1 class="text-4xl font-bold text-center mb-6">Wordle</h1>
    <div id="game-board" class="grid grid-cols-5 gap-2">
      <!-- Wordle game will be here -->
    </div>
    <button class="start-btn bg-blue-500 text-white px-4 py-2 rounded mt-4 hover:bg-blue-600">Start Game</button>
  `;
  app.appendChild(gameDiv);
};

setupWordleGame();
