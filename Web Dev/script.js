const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');
const links = document.querySelectorAll('.nav-links a');
const reveals = document.querySelectorAll('.reveal');
const sections = document.querySelectorAll('main section[id]');
const loader = document.querySelector('.loader');
const cursorRing = document.querySelector('.cursor-ring');
const cursorDot = document.querySelector('.cursor-dot');
const magneticItems = document.querySelectorAll('.magnetic');
const filterBars = document.querySelectorAll('.filter-bar');
const projectCards = document.querySelectorAll('.project-card');
const previewButtons = document.querySelectorAll('.preview-trigger');
const previewModal = document.querySelector('.preview-modal');
const previewImage = document.querySelector('#previewImage');
const previewTag = document.querySelector('#previewTag');
const previewTitle = document.querySelector('#previewTitle');
const previewDescription = document.querySelector('#previewDescription');
const closeModalNodes = document.querySelectorAll('[data-close-modal]');
const glowA = document.querySelector('.glow-a');
const glowB = document.querySelector('.glow-b');
const bgGrid = document.querySelector('.bg-grid');
const contactForm = document.querySelector('#contactForm');
const contactSubmit = document.querySelector('#contactSubmit');
const contactStatus = document.querySelector('#contactStatus');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const hasFinePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
const defaultApiBaseUrl = window.location.hostname.includes('onrender.com')
  ? 'https://sam-portfolio-api.onrender.com'
  : 'http://127.0.0.1:8000';
const apiBaseUrl = window.API_BASE_URL || defaultApiBaseUrl;

const setContactStatus = (message, type = '') => {
  if (!contactStatus) {
    return;
  }

  contactStatus.textContent = message;
  contactStatus.classList.remove('success', 'error');
  if (type) {
    contactStatus.classList.add(type);
  }
};

if (contactForm) {
  contactForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    setContactStatus('');

    const formData = new FormData(contactForm);
    const payload = {
      name: String(formData.get('name') || '').trim(),
      email: String(formData.get('email') || '').trim(),
      subject: String(formData.get('subject') || '').trim(),
      message: String(formData.get('message') || '').trim(),
    };

    if (contactSubmit) {
      contactSubmit.disabled = true;
      contactSubmit.textContent = 'Sending...';
    }

    try {
      const response = await fetch(`${apiBaseUrl}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Unable to send message right now.');
      }

      setContactStatus(result.message || 'Message sent successfully.', 'success');
      contactForm.reset();
    } catch (error) {
      setContactStatus(error.message || 'Message failed. Please try again later.', 'error');
    } finally {
      if (contactSubmit) {
        contactSubmit.disabled = false;
        contactSubmit.textContent = 'Send Message';
      }
    }
  });
}

if (menuToggle && navLinks) {
  menuToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', String(isOpen));
  });
}

links.forEach((link) => {
  link.addEventListener('click', () => {
    if (navLinks) {
      navLinks.classList.remove('open');
    }
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'false');
    }
  });
});

window.addEventListener('load', () => {
  setTimeout(() => {
    document.body.classList.remove('is-loading');
    document.body.classList.add('loaded');
    if (loader) {
      loader.setAttribute('aria-hidden', 'true');
    }
  }, prefersReducedMotion ? 80 : 850);
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
      }
    });
  },
  { threshold: 0.16 }
);

reveals.forEach((item) => revealObserver.observe(item));

const stageSections = document.querySelectorAll('main .section');
stageSections.forEach((section) => {
  const stageItems = section.querySelectorAll('.hero-content, .hero-panel, .panel, .filter-bar, .project-card, .contact-panel, .contact-list');
  stageItems.forEach((item, index) => {
    item.classList.add('stage-item');
    item.style.setProperty('--stage-delay', `${index * 70}ms`);
    if (prefersReducedMotion) {
      item.classList.add('stage-in');
    }
  });
});

if (!prefersReducedMotion) {
  const stageObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || entry.target.dataset.staged === 'true') {
          return;
        }

        const stageItems = entry.target.querySelectorAll('.stage-item');
        stageItems.forEach((item) => item.classList.add('stage-in'));
        entry.target.dataset.staged = 'true';
      });
    },
    { threshold: 0.24 }
  );

  stageSections.forEach((section) => stageObserver.observe(section));
}

if (hasFinePointer && cursorRing && cursorDot) {
  document.body.classList.add('pointer-enabled');

  let ringX = 0;
  let ringY = 0;
  let mouseX = 0;
  let mouseY = 0;

  const moveCursor = () => {
    ringX += (mouseX - ringX) * 0.18;
    ringY += (mouseY - ringY) * 0.18;
    cursorDot.style.left = `${mouseX}px`;
    cursorDot.style.top = `${mouseY}px`;
    cursorRing.style.left = `${ringX}px`;
    cursorRing.style.top = `${ringY}px`;
    requestAnimationFrame(moveCursor);
  };

  window.addEventListener('mousemove', (event) => {
    mouseX = event.clientX;
    mouseY = event.clientY;
  });

  moveCursor();

  const interactiveNodes = document.querySelectorAll('a, button, .filter-btn, .project-card');
  interactiveNodes.forEach((node) => {
    node.addEventListener('mouseenter', () => {
      document.documentElement.style.setProperty('--cursor-scale', '1.45');
    });
    node.addEventListener('mouseleave', () => {
      document.documentElement.style.setProperty('--cursor-scale', '1');
    });
  });

  if (!prefersReducedMotion) {
    magneticItems.forEach((item) => {
      item.addEventListener('mousemove', (event) => {
        const rect = item.getBoundingClientRect();
        const x = event.clientX - rect.left - rect.width / 2;
        const y = event.clientY - rect.top - rect.height / 2;
        item.style.transform = `translate(${x * 0.12}px, ${y * 0.12}px)`;
      });

      item.addEventListener('mouseleave', () => {
        item.style.transform = 'translate(0, 0)';
      });
    });
  }
}

if (hasFinePointer && !prefersReducedMotion) {
  projectCards.forEach((card) => {
    card.addEventListener('mousemove', (event) => {
      if (card.classList.contains('is-hidden')) {
        return;
      }

      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      const rotateY = (x - 0.5) * 12;
      const rotateX = (0.5 - y) * 10;

      card.style.setProperty('--rx', `${rotateX}deg`);
      card.style.setProperty('--ry', `${rotateY}deg`);
    });

    card.addEventListener('mouseleave', () => {
      card.style.setProperty('--rx', '0deg');
      card.style.setProperty('--ry', '0deg');
    });
  });
}

filterBars.forEach((bar) => {
  const group = bar.dataset.filterGroup;
  const buttons = bar.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll(`.project-card[data-group="${group}"]`);

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;

      buttons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      cards.forEach((card) => {
        const matches = filter === 'all' || card.dataset.type === filter;
        if (matches) {
          if (card.classList.contains('is-hidden')) {
            card.classList.remove('is-hidden');
            card.classList.add('is-filtering-in');
            requestAnimationFrame(() => {
              card.classList.remove('is-filtering-in');
            });
          }
        } else if (!card.classList.contains('is-hidden')) {
          card.classList.add('is-filtering-out');
          card.style.setProperty('--rx', '0deg');
          card.style.setProperty('--ry', '0deg');
          window.setTimeout(() => {
            card.classList.remove('is-filtering-out');
            card.classList.add('is-hidden');
          }, 220);
        }
      });
    });
  });
});

const toneMap = {
  teal: ['#0a7ea4', '#0f766e'],
  gold: ['#f59e0b', '#d97706'],
  slate: ['#475569', '#1f2937'],
};

const buildPreviewSvg = (title, tag, toneKey) => {
  const colors = toneMap[toneKey] || toneMap.teal;
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700" role="img" aria-label="${title}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${colors[0]}"/>
      <stop offset="100%" stop-color="${colors[1]}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="700" fill="#d7e4f2"/>
  <rect x="90" y="70" rx="20" ry="20" width="1020" height="560" fill="#f8fbff" stroke="#9fb4c9" stroke-width="2"/>
  <rect x="90" y="70" rx="20" ry="20" width="1020" height="84" fill="url(#g)"/>
  <circle cx="140" cy="112" r="10" fill="#ffffff" fill-opacity="0.85"/>
  <circle cx="170" cy="112" r="10" fill="#ffffff" fill-opacity="0.72"/>
  <circle cx="200" cy="112" r="10" fill="#ffffff" fill-opacity="0.6"/>
  <text x="250" y="120" font-family="Arial, sans-serif" font-size="24" fill="#ffffff">${tag}</text>
  <rect x="140" y="200" width="620" height="38" rx="10" fill="#e9f2fc"/>
  <rect x="140" y="260" width="920" height="18" rx="9" fill="#d5e5f7"/>
  <rect x="140" y="295" width="870" height="18" rx="9" fill="#d5e5f7"/>
  <rect x="140" y="330" width="740" height="18" rx="9" fill="#d5e5f7"/>
  <rect x="805" y="200" width="255" height="200" rx="16" fill="url(#g)" fill-opacity="0.18"/>
  <text x="140" y="226" font-family="Arial, sans-serif" font-size="25" fill="#0f172a">${title}</text>
</svg>`;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
};

const openPreview = (button) => {
  if (!previewModal || !previewImage || !previewTag || !previewTitle || !previewDescription) {
    return;
  }

  const title = button.dataset.previewTitle || 'Project Preview';
  const tag = button.dataset.previewTag || 'Preview';
  const description = button.dataset.previewDescription || 'Project details.';
  const tone = button.dataset.previewTone || 'teal';

  previewTitle.textContent = title;
  previewTag.textContent = tag;
  previewDescription.textContent = description;
  previewImage.src = buildPreviewSvg(title, tag, tone);
  previewImage.alt = `${title} screenshot preview`;

  previewModal.classList.add('open');
  previewModal.setAttribute('aria-hidden', 'false');
  document.body.classList.add('modal-open');
};

const closePreview = () => {
  if (!previewModal) {
    return;
  }

  previewModal.classList.remove('open');
  previewModal.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('modal-open');
};

previewButtons.forEach((button) => {
  button.addEventListener('click', () => openPreview(button));
});

closeModalNodes.forEach((node) => {
  node.addEventListener('click', closePreview);
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closePreview();
  }
});

const setActiveLink = () => {
  const scrollY = window.scrollY + 120;

  sections.forEach((section) => {
    const top = section.offsetTop;
    const height = section.offsetHeight;
    const id = section.getAttribute('id');
    const navLink = document.querySelector(`.nav-links a[href="#${id}"]`);

    if (!navLink) {
      return;
    }

    if (scrollY >= top && scrollY < top + height) {
      navLink.classList.add('active');
    } else {
      navLink.classList.remove('active');
    }
  });
};

const updateSceneOnScroll = () => {
  const y = window.scrollY;
  document.body.classList.toggle('scrolled', y > 12);

  if (!prefersReducedMotion) {
    if (glowA) {
      glowA.style.setProperty('--parallax-y', `${y * -0.022}px`);
      glowA.style.setProperty('--parallax-x', `${y * -0.006}px`);
    }
    if (glowB) {
      glowB.style.setProperty('--parallax-y', `${y * 0.018}px`);
      glowB.style.setProperty('--parallax-x', `${y * 0.004}px`);
    }
    if (bgGrid) {
      bgGrid.style.setProperty('--grid-shift', `${y * -0.012}px`);
    }
  }
};

let scrollTicking = false;
const onScroll = () => {
  if (scrollTicking) {
    return;
  }

  scrollTicking = true;
  requestAnimationFrame(() => {
    setActiveLink();
    updateSceneOnScroll();
    scrollTicking = false;
  });
};

window.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('load', setActiveLink);
window.addEventListener('load', updateSceneOnScroll);
