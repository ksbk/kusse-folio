/* Jeannot Tsirenge Portfolio — main.js */

(() => {
  'use strict';

  // ---------------------------------------------------------
  // Scroll reveal
  // ---------------------------------------------------------
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  } else {
    // Fallback: show all immediately
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
  }

  // ---------------------------------------------------------
  // Testimonial rotator
  // ---------------------------------------------------------
  const track = document.querySelector('.testimonials-track');
  if (track) {
    const items = Array.from(track.querySelectorAll('.testimonial'));
    const dots = Array.from(document.querySelectorAll('.testimonials-dot'));
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (items.length > 1) {
      let current = 0;
      let timer = null;

      const show = idx => {
        items[current].classList.add('testimonial--hidden');
        dots[current]?.classList.remove('testimonials-dot--active');
        current = (idx + items.length) % items.length;
        items[current].classList.remove('testimonial--hidden');
        dots[current]?.classList.add('testimonials-dot--active');
      };

      const start = () => {
        if (!prefersReducedMotion && !timer) {
          timer = setInterval(() => show(current + 1), 5500);
        }
      };

      const stop = () => {
        clearInterval(timer);
        timer = null;
      };

      start();

      // Pause when the user is interacting with the section
      const section = track.closest('section');
      if (section) {
        section.addEventListener('mouseenter', stop, { passive: true });
        section.addEventListener('mouseleave', start, { passive: true });
        section.addEventListener('focusin', stop, { passive: true });
        section.addEventListener('focusout', start, { passive: true });
      }

      // Dot navigation
      dots.forEach((dot, i) => {
        dot.addEventListener('click', () => {
          stop();
          show(i);
          start();
        });
      });
    }
  }

  // ---------------------------------------------------------
  // Category filter — preserve scroll position on page load
  // ---------------------------------------------------------
  const filterBar = document.querySelector('.filter-bar__nav');
  if (filterBar) {
    const active = filterBar.querySelector('.filter-btn--active');
    if (active) {
      active.scrollIntoView({ block: 'nearest', inline: 'center' });
    }
  }

  // ---------------------------------------------------------
  // Form submit state
  // ---------------------------------------------------------
  document.querySelectorAll('form[data-submit-pending-label]').forEach(form => {
    form.addEventListener('submit', () => {
      const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
      if (!submitButton || submitButton.disabled) {
        return;
      }

      submitButton.dataset.originalLabel = submitButton.textContent;
      submitButton.textContent = form.dataset.submitPendingLabel;
      submitButton.disabled = true;
      submitButton.setAttribute('aria-disabled', 'true');
    });
  });

})();
