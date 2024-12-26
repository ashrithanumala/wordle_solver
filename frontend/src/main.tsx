import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

type TileStatus = 'empty' | 'filled' | 'correct' | 'present' | 'absent';

interface TileProps {
  letter: string;
  status: TileStatus;
}

interface Suggestion {
  word: string;
  probability: number;
}

const Tile: React.FC<TileProps> = ({ letter, status }) => {
  const baseStyles = "w-14 h-14 border-2 flex items-center justify-center text-2xl font-bold uppercase transition-colors duration-500";
  
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

  const startNewGame = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/start-game', {
        method: 'POST',
      });
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
      }
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };

  const getStatusFromState = (state: number): TileStatus => {
    switch (state) {
      case 2: return 'correct';
      case 1: return 'present';
      case -1: return 'absent';
      default: return 'empty';
    }
  };

  const makeGuess = async (word: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/make-guess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ guess: word }),
      });
      const data = await response.json();
      
      if (response.ok) {
        const newBoard = [...board];
        for (let i = 0; i < 5; i++) {
          newBoard[currentRow][i].status = getStatusFromState(data.state[i]);
        }
        setBoard(newBoard);
        setSuggestions(data.suggestions);
        
        if (data.done) {
          setGameOver(true);
          setTargetWord(data.target_word);
          setGameActive(false);
        } else {
          setCurrentRow(currentRow + 1);
          setCurrentTile(0);
        }
      }
    } catch (error) {
      console.error('Error making guess:', error);
    }
  };

  const handleKeyClick = (key: string) => {
    if (!gameActive || gameOver) return;
    
    const newBoard = [...board];
    
    if (key === '←' || key === 'Backspace') {
      if (currentTile > 0) {
        newBoard[currentRow][currentTile - 1].letter = '';
        newBoard[currentRow][currentTile - 1].status = 'empty';
        setCurrentTile(currentTile - 1);
      }
    } else if (key === 'ENTER') {
      if (currentTile === 5) {
        const word = newBoard[currentRow].map(tile => tile.letter).join('').toLowerCase();
        makeGuess(word);
      }
    } else if (currentTile < 5) {
      newBoard[currentRow][currentTile].letter = key;
      newBoard[currentRow][currentTile].status = 'filled';
      setCurrentTile(currentTile + 1);
    }

    setBoard(newBoard);
  };

  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
      if (!gameActive || gameOver) return;
      
      if (event.key === 'Enter') {
        handleKeyClick('ENTER');
      } else if (event.key === 'Backspace') {
        handleKeyClick('←');
      } else if (/^[a-zA-Z]$/.test(event.key)) {
        handleKeyClick(event.key.toUpperCase());
      }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, [currentRow, currentTile, board, gameActive, gameOver]);

  const keyboardRows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '←']
  ];

  return (
    <div className="flex min-h-screen bg-white">
      {/* Left panel with Start button */}
      <div className="w-64 p-4 border-r border-gray-200">
        <button
          onClick={startNewGame}
          className="w-full py-2 px-4 bg-black text-white rounded hover:bg-gray-800 transition-colors"
        >
          Start Game
        </button>
      </div>

      {/* Main game board */}
      <div className="flex-1 flex flex-col items-center p-4">
        <header className="w-full max-w-xl border-b border-gray-200 pb-2 mb-8">
          <h1 className="text-4xl font-bold text-center">Wordle (Solver)</h1>
        </header>

        <div className="grid grid-rows-6 gap-1 mb-8">
          {board.map((row, rowIndex) => (
            <div key={rowIndex} className="grid grid-cols-5 gap-1">
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

        {gameOver && (
          <div className="mt-4 text-center">
            <p className="text-xl font-bold">
              Game Over! The word was: {targetWord}
            </p>
          </div>
        )}
      </div>

      {/* Right panel with suggestions */}
      <div className="w-80 p-4 border-l border-gray-200">
        <h2 className="text-lg font-bold mb-4">Suggested Words</h2>
        <div className="space-y-2">
          {suggestions.map(({ word, probability }, index) => (
            <div key={index} className="flex justify-between">
              <span className="font-mono uppercase">{word}</span>
              <span className="text-gray-600">{(probability * 100).toFixed(2)}%</span>
            </div>
          ))}
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
);