import React, { useState, useEffect } from 'react';

type TileStatus = 'empty' | 'filled' | 'correct' | 'present' | 'absent';

interface TileProps {
  letter: string;
  status: TileStatus;
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

  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        handleKeyClick('ENTER');
      } else if (event.key === 'Backspace') {
        handleKeyClick('←');
      } else if (/^[a-zA-Z]$/.test(event.key)) {
        handleKeyClick(event.key.toUpperCase());
      }
    };

    window.addEventListener('keydown', handleKeydown);
    
    return () => {
      window.removeEventListener('keydown', handleKeydown);
    };
  }, [currentRow, currentTile, board]);

  const handleKeyClick = (key: string) => {
    if (currentRow >= 6) return;

    const newBoard = [...board];
    
    if (key === '←' || key === 'Backspace') {
      if (currentTile > 0) {
        newBoard[currentRow][currentTile - 1].letter = '';
        newBoard[currentRow][currentTile - 1].status = 'empty';
        setCurrentTile(currentTile - 1);
      }
    } else if (key === 'ENTER') {
      if (currentTile === 5) {
        newBoard[currentRow].forEach((tile, index) => {
          if (index === 0) tile.status = 'correct';
          else if (index === 1) tile.status = 'present';
          else tile.status = 'absent';
        });
        setCurrentRow(currentRow + 1);
        setCurrentTile(0);
      }
    } else if (currentTile < 5) {
      newBoard[currentRow][currentTile].letter = key;
      newBoard[currentRow][currentTile].status = 'filled';
      setCurrentTile(currentTile + 1);
    }

    setBoard(newBoard);
  };

  const keyboardRows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '←']
  ];

  return (
    <div className="flex flex-col items-center bg-white min-h-screen p-4">
      {/* Title */}
      <header className="w-full max-w-xl border-b border-gray-200 pb-2 mb-8">
        <h1 className="text-4xl font-bold text-center">Wordle (Solver)</h1>
      </header>

      {/* Word Board */}
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

      {/* Keys */}
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
    </div>
  );
};

export default WordleGame;