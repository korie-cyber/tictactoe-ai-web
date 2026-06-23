# Tic-Tac-Toe vs AI

[![Live Demo](https://img.shields.io/badge/Live-tictactoe--ai--tau.vercel.app-38BDF8?style=flat-square)](https://tictactoe-ai-tau.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A premium tic-tac-toe game with three AI difficulty tiers, built as a pure client-side static site with a dark circuit-board aesthetic and frosted-glass UI.

## Play it

**[tictactoe-ai-tau.vercel.app](https://tictactoe-ai-tau.vercel.app)**

## Features

- **Three AI difficulties** — Easy (random), Medium (minimax with mistakes), Hard (full minimax with alpha-beta pruning). Genuinely different behavior at each tier.
- **Frosted-glass UI** — `backdrop-filter` blur over an animated circuit-board SVG background with traveling cyan neon pulses and pulsing glow nodes.
- **Fully client-side** — Zero server dependencies. Minimax runs in the browser in microseconds. Deployed as a static site on Vercel.
- **Responsive down to 320px** — Tested across 13 real device profiles (iPhone SE through iPad Air, small Android through Pro Max). Height-adaptive layout fits within mobile browser chrome with no scrolling.
- **Accessible** — Full keyboard navigation (tab + arrow keys + enter/space), ARIA roles and labels, visible focus states, `prefers-reduced-motion` support.
- **Streak tracking** — Win streak counter with animated badge, score persistence via localStorage.
- **Tactile interactions** — GSAP-powered piece placement spring animation, win-line draw, screen shake, staggered board clear/enter, optional haptic feedback via Vibration API.

## Tech Stack

| Layer | Tech |
|-------|------|
| UI | Vanilla JS (ES modules), CSS custom properties, GSAP |
| Game engine | Pure functions: board state, win/draw detection, valid moves |
| AI engine | Minimax with alpha-beta pruning, difficulty-scaled error injection |
| Background | Procedurally generated SVG circuit traces, CSS `stroke-dashoffset` animation |
| Glass effect | `backdrop-filter: blur(20px) saturate(120%)` with `@supports` fallback |
| Deploy | Vercel static site, zero build step |

## Project Structure

```
tictactoe-ai/
├── index.html          # Single-page app markup
├── css/
│   └── styles.css      # Design system, glass tokens, responsive breakpoints
├── js/
│   ├── app.js          # DOM controller, event binding, render loop
│   ├── gameEngine.js   # Pure board logic: win/draw/valid moves
│   ├── aiEngine.js     # Minimax AI with difficulty tiers
│   ├── gameState.js    # Centralized reducer + localStorage persistence
│   ├── animations.js   # GSAP animation helpers
│   └── circuitBg.js    # Procedural circuit-board SVG generator
└── vercel.json         # Static deployment config
```

## Run Locally

```bash
# Any static file server works — no build step needed
npx serve .
# or
python -m http.server 8080
```

Open `http://localhost:8080` (or whatever port your server uses).

## License

MIT
