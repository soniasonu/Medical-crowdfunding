/* Nypunya Worker App – Dashboard JS */

// Sidebar hamburger toggle
document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.querySelector('.hamburger');
  const sidebar   = document.querySelector('.sidebar');
  const overlay   = document.getElementById('sidebar-overlay');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // Animated number counters
  document.querySelectorAll('.value[data-count]').forEach(el => {
    const target = parseInt(el.getAttribute('data-count'), 10);
    let current  = 0;
    const step   = Math.max(1, Math.ceil(target / 30));
    const timer  = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });

  // Highlight active nav item based on hash
  function highlightNav() {
    const hash = window.location.hash;
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === hash || a.getAttribute('href') === window.location.pathname);
    });
  }
  highlightNav();
  window.addEventListener('hashchange', highlightNav);

  // Section observer for active nav
  const sections = document.querySelectorAll('[data-section]');
  if (sections.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          document.querySelectorAll('.sidebar-nav .nav-item').forEach(a => {
            a.classList.toggle('active', a.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-40% 0px -50% 0px' });
    sections.forEach(s => io.observe(s));
  }

  // Auto hide flash messages
  document.querySelectorAll('.message').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 4500);
  });

  // Role tab switching (login page)
  document.querySelectorAll('.role-tab').forEach(tab => {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.role-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const roleInput = document.getElementById('role-input');
      if (roleInput) roleInput.value = this.dataset.role;
    });
  });
});
