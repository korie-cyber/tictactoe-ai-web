export function initCircuitBackground() {
  const container = document.querySelector('.circuit-bg');
  if (!container) return;

  function generate() {
    const W = window.innerWidth;
    const H = window.innerHeight;
    const cx = W / 2;
    const cy = H / 2;

    function tracePath(points) {
      return 'M' + points.map(p => `${p[0]} ${p[1]}`).join(' L');
    }

    function routeToEdge(startX, startY, dirX, dirY, steps) {
      const pts = [[startX, startY]];
      let x = startX, y = startY;
      const segMin = Math.min(W, H) * 0.06;
      const segMax = Math.min(W, H) * 0.15;

      for (let i = 0; i < steps; i++) {
        const seg = segMin + Math.random() * (segMax - segMin);
        if (i % 2 === 0) {
          x += dirX * seg;
        } else {
          y += dirY * seg;
        }
        x = Math.max(-20, Math.min(W + 20, x));
        y = Math.max(-20, Math.min(H + 20, y));
        pts.push([Math.round(x), Math.round(y)]);
      }
      return pts;
    }

    const routes = [];
    const directions = [
      [-1, -1], [0, -1], [1, -1],
      [-1, 0],           [1, 0],
      [-1, 1],  [0, 1],  [1, 1],
    ];

    for (const [dx, dy] of directions) {
      routes.push(routeToEdge(cx, cy, dx, dy, 8));
      const ox = cx + (dx * W * 0.05) + (dy * W * 0.03);
      const oy = cy + (dy * H * 0.05) - (dx * H * 0.03);
      routes.push(routeToEdge(ox, oy, dx, dy, 7));
    }

    const branchRoutes = [];
    for (const route of routes) {
      if (route.length > 3 && Math.random() < 0.7) {
        const branchIdx = 2 + Math.floor(Math.random() * (route.length - 3));
        const bp = route[branchIdx];
        const bdx = Math.random() < 0.5 ? 1 : -1;
        const bdy = Math.random() < 0.5 ? 1 : -1;
        branchRoutes.push(routeToEdge(bp[0], bp[1], bdx, bdy, 5));
      }
    }
    routes.push(...branchRoutes);

    const edgeSpacing = Math.min(W, H) * 0.12;
    for (let i = 0; i < 6; i++) {
      const side = i % 4;
      let sx, sy, dx, dy;
      if (side === 0) { sx = -10; sy = edgeSpacing * (1 + i); dx = 1; dy = (Math.random() - 0.5) * 0.6; }
      else if (side === 1) { sx = W + 10; sy = H - edgeSpacing * (1 + i); dx = -1; dy = (Math.random() - 0.5) * 0.6; }
      else if (side === 2) { sx = edgeSpacing * (2 + i); sy = -10; dx = (Math.random() - 0.5) * 0.6; dy = 1; }
      else { sx = W - edgeSpacing * (1 + i); sy = H + 10; dx = (Math.random() - 0.5) * 0.6; dy = -1; }
      routes.push(routeToEdge(sx, sy, dx, dy, 7));
    }

    const allPaths = routes.map(r => tracePath(r));

    const glowClasses = [
      'trace-glow', 'trace-glow-2', 'trace-glow-3', 'trace-glow-4',
      'trace-glow-5', 'trace-glow-6', 'trace-glow-7', 'trace-glow-8',
      'trace-glow-9', 'trace-glow-10', 'trace-glow-11', 'trace-glow-12',
      'trace-glow-13', 'trace-glow-14',
    ];

    const nodes = [];
    for (const route of routes) {
      for (let i = 1; i < route.length - 1; i++) {
        if (Math.random() < 0.35) {
          nodes.push(route[i]);
        }
      }
    }
    nodes.push([cx, cy]);

    let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">
      <defs>
        <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <filter id="node-bloom"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <pattern id="dot-grid" width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="12" cy="12" r="0.5" fill="rgba(125,211,252,0.07)"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dot-grid)"/>
      <g stroke="#1E293B" stroke-width="1" fill="none" stroke-linecap="round" stroke-linejoin="round">`;

    for (const d of allPaths) {
      svg += `<path d="${d}"/>`;
    }
    svg += `</g>`;

    svg += `<g stroke="#1A2332" stroke-width="0.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.6">`;
    for (const d of allPaths) {
      svg += `<path d="${d}" stroke-dasharray="2 6"/>`;
    }
    svg += `</g>`;

    svg += `<g filter="url(#glow)" fill="none" stroke-linecap="round" stroke-linejoin="round">`;
    const animatedCount = Math.min(allPaths.length, glowClasses.length);
    for (let i = 0; i < animatedCount; i++) {
      const stroke = i % 2 === 0 ? '#38BDF8' : '#7DD3FC';
      const sw = i < 8 ? 1.5 : 1;
      svg += `<path class="${glowClasses[i]}" stroke="${stroke}" stroke-width="${sw}" d="${allPaths[i]}"/>`;
    }
    svg += `</g>`;

    svg += `<g filter="url(#node-bloom)">`;
    for (let i = 0; i < nodes.length; i++) {
      const [nx, ny] = nodes[i];
      const r = i === nodes.length - 1 ? 3 : 1.5 + Math.random() * 1.5;
      const fill = i % 2 === 0 ? '#38BDF8' : '#7DD3FC';
      const delay = -(i * 0.7 % 8).toFixed(1);
      svg += `<circle class="node-glow" cx="${nx}" cy="${ny}" r="${r}" fill="${fill}" style="animation-delay:${delay}s"/>`;
    }
    svg += `</g></svg>`;

    container.innerHTML = svg;
  }

  generate();

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(generate, 300);
  });
}
