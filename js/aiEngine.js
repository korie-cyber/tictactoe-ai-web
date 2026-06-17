import { getAvailableMoves, checkWinner, isBoardFull, opponent } from './gameEngine.js';

function minimax(board, depth, isMaximizing, alpha, beta, aiPlayer) {
  const humanPlayer = opponent(aiPlayer);
  const result = checkWinner(board);

  if (result) {
    return result.winner === aiPlayer ? 10 - depth : depth - 10;
  }
  if (isBoardFull(board)) return 0;

  const moves = getAvailableMoves(board);

  if (isMaximizing) {
    let best = -Infinity;
    for (const move of moves) {
      board[move] = aiPlayer;
      best = Math.max(best, minimax(board, depth + 1, false, alpha, beta, aiPlayer));
      board[move] = null;
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = Infinity;
    for (const move of moves) {
      board[move] = humanPlayer;
      best = Math.min(best, minimax(board, depth + 1, true, alpha, beta, aiPlayer));
      board[move] = null;
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

function getBestMove(board, aiPlayer) {
  const moves = getAvailableMoves(board);
  let bestScore = -Infinity;
  let bestMove = moves[0];

  for (const move of moves) {
    board[move] = aiPlayer;
    const score = minimax(board, 0, false, -Infinity, Infinity, aiPlayer);
    board[move] = null;
    if (score > bestScore) {
      bestScore = score;
      bestMove = move;
    }
  }
  return bestMove;
}

function getRandomMove(board) {
  const moves = getAvailableMoves(board);
  return moves[Math.floor(Math.random() * moves.length)];
}

function getBlockingOrWinningMove(board, player) {
  const moves = getAvailableMoves(board);
  const opp = opponent(player);

  for (const move of moves) {
    board[move] = player;
    if (checkWinner(board)) { board[move] = null; return move; }
    board[move] = null;
  }
  for (const move of moves) {
    board[move] = opp;
    if (checkWinner(board)) { board[move] = null; return move; }
    board[move] = null;
  }
  return null;
}

export function getAIMove(board, aiPlayer, difficulty) {
  const moves = getAvailableMoves(board);
  if (moves.length === 0) return null;

  switch (difficulty) {
    case 'easy': {
      const tactical = getBlockingOrWinningMove(board, aiPlayer);
      if (tactical !== null && Math.random() < 0.3) return tactical;
      return getRandomMove(board);
    }

    case 'medium': {
      const tactical = getBlockingOrWinningMove(board, aiPlayer);
      if (tactical !== null) return tactical;
      if (Math.random() < 0.4) return getBestMove(board, aiPlayer);
      if (board[4] === null && Math.random() < 0.6) return 4;
      return getRandomMove(board);
    }

    case 'hard':
    default:
      return getBestMove(board, aiPlayer);
  }
}
