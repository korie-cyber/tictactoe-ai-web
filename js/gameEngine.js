const WIN_PATTERNS = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

export function createBoard() {
  return Array(9).fill(null);
}

export function getAvailableMoves(board) {
  return board.reduce((moves, cell, i) => {
    if (cell === null) moves.push(i);
    return moves;
  }, []);
}

export function applyMove(board, index, player) {
  if (board[index] !== null) return null;
  const next = board.slice();
  next[index] = player;
  return next;
}

export function checkWinner(board) {
  for (const pattern of WIN_PATTERNS) {
    const [a, b, c] = pattern;
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return { winner: board[a], line: pattern };
    }
  }
  return null;
}

export function isBoardFull(board) {
  return board.every(cell => cell !== null);
}

export function getGameResult(board) {
  const win = checkWinner(board);
  if (win) return { status: 'win', winner: win.winner, line: win.line };
  if (isBoardFull(board)) return { status: 'draw', winner: null, line: null };
  return { status: 'playing', winner: null, line: null };
}

export function opponent(player) {
  return player === 'X' ? 'O' : 'X';
}

export { WIN_PATTERNS };
