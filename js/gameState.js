import { createBoard, applyMove, getGameResult, opponent } from './gameEngine.js';
import { getAIMove } from './aiEngine.js';

const STORAGE_KEY = 'tictactoe_state';

function loadPersisted() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const d = JSON.parse(raw);
      return {
        scores: d.scores || { human: 0, ai: 0, draw: 0 },
        streak: d.streak || 0,
        bestStreak: d.bestStreak || 0,
      };
    }
  } catch { /* ignore */ }
  return { scores: { human: 0, ai: 0, draw: 0 }, streak: 0, bestStreak: 0 };
}

function persist(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      scores: state.scores,
      streak: state.streak,
      bestStreak: state.bestStreak,
    }));
  } catch { /* ignore */ }
}

export function createInitialState(humanMarker = 'X', difficulty = 'medium') {
  const persisted = loadPersisted();
  return {
    board: createBoard(),
    humanMarker,
    aiMarker: opponent(humanMarker),
    difficulty,
    currentTurn: 'X',
    phase: 'playing',
    winLine: null,
    scores: persisted.scores,
    streak: persisted.streak,
    bestStreak: persisted.bestStreak,
    lastPlacedIndex: null,
  };
}

export function reduce(state, action) {
  switch (action.type) {
    case 'HUMAN_MOVE': {
      if (state.phase !== 'playing') return state;
      if (state.currentTurn !== state.humanMarker) return state;
      const newBoard = applyMove(state.board, action.index, state.humanMarker);
      if (!newBoard) return state;

      const result = getGameResult(newBoard);
      if (result.status === 'win') {
        const newStreak = state.streak + 1;
        const newBest = Math.max(state.bestStreak, newStreak);
        const next = {
          ...state,
          board: newBoard,
          phase: 'won',
          winLine: result.line,
          lastPlacedIndex: action.index,
          scores: { ...state.scores, human: state.scores.human + 1 },
          streak: newStreak,
          bestStreak: newBest,
        };
        persist(next);
        return next;
      }
      if (result.status === 'draw') {
        const next = {
          ...state,
          board: newBoard,
          phase: 'draw',
          lastPlacedIndex: action.index,
          scores: { ...state.scores, draw: state.scores.draw + 1 },
          streak: 0,
        };
        persist(next);
        return next;
      }
      return {
        ...state,
        board: newBoard,
        currentTurn: state.aiMarker,
        lastPlacedIndex: action.index,
      };
    }

    case 'AI_MOVE': {
      if (state.phase !== 'playing') return state;
      if (state.currentTurn !== state.aiMarker) return state;
      const move = getAIMove(state.board.slice(), state.aiMarker, state.difficulty);
      if (move === null) return state;
      const newBoard = applyMove(state.board, move, state.aiMarker);
      if (!newBoard) return state;

      const result = getGameResult(newBoard);
      if (result.status === 'win') {
        const next = {
          ...state,
          board: newBoard,
          phase: 'lost',
          winLine: result.line,
          lastPlacedIndex: move,
          scores: { ...state.scores, ai: state.scores.ai + 1 },
          streak: 0,
        };
        persist(next);
        return next;
      }
      if (result.status === 'draw') {
        const next = {
          ...state,
          board: newBoard,
          phase: 'draw',
          lastPlacedIndex: move,
          scores: { ...state.scores, draw: state.scores.draw + 1 },
          streak: 0,
        };
        persist(next);
        return next;
      }
      return {
        ...state,
        board: newBoard,
        currentTurn: state.humanMarker,
        lastPlacedIndex: move,
      };
    }

    case 'NEW_GAME': {
      return {
        ...state,
        board: createBoard(),
        currentTurn: 'X',
        phase: 'playing',
        winLine: null,
        lastPlacedIndex: null,
      };
    }

    case 'SET_MARKER': {
      const s = {
        ...state,
        humanMarker: action.marker,
        aiMarker: opponent(action.marker),
        board: createBoard(),
        currentTurn: 'X',
        phase: 'playing',
        winLine: null,
        lastPlacedIndex: null,
      };
      return s;
    }

    case 'SET_DIFFICULTY': {
      return {
        ...state,
        difficulty: action.difficulty,
        board: createBoard(),
        currentTurn: 'X',
        phase: 'playing',
        winLine: null,
        lastPlacedIndex: null,
      };
    }

    default:
      return state;
  }
}
