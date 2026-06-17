import { createInitialState, reduce } from './gameState.js';
import { WIN_PATTERNS } from './gameEngine.js';
import {
  animatePiecePlacement, animateWinLine, animateWinCells,
  animateScreenShake, animateModalIn, animateModalOut,
  animateBoardClear, animateBoardIn, animateScorePop, pulseStreakIcon,
} from './animations.js';

let state = createInitialState('X', 'medium');
let aiMoveQueued = false;

// ── DOM refs ──
const $ = (s, p) => (p || document).querySelector(s);
const $$ = (s, p) => [...(p || document).querySelectorAll(s)];

const boardEl = $('#board');
const cells = $$('.cell', boardEl);
const turnText = $('#turn-text');
const scoreEls = {
  human: $('#score-human'),
  ai: $('#score-ai'),
  draw: $('#score-draw'),
};
const streakBadge = $('#streak-badge');
const streakCount = $('#streak-count');
const overlay = $('#result-overlay');
const modal = $('#result-modal');
const resultBadge = $('#result-badge-piece');
const resultTitle = $('#result-title');
const resultSubtitle = $('#result-subtitle');
const winLineContainer = $('#win-line-container');
const boardWrapper = $('#board-wrapper');

// Segmented controls
const markerBtns = $$('[data-marker]');
const diffBtns = $$('[data-diff]');
const markerSlider = $('#marker-slider');
const diffSlider = $('#diff-slider');

// ── Render helpers ──
function renderBoard() {
  cells.forEach((cell, i) => {
    const val = state.board[i];
    cell.classList.toggle('occupied', val !== null);
    cell.classList.toggle('game-over', state.phase !== 'playing');
    cell.setAttribute('aria-label',
      val ? `Cell ${i + 1}: ${val}` : `Cell ${i + 1}: empty`);
    cell.setAttribute('aria-disabled', val !== null || state.phase !== 'playing' ? 'true' : 'false');

    const existing = cell.querySelector('.piece');
    if (val && !existing) {
      const piece = document.createElement('div');
      piece.className = `piece piece-${val.toLowerCase()}`;
      cell.appendChild(piece);
      if (i === state.lastPlacedIndex) {
        animatePiecePlacement(cell);
        tryHaptic(10);
      }
    } else if (!val && existing) {
      existing.remove();
    }
  });
}

function renderScores() {
  const prev = { ...scoreEls };
  Object.entries(scoreEls).forEach(([key, el]) => {
    const val = state.scores[key];
    if (el.textContent !== String(val)) {
      el.textContent = val;
      animateScorePop(el);
    }
  });

  // Leading indicator
  const cards = $$('.score-card');
  cards.forEach(c => c.classList.remove('leading'));
  if (state.scores.human > state.scores.ai) {
    cards[0].classList.add('leading');
  } else if (state.scores.ai > state.scores.human) {
    cards[2].classList.add('leading');
  }

  // Streak — hide entirely when zero
  if (state.streak > 0) {
    streakBadge.hidden = false;
    streakBadge.classList.add('active');
    streakCount.textContent = state.streak;
    pulseStreakIcon(streakBadge);
  } else {
    streakBadge.hidden = true;
    streakBadge.classList.remove('active');
  }
}

function renderTurn() {
  if (state.phase !== 'playing') {
    turnText.textContent = '';
    return;
  }
  turnText.textContent = state.currentTurn === state.humanMarker
    ? 'YOUR TURN' : 'AI THINKING';
}

function renderSegmented() {
  markerBtns.forEach((btn, i) => {
    const active = btn.dataset.marker === state.humanMarker;
    btn.setAttribute('aria-pressed', active);
  });
  const markerIdx = state.humanMarker === 'X' ? 0 : 1;
  const markerBtnW = markerBtns[0].offsetWidth;
  markerSlider.style.width = markerBtnW + 'px';
  markerSlider.style.transform = `translateX(${markerIdx * markerBtnW}px)`;

  diffBtns.forEach(btn => {
    const active = btn.dataset.diff === state.difficulty;
    btn.setAttribute('aria-pressed', active);
  });
  const diffIdx = ['easy', 'medium', 'hard'].indexOf(state.difficulty);
  const diffBtnW = diffBtns[0].offsetWidth;
  diffSlider.style.width = diffBtnW + 'px';
  diffSlider.style.transform = `translateX(${diffIdx * diffBtnW}px)`;
}

function render() {
  renderBoard();
  renderScores();
  renderTurn();
  renderSegmented();
}

// ── Dispatch ──
function dispatch(action) {
  state = reduce(state, action);
  render();
  handlePhase();
}

function handlePhase() {
  if (state.phase === 'playing' && state.currentTurn === state.aiMarker && !aiMoveQueued) {
    aiMoveQueued = true;
    requestAnimationFrame(() => {
      dispatch({ type: 'AI_MOVE' });
      aiMoveQueued = false;
    });
  }

  if (state.phase === 'won' || state.phase === 'lost' || state.phase === 'draw') {
    onGameEnd();
  }
}

async function onGameEnd() {
  if (state.winLine) {
    const lineEl = drawWinLine(state.winLine);
    await animateWinLine(lineEl);
    const winCells = state.winLine.map(i => cells[i]);
    animateWinCells(winCells);
    animateScreenShake(boardWrapper);
    tryHaptic(30);
  } else {
    tryHaptic(15);
  }

  await delay(800);
  showResult();
}

function showResult() {
  let title, subtitle, pieceClass;
  if (state.phase === 'won') {
    title = 'You Win';
    subtitle = state.streak > 1 ? `${state.streak} win streak!` : 'Well played!';
    pieceClass = `piece-${state.humanMarker.toLowerCase()}`;
  } else if (state.phase === 'lost') {
    title = 'AI Wins';
    subtitle = 'Better luck next time';
    pieceClass = `piece-${state.aiMarker.toLowerCase()}`;
  } else {
    title = "It's a Draw";
    subtitle = 'Evenly matched';
    pieceClass = '';
  }

  resultTitle.textContent = title;
  resultSubtitle.textContent = subtitle;
  resultBadge.className = `piece ${pieceClass}`;
  overlay.style.visibility = 'visible';
  animateModalIn(overlay);
}

// ── Win line geometry ──
function drawWinLine(pattern) {
  winLineContainer.innerHTML = '';
  const [a, , c] = pattern;
  const cellA = cells[a];
  const cellC = cells[c];
  const boardRect = boardEl.getBoundingClientRect();
  const rectA = cellA.getBoundingClientRect();
  const rectC = cellC.getBoundingClientRect();

  const x1 = rectA.left + rectA.width / 2 - boardRect.left;
  const y1 = rectA.top + rectA.height / 2 - boardRect.top;
  const x2 = rectC.left + rectC.width / 2 - boardRect.left;
  const y2 = rectC.top + rectC.height / 2 - boardRect.top;

  const length = Math.hypot(x2 - x1, y2 - y1);
  const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

  const line = document.createElement('div');
  line.className = 'win-line';
  line.style.width = length + 'px';
  line.style.left = x1 + 'px';
  line.style.top = y1 + 'px';
  line.style.transform = `rotate(${angle}deg)`;
  winLineContainer.appendChild(line);
  return line;
}

// ── New game ──
async function startNewGame() {
  if (overlay.style.visibility === 'visible') {
    await animateModalOut(overlay);
  }
  await animateBoardClear(cells);
  winLineContainer.innerHTML = '';
  cells.forEach(cell => {
    const piece = cell.querySelector('.piece');
    if (piece) piece.remove();
    cell.classList.remove('occupied', 'game-over');
    cell.style.boxShadow = '';
    cell.style.opacity = '';
    cell.style.transform = '';
  });
  dispatch({ type: 'NEW_GAME' });
  await animateBoardIn(cells);
}

// ── Haptics ──
function tryHaptic(duration) {
  try { navigator.vibrate?.(duration); } catch { /* requires user gesture */ }
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ── Event binding ──
cells.forEach((cell, i) => {
  cell.addEventListener('click', () => {
    if (state.currentTurn === state.humanMarker && state.phase === 'playing') {
      dispatch({ type: 'HUMAN_MOVE', index: i });
    }
  });
  cell.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (state.currentTurn === state.humanMarker && state.phase === 'playing') {
        dispatch({ type: 'HUMAN_MOVE', index: i });
      }
    }
    // Arrow key navigation
    let target = null;
    const row = Math.floor(i / 3);
    const col = i % 3;
    if (e.key === 'ArrowRight' && col < 2) target = i + 1;
    if (e.key === 'ArrowLeft' && col > 0) target = i - 1;
    if (e.key === 'ArrowDown' && row < 2) target = i + 3;
    if (e.key === 'ArrowUp' && row > 0) target = i - 3;
    if (target !== null) {
      e.preventDefault();
      cells[target].focus();
    }
  });
});

markerBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    dispatch({ type: 'SET_MARKER', marker: btn.dataset.marker });
  });
});

diffBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    dispatch({ type: 'SET_DIFFICULTY', difficulty: btn.dataset.diff });
  });
});

$('#btn-new-game').addEventListener('click', startNewGame);
$('#btn-play-again').addEventListener('click', startNewGame);
$('#btn-change-diff').addEventListener('click', async () => {
  await animateModalOut(overlay);
});

// ── Init ──
render();
handlePhase();
