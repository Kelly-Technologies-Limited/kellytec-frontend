(function initRevealOnScroll() {
  const revealTargets = document.querySelectorAll(
    '.hero-title, .section-eyebrow, .section-title, .team-card, .contact-address, .contact-mail, .strategies-viz'
  );
  revealTargets.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealTargets.forEach(el => io.observe(el));
})();
