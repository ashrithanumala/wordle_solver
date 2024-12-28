import {StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { Alert } from './components/Alert'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

type TileStatus = 'empty' | 'filled' | 'correct' | 'present' | 'absent';

interface TileProps {
  letter: string;
  status: TileStatus;
}

interface Suggestion {
  word: string;
  probability: number;
}

const Tile: React.FC<TileProps & { isCurrent?: boolean }> = ({ letter, status }) => {
  const baseStyles = "w-14 h-14 border-2 flex items-center justify-center text-2xl font-bold uppercase transition-colors duration-500 relative";
  
  const statusStyles = {
    empty: "border-gray-300",
    filled: "border-gray-500",
    correct: "border-green-500 bg-green-500 text-white",
    present: "border-yellow-500 bg-yellow-500 text-white",
    absent: "border-gray-500 bg-gray-500 text-white",
  };

  return (
    <div className={`${baseStyles} ${statusStyles[status]}`}>
      {letter}
    </div>
  );
};

const KeyboardKey: React.FC<{ 
  letter: string; 
  status?: TileStatus;
  onClick: (letter: string) => void;
  isWide?: boolean;
}> = ({ letter, status = 'empty', onClick, isWide }) => {
  const baseStyles = "h-14 flex items-center justify-center text-sm font-bold rounded uppercase transition-colors duration-150 hover:opacity-90";
  
  const statusStyles = {
    empty: "bg-gray-200 text-black",
    correct: "bg-green-500 text-white",
    present: "bg-yellow-500 text-white",
    absent: "bg-gray-500 text-white",
    filled: "bg-gray-200 text-black",
  };

  return (
    <button 
      className={`${baseStyles} ${statusStyles[status]} ${isWide ? 'w-16' : 'w-10'}`}
      onClick={() => onClick(letter)}
    >
      {letter}
    </button>
  );
};

const WordleGame: React.FC = () => {
  const [board, setBoard] = useState<Array<Array<{ letter: string; status: TileStatus }>>>(
    Array(6).fill(null).map(() => 
      Array(5).fill(null).map(() => ({ letter: '', status: 'empty' }))
    )
  );
  const [currentRow, setCurrentRow] = useState(0);
  const [currentTile, setCurrentTile] = useState(0);
  const [gameActive, setGameActive] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [gameOver, setGameOver] = useState(false);
  const [targetWord, setTargetWord] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [gameSession, setGameSession] = useState<string>('');
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const startNewGame = async (mode: 'random' | 'daily') => {
    try {
      const endpoint = mode === 'random' 
        ? 'http://localhost:5001/api/start-game-random' 
        : 'http://localhost:5001/api/start-game-daily';

      const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setBoard(Array(6).fill(null).map(() => 
          Array(5).fill(null).map(() => ({ letter: '', status: 'empty' }))
        ));
        setCurrentRow(0);
        setCurrentTile(0);
        setGameActive(true);
        setGameOver(false);
        setTargetWord('');
        setSuggestions(data.suggestions);
        setGameSession(data.session_id);
      }
    } catch (error) {
      console.error('Error starting game:', error);
      setError('Failed to start game. Please try again.');
    }
  };

  const makeGuess = async (word: string) => {
    if (isSubmitting) return false;
    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:5001/api/make-guess', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ 
          guess: word,
          session_id: gameSession
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        if (data.error === 'Invalid word') {
          setError('Not a valid word! Try again.');
          return false;
        } else if (data.error === 'Invalid session') {
          setError('Game session expired. Please start a new game.');
          setGameActive(false);
          return false;
        } else {
          setError(data.error || 'An error occurred. Please try again.');
          return false;
        }
      }
      
      const newBoard = [...board];
      for (let i = 0; i < 5; i++) {
        const position_state = data.state[i];
        let status: TileStatus = 'absent';

        if (position_state === 2) {
          status = 'correct';
        } else if (position_state === 1) {
          status = 'present';
        }
        newBoard[currentRow][i].status = status;
      }

      setBoard(newBoard);
      setSuggestions(data.suggestions);

      if (data.done) {
        setGameOver(true);
        setGameActive(false);
        if (data.target_word) {
          setTargetWord(data.target_word);
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error making guess:', error);
      setError('Network error. Please try again.');
      return false;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyClick = async (key: string, event?: KeyboardEvent) => {
    // for some reason this makes the start_game issue go away
    if (event) {
        event.preventDefault();
    }
    
    if (!gameActive || gameOver) return;
    
    const newBoard = [...board];
    
    if (key === '←' || key === 'Backspace') {
        if (currentTile > 0) {
            newBoard[currentRow][currentTile - 1].letter = '';
            newBoard[currentRow][currentTile - 1].status = 'empty';
            setCurrentTile(currentTile - 1);
            setBoard(newBoard);
        }
    } else if (key === 'ENTER') {
        if (currentTile === 5) {
            const word = newBoard[currentRow].map(tile => tile.letter).join('').toLowerCase();
            const successful_guess = await makeGuess(word);
            if (successful_guess) {
                setCurrentRow(currentRow + 1);
                setCurrentTile(0);
            }
        }
    } else if (currentTile < 5) {
        newBoard[currentRow][currentTile].letter = key;
        newBoard[currentRow][currentTile].status = 'filled';
        setCurrentTile(currentTile + 1);
        setBoard(newBoard);
    }
  };

  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
        if (!gameActive || gameOver) return;
        
        if (event.key === 'Enter') {
            event.preventDefault(); // manually do form submission
            handleKeyClick('ENTER', event);
        } else if (event.key === 'Backspace') {
            handleKeyClick('←', event);
        } else if (/^[a-zA-Z]$/.test(event.key)) {
            handleKeyClick(event.key.toUpperCase(), event);
        }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
}, [currentRow, currentTile, board, gameActive, gameOver, handleKeyClick]);

  const keyboardRows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '←']
  ];

  return (
    <div className="flex min-h-screen bg-white relative">
      {/* Error Alert */}
      {error && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-96">
          <Alert variant="destructive">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button 
                onClick={() => setError(null)}
                className="ml-2 text-sm hover:opacity-80"
              >
                ✕
              </button>
            </div>
          </Alert>
        </div>
      )}
  
      {/* Left Half - Grid */}
      <div className="w-1/2 flex flex-col items-center p-8">
        <header className="w-full max-w-xl pb-2 mb-8">
          <h1 className="text-4xl font-bold text-center">Wordle (Boosted)</h1>
        </header>
  
        <div className="flex gap-4 mb-12">
          <button
            onClick={() => startNewGame('random')}
            className="py-3 px-4 bg-black text-white rounded hover:bg-gray-800 transition-colors"
          >
            Play Random Word
          </button>
          <button
            onClick={() => startNewGame('daily')}
            className="py-3 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Play Daily Word
          </button>
        </div>
  
        {/* Game Board */}
        <div className="grid grid-rows-6 gap-1 mb-8">
          {board.map((row, rowIndex) => (
            <div key={rowIndex} className={`grid grid-cols-5 gap-1 relative
            }`}>
              {rowIndex === currentRow && <div className="row-indicator"></div>}
              {row.map((tile, tileIndex) => (
                <Tile
                  key={`${rowIndex}-${tileIndex}`}
                  letter={tile.letter}
                  status={tile.status}
                />
              ))}
            </div>
          ))}
        </div>
  
        {/* Keyboard */}
        <div className="w-full max-w-xl">
          {keyboardRows.map((row, rowIndex) => (
            <div key={rowIndex} className="flex justify-center gap-1.5 mb-1.5">
              {row.map((key) => (
                <KeyboardKey
                  key={key}
                  letter={key}
                  onClick={handleKeyClick}
                  isWide={key.length > 1}
                />
              ))}
            </div>
          ))}
        </div>
  
        {/* Game Over Message */}
        {gameOver && (
          <div className="mt-4 text-center">
            <p className="text-xl font-bold">
              Game Over! The word was: {targetWord}
            </p>
          </div>
        )}
      </div>
  
      {/* Right Half - Suggestions */}
      <div className="w-1/2 p-8 border-l border-gray-200 flex flex-col">
        <h2 className="text-2xl font-bold mb-6">Suggested Words</h2>
          <div className="flex-1 min-h-[600px]">
            <ResponsiveContainer width="95%" height="100%">
              <PieChart>
                <Pie
                  data={suggestions.map(({ word, probability }) => ({
                    name: word.toUpperCase(),
                    value: probability * 100
                  }))}
                  innerRadius="33%"
                  outerRadius="60%"
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, value }) => `${name} (${value.toFixed(1)}%)`}
                  labelLine={false}
                >
                  {suggestions.map((_, index) => (
                    <Cell 
                      key={`cell-${index}`}
                      fill={[
                        '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
                        '#82CA9D', '#F06292', '#BA68C8', '#4DD0E1', '#81C784'
                      ][index % 10]}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => `${(value as number).toFixed(2)}%`}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="min-h-screen bg-white">
      <WordleGame />
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)