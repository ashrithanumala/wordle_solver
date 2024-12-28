# Wordle with AI Suggestions

A "boosted" version of Wordle that provides AI-powered suggestions for your next guess. Play either with random words or challenge yourself with the official NYT Wordle word of the day.

## Features

- Two game modes:
  - Random words from past Wordle answers
  - Daily word synchronized with NYT's Wordle
- AI-powered suggestions with probability visualization
- Real-time feedback on guesses

### Quick Start

1. Clone the repository
2. Run the startup script: start.sh

### Manual Setup

You can also startup the services independently:

#### Backend Setup
\```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
\```

#### Frontend Setup
\```
cd frontend
npm install
npm run dev
\```

### Playing the Game

1. Open your browser and navigate to `http://localhost:5173`
2. Choose your game mode:
   - "Play Random Word" for a random challenge
   - "Play Daily Word" to attempt the update NYT Wordle daily word
3. Make your guesses using the on-screen keyboard or your physical keyboard
4. Use the chart on the right to see AI-suggested words
5. Color feedback:
   - 🟩 Green: Correct letter in correct position
   - 🟨 Yellow: Correct letter in wrong position
   - ⬜ Gray: Letter not in word

## Technical Details

### Frontend
- Built with React + TypeScript
- Uses Vite for development
- Recharts for probability visualization
- Tailwind CSS for styling

### Backend
- Flask server with Python
- AI suggestions based on probability analysis
- Caching system for daily words
- CORS enabled for local development

### API Endpoints

- `POST /api/start-game-random`: Start a new game with random word
- `POST /api/start-game-daily`: Start a new game with NYT's daily word
- `POST /api/make-guess`: Submit a guess and get feedback

### Reinforcement learning agent
- you can also test the agent on custom words using instructions found in backend/test.py

## Project Structure
\```
wordle-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── index.tsx
│   ├── package.json
│   └── index.html
├── backend/
│   ├── data/
│   │   ├── wordle_words.txt
│   │   ├── common_words.txt
│   │   └── past_wordle_answers.txt
│   ├── app.py
│   ├── wordle_env.py
│   └── requirements.txt
└── start.sh
\```

Thank you for making it this far!
