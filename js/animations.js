const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function dur(ms) {
  return reducedMotion ? 0 : ms / 1000;
}

export function animatePiecePlacement(cell) {
  if (reducedMotion) {
    cell.style.opacity = '1';
    return Promise.resolve();
  }
  return new Promise(resolve => {
    gsap.fromTo(cell.querySelector('.piece'),
      { scale: 0.6, opacity: 0 },
      {
        scale: 1, opacity: 1, duration: 0.2,
        ease: 'back.out(1.7)',
        onComplete: resolve,
      }
    );
    gsap.fromTo(cell,
      { boxShadow: '0 0 0px rgba(56,189,248,0)' },
      {
        boxShadow: '0 0 20px rgba(56,189,248,0.5), 0 0 40px rgba(125,211,252,0.3)',
        duration: 0.3,
        ease: 'power2.out',
        onComplete() {
          gsap.to(cell, {
            boxShadow: '0 0 6px rgba(56,189,248,0.1), 0 0 12px rgba(125,211,252,0.05)',
            duration: 0.6,
            ease: 'power2.inOut',
          });
        }
      }
    );
  });
}

export function animateWinLine(lineEl) {
  if (reducedMotion) {
    lineEl.style.opacity = '1';
    return Promise.resolve();
  }
  return new Promise(resolve => {
    gsap.fromTo(lineEl,
      { scaleX: 0, opacity: 0 },
      { scaleX: 1, opacity: 1, duration: 0.4, ease: 'power3.out', onComplete: resolve }
    );
  });
}

export function animateWinCells(cells) {
  if (reducedMotion) return;
  gsap.to(cells, {
    scale: 1.05,
    duration: 0.15,
    ease: 'power2.out',
    yoyo: true,
    repeat: 1,
    stagger: 0.05,
  });
}

export function animateScreenShake(container) {
  if (reducedMotion) return;
  gsap.to(container, {
    x: 3, duration: 0.05, ease: 'power2.inOut',
    yoyo: true, repeat: 5,
    onComplete() { gsap.set(container, { x: 0 }); }
  });
}

export function animateModalIn(modal) {
  if (reducedMotion) {
    modal.style.opacity = '1';
    modal.style.visibility = 'visible';
    return;
  }
  gsap.fromTo(modal,
    { scale: 0.95, opacity: 0, visibility: 'visible' },
    { scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(1.4)' }
  );
}

export function animateModalOut(modal) {
  if (reducedMotion) {
    modal.style.opacity = '0';
    modal.style.visibility = 'hidden';
    return Promise.resolve();
  }
  return new Promise(resolve => {
    gsap.to(modal, {
      scale: 0.95, opacity: 0, duration: 0.2, ease: 'power2.in',
      onComplete() {
        modal.style.visibility = 'hidden';
        resolve();
      }
    });
  });
}

export function animateBoardClear(cells) {
  if (reducedMotion) {
    cells.forEach(c => { c.style.opacity = '0'; });
    return Promise.resolve();
  }
  return new Promise(resolve => {
    gsap.to(cells, {
      opacity: 0,
      scale: 0.8,
      duration: 0.15,
      stagger: 0.02,
      ease: 'power2.in',
      onComplete: resolve,
    });
  });
}

export function animateBoardIn(cells) {
  if (reducedMotion) {
    cells.forEach(c => { c.style.opacity = '1'; c.style.transform = ''; });
    return Promise.resolve();
  }
  return new Promise(resolve => {
    gsap.fromTo(cells,
      { opacity: 0, scale: 0.9 },
      {
        opacity: 1, scale: 1, duration: 0.2,
        stagger: 0.02, ease: 'back.out(1.2)',
        onComplete: resolve,
      }
    );
  });
}

export function animateScorePop(el) {
  if (reducedMotion) return;
  gsap.fromTo(el,
    { scale: 1.3 },
    { scale: 1, duration: 0.3, ease: 'back.out(2)' }
  );
}

export function pulseStreakIcon(el) {
  if (reducedMotion) return;
  gsap.fromTo(el,
    { scale: 1 },
    { scale: 1.2, duration: 0.15, ease: 'power2.out', yoyo: true, repeat: 1 }
  );
}
