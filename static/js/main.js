/* Jeannot Tsirenge Portfolio — main.js */

(() => {
  'use strict';

  // ---------------------------------------------------------
  // Header scroll behaviour
  // ---------------------------------------------------------
  const header = document.getElementById('site-header');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // initial
  }

  // ---------------------------------------------------------
  // Mobile nav toggle
  // ---------------------------------------------------------
  const toggle = document.querySelector('.nav__toggle');
  const navLinks = document.querySelector('.nav__links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });

    // Close on Escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && navLinks.classList.contains('is-open')) {
        navLinks.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        toggle.focus();
      }
    });
  }

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
    const testimonials = Array.from(track.querySelectorAll('.testimonial'));
    if (testimonials.length > 1) {
      let current = 0;
      const show = idx => {
        testimonials[current].classList.add('testimonial--hidden');
        current = (idx + testimonials.length) % testimonials.length;
        testimonials[current].classList.remove('testimonial--hidden');
      };
      setInterval(() => show(current + 1), 5500);
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

})();
