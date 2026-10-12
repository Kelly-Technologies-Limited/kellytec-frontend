// Volatility surface (right side of Strategies)
(function renderVolSurface() {
  const svg = document.querySelector('.vol-surface');
  if (!svg) return;
  const NS = 'http://www.w3.org/2000/svg';

  const nK = 13, nT = 9;
  const sx = 23, sy = 22, sz = 200;
  const rad = 28 * Math.PI / 180;
  const cosA = Math.cos(rad), sinA = Math.sin(rad);
  const ox = 45, oy = 295;

  // SPX-like skew with off-ATM hump + subtle organic ripple (not a textbook surface)
  function h(i, j) {
    const K = (i / (nK - 1)) * 2 - 1;
    const T = j / (nT - 1);
    const atm = 0.20 + 0.04 * T;                                    // mild contango
    const left  = Math.pow(Math.max(-K, 0), 1.3);
    const right = Math.pow(Math.max( K, 0), 2);
    const skew = (0.48 * left + 0.12 * right) * (1 - 0.30 * T);     // flattens with T
    const d = K + 0.25;
    const hump = 0.06 * Math.exp(-d * d / 0.15) * (1 - 0.5 * T);    // slight near-ATM bump
    const ripple = 0.018 * Math.sin(4.5 * K + 2.2 * T + 1.1);       // imperfection
    return atm + skew + hump + ripple;
  }

  function project(i, j) {
    return [
      ox + i * sx + j * cosA * sy,
      oy - j * sinA * sy - h(i, j) * sz,
    ];
  }
  function projectFloor(i, j) {
    return [ox + i * sx + j * cosA * sy, oy - j * sinA * sy];
  }

  // Catmull-Rom -> cubic bezier
  function smoothPath(pts) {
    if (pts.length < 2) return '';
    let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(0, i - 1)];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[Math.min(pts.length - 1, i + 2)];
      const c1x = p1[0] + (p2[0] - p0[0]) / 6;
      const c1y = p1[1] + (p2[1] - p0[1]) / 6;
      const c2x = p2[0] - (p3[0] - p1[0]) / 6;
      const c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += `C${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
    }
    return d;
  }

  function addPath(attrs) {
    const el = document.createElementNS(NS, 'path');
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    svg.appendChild(el);
  }

  // Build a closed "wall" polygon from parallel top/bottom point arrays
  function wallPath(top, bottom) {
    let d = `M${top[0][0].toFixed(1)} ${top[0][1].toFixed(1)}`;
    for (let i = 1; i < top.length; i++) {
      d += `L${top[i][0].toFixed(1)} ${top[i][1].toFixed(1)}`;
    }
    for (let i = bottom.length - 1; i >= 0; i--) {
      d += `L${bottom[i][0].toFixed(1)} ${bottom[i][1].toFixed(1)}`;
    }
    return d + 'Z';
  }

  // Bottom floor plane (filled parallelogram at h=0) - drawn first, sits under everything
  const floor4 = [
    projectFloor(0, 0),
    projectFloor(nK - 1, 0),
    projectFloor(nK - 1, nT - 1),
    projectFloor(0, nT - 1),
  ];
  addPath({
    class: 'wall wall-bottom',
    d: `M${floor4[0][0].toFixed(1)} ${floor4[0][1].toFixed(1)}` +
       `L${floor4[1][0].toFixed(1)} ${floor4[1][1].toFixed(1)}` +
       `L${floor4[2][0].toFixed(1)} ${floor4[2][1].toFixed(1)}` +
       `L${floor4[3][0].toFixed(1)} ${floor4[3][1].toFixed(1)}Z`,
  });

  // Left side wall (K=-1 plane) - connects the surface's left edge to the floor
  const leftTop = [], leftBot = [];
  for (let j = 0; j < nT; j++) { leftTop.push(project(0, j)); leftBot.push(projectFloor(0, j)); }
  addPath({ class: 'wall wall-left', d: wallPath(leftTop, leftBot) });

  // Smile curves (constant T), drawn back-to-front so the front sits on top
  for (let j = nT - 1; j >= 0; j--) {
    const pts = [];
    for (let i = 0; i < nK; i++) pts.push(project(i, j));
    const t = j / (nT - 1);                     // 0 front, 1 back
    const op = 0.30 + (1 - t) * 0.55;
    const sw = 0.7  + (1 - t) * 0.5;
    addPath({
      class: 'smile',
      d: smoothPath(pts),
      'stroke-width': sw.toFixed(2),
      'stroke-opacity': op.toFixed(3),
    });
  }

  // Expiry ribs (constant K), edges brighter than center
  for (let i = 0; i < nK; i++) {
    const pts = [];
    for (let j = 0; j < nT; j++) pts.push(project(i, j));
    const edge = Math.abs((i - (nK - 1) / 2) / ((nK - 1) / 2));
    const op = 0.20 + edge * 0.40;
    addPath({
      class: 'rib',
      d: smoothPath(pts),
      'stroke-width': 0.65,
      'stroke-opacity': op.toFixed(3),
    });
  }
})();
