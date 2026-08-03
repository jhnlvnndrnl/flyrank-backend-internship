/* ==========================================================================
   WEEK 3 VISUAL IDENTITY KIT INTERACTIVE LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // Toast Notification Helper
  // ==========================================
  const toast = document.getElementById('toast');
  
  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    
    // Clear previous timeout if any
    if (window.toastTimeout) {
      clearTimeout(window.toastTimeout);
    }
    
    window.toastTimeout = setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  // ==========================================
  // Monogram Logo Copy & Download
  // ==========================================
  const btnCopySvg = document.getElementById('btn-copy-svg');
  const btnDownloadSvg = document.getElementById('btn-download-svg');
  const svgPreview = document.getElementById('svg-logo-preview');

  // Helper to get raw SVG string
  function getSvgString() {
    // Get outerHTML of the preview SVG and clean it up slightly if needed
    return svgPreview.outerHTML;
  }

  // Copy SVG Code
  if (btnCopySvg) {
    btnCopySvg.addEventListener('click', () => {
      const svgCode = getSvgString();
      navigator.clipboard.writeText(svgCode)
        .then(() => {
          showToast('SVG XML code copied to clipboard!');
        })
        .catch(err => {
          console.error('Could not copy text: ', err);
          showToast('Failed to copy SVG code.');
        });
    });
  }

  // Download SVG File
  if (btnDownloadSvg) {
    btnDownloadSvg.addEventListener('click', () => {
      const svgCode = getSvgString();
      const blob = new Blob([svgCode], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      
      const downloadLink = document.createElement('a');
      downloadLink.href = url;
      downloadLink.download = 'je-monogram-logo.svg';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
      URL.revokeObjectURL(url);
      showToast('Logo SVG file downloaded successfully!');
    });
  }

  // ==========================================
  // Interactive Typography Playground
  // ==========================================
  const playgroundInput = document.getElementById('playground-input');
  const outputSyne = document.getElementById('output-syne');
  const outputInter = document.getElementById('output-inter');

  if (playgroundInput && outputSyne && outputInter) {
    playgroundInput.addEventListener('input', (e) => {
      const value = e.target.value.trim() || 'Building high-performance backend systems with clean architectures';
      outputSyne.textContent = value;
      outputInter.textContent = value;
    });
  }

  // ==========================================
  // Color Swatch "Click to Copy"
  // ==========================================
  const colorCards = document.querySelectorAll('.color-card');
  
  colorCards.forEach(card => {
    const hex = card.getAttribute('data-hex');
    const overlay = card.querySelector('.color-copy-overlay');
    
    if (overlay && hex) {
      overlay.addEventListener('click', () => {
        navigator.clipboard.writeText(hex)
          .then(() => {
            showToast(`Hex code ${hex} copied to clipboard!`);
          })
          .catch(err => {
            console.error('Could not copy text: ', err);
            showToast('Failed to copy hex code.');
          });
      });
    }
  });

  // ==========================================
  // Scroll Spy Sidebar Navigation
  // ==========================================
  const sections = document.querySelectorAll('.content-section');
  const navItems = document.querySelectorAll('.nav-item');

  function updateActiveNav() {
    let currentActiveId = '';
    const scrollPosition = window.scrollY + 120; // Offset for section activation

    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      
      if (scrollPosition >= top && scrollPosition < top + height) {
        currentActiveId = id;
      }
    });

    // Special case: check if we are at the very top
    if (window.scrollY < 50) {
      currentActiveId = sections[0].getAttribute('id');
    }
    
    // Special case: check if we scrolled to the very bottom
    if ((window.innerHeight + window.scrollY) >= document.documentElement.scrollHeight - 20) {
      currentActiveId = sections[sections.length - 1].getAttribute('id');
    }

    if (currentActiveId) {
      navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === `#${currentActiveId}`) {
          item.classList.add('active');
        }
      });
    }
  }

  window.addEventListener('scroll', updateActiveNav);
  
  // Smooth scroll activation logic
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      // Allow browser to perform natural smooth scroll, but update active class immediately
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');
    });
  });

  // Initial call to set active nav on load
  updateActiveNav();
});
