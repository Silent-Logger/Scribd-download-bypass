// ==UserScript==
// @name         Scribd Downloader (freshlal fork)
// @namespace    https://github.com/freshlal/scribd-downloader
// @version      2.3.1
// @description  📚 Download documents from Scribd as PDF (fork with tweaks & blank-page fixes)
// @author       ThanhNguyxn
// @contributor  freshlal
// @match        https://www.scribd.com/*
// @icon         https://www.scribd.com/favicon.ico
// @grant        GM_addStyle
// @grant        GM_setClipboard
// @grant        GM_openInTab
// @run-at       document-idle
// @license      MIT
// @homepageURL  https://github.com/Silent-Logger/Scribd-Auto-Download-PDF
// @supportURL   https://github.com/Silent-Logger/Scribd-Auto-Download-PDF/issues
// ==/UserScript==

(function () {
  'use strict';

  // ==================== CONFIG ====================
  const BUTTON_DELAY = 1500;
  const ORIGINAL_REPO = 'https://github.com/Silent-Logger/Scribd-Auto-Download-PDF';

  // Tuning for lazy-load reliability
  const PAGE_LOAD_TIMEOUT_MS = 5000;   // slightly higher to reduce misses
  const MIN_TEXT_PER_PAGE   = 30;

  // ==================== STYLES ====================
  const styles = `
  #sd-floating-btn {
    position: fixed !important;
    top: 80px !important;
    right: 20px !important;
    z-index: 2147483647 !important;
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%) !important;
    color: #fff !important;
    border: none !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(102,126,234,.5) !important;
    font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    transition: all .3s ease !important;
    text-decoration: none !important;
  }
  #sd-floating-btn:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 25px rgba(102,126,234,.6) !important;
  }
  #sd-floating-btn.loading {
    background: linear-gradient(135deg,#ffa726 0%,#fb8c00 100%) !important;
    pointer-events: none !important;
  }
  #sd-popup {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(0,0,0,.85) !important;
    z-index: 2147483647 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    opacity: 0;
    visibility: hidden;
    transition: all .3s ease !important;
  }
  #sd-popup.show { opacity: 1; visibility: visible; }
  #sd-popup-content {
    background: #fff !important;
    padding: 30px !important;
    border-radius: 20px !important;
    max-width: 420px !important;
    width: 90% !important;
    text-align: center !important;
    box-shadow: 0 25px 80px rgba(0,0,0,.4) !important;
    transform: scale(.9);
    transition: transform .3s ease !important;
  }
  #sd-popup.show #sd-popup-content { transform: scale(1) !important; }
  #sd-url-display {
    background: linear-gradient(135deg,#1a1a2e 0%,#16213e 100%) !important;
    color: #00d9ff !important;
    padding: 15px !important;
    border-radius: 10px !important;
    font-family: Monaco,Consolas,monospace !important;
    font-size: 12px !important;
    word-break: break-all !important;
    margin: 15px 0 !important;
    text-align: left !important;
    border: 2px solid #667eea !important;
    user-select: all !important;
    cursor: text !important;
  }
  .sd-btn {
    padding: 12px 24px !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all .2s ease !important;
    margin: 5px !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
  }
  .sd-btn-success {
    background: linear-gradient(135deg,#11998e 0%,#38ef7d 100%) !important;
    color: #fff !important;
  }
  .sd-btn-warning {
    background: linear-gradient(135deg,#f093fb 0%,#f5576c 100%) !important;
    color: #fff !important;
  }
  .sd-btn-close { background: #e0e0e0 !important; color: #333 !important; }
  .sd-btn:hover { transform: scale(1.05) !important; box-shadow: 0 5px 20px rgba(0,0,0,.2) !important; }
  .sd-info {
    background: linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%) !important;
    border-left: 4px solid #4caf50 !important;
    padding: 12px 15px !important;
    margin: 15px 0 !important;
    border-radius: 0 10px 10px 0 !important;
    text-align: left !important;
    font-size: 13px !important;
    color: #2e7d32 !important;
  }
  .sd-btn-group {
    display: flex !important;
    gap: 8px !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    margin-top: 15px !important;
  }
  .sd-links {
    margin-top: 20px !important;
    padding-top: 15px !important;
    border-top: 1px solid #eee !important;
    display: flex !important;
    justify-content: center !important;
    gap: 15px !important;
  }
  .sd-link {
    color: #666 !important;
    text-decoration: none !important;
    font-size: 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 5px !important;
    transition: color .2s !important;
  }
  .sd-link:hover { color: #667eea !important; }

  #sd-download-btn {
    position: fixed !important;
    top: 20px !important;
    right: 20px !important;
    z-index: 2147483647 !important;
    background: linear-gradient(135deg,#11998e 0%,#38ef7d 100%) !important;
    color: #fff !important;
    border: none !important;
    padding: 14px 24px !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(17,153,142,.5) !important;
    font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    transition: all .3s ease !important;
  }
  #sd-download-btn.loading {
    background: linear-gradient(135deg,#ffa726 0%,#fb8c00 100%) !important;
  }

  #sd-progress-popup {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(0,0,0,.9) !important;
    z-index: 2147483647 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
  }
  #sd-progress-content {
    background: #fff !important;
    padding: 35px !important;
    border-radius: 20px !important;
    text-align: center !important;
    min-width: 320px !important;
  }
  #sd-progress-bar {
    width: 100% !important;
    height: 10px !important;
    background: #e0e0e0 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    margin: 20px 0 !important;
  }
  #sd-progress-fill {
    height: 100% !important;
    background: linear-gradient(90deg,#667eea,#764ba2) !important;
    width: 0 !important;
    transition: width .3s ease !important;
    border-radius: 10px !important;
  }
  #sd-progress-text {
    color: #666 !important;
    font-size: 15px !important;
    margin-bottom: 10px !important;
  }

  @media print {
    .toolbar_top, .toolbar_bottom {
      display: none !important;
    }
    #sd-download-btn, #sd-progress-popup, #sd-floating-btn {
      display: none !important;
    }
    @page { margin: 0; }
  }
  `;

  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);

  // ==================== UTILITIES ====================
  function getDocId() {
    const url = window.location.href;
    const match = url.match(/(?:document|doc|embeds|read)\/(\d+)/);
    return match ? match[1] : null;
  }

  function isEmbed() {
    return window.location.href.includes('/embeds/');
  }

  function getEmbedUrl(id) {
    return `https://www.scribd.com/embeds/${id}/content`;
  }

  function copyText(text) {
    try {
      if (typeof GM_setClipboard === 'function') {
        GM_setClipboard(text, 'text');
        return true;
      }
    } catch (e) {}
    try {
      navigator.clipboard.writeText(text);
      return true;
    } catch (e) {}
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
      return true;
    } catch (e) {}
    return false;
  }

  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  // --------- PATCH 1: safer page element detection ----------
  function getPageElements() {
    // Prefer explicit Scribd page containers
    let pages = qa('[data-page-number], .outer_page, .new_page, .page_content');

    // Fallback to .page only (avoid [class*="page"])
    if (pages.length === 0) {
      pages = qa('.page');
    }

    // Filter out tiny / hidden nodes
    return pages.filter(node => {
      const rect  = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return rect.height > 300 &&
             rect.width  > 300 &&
             style.display !== 'none' &&
             style.visibility !== 'hidden';
    });
  }

  // --------- PATCH 2: stronger “is loaded” heuristic ----------
  function isPageLoaded(page) {
    try {
      const text = (page.innerText || '').trim();
      if (text.length >= MIN_TEXT_PER_PAGE) return true;

      const imgs = page.querySelectorAll('img, svg, canvas');
      if (imgs.length > 0) {
        for (const img of imgs) {
          if (img.naturalWidth > 50 && img.naturalHeight > 50) return true;
        }
      }

      const cls = page.className || '';
      if (cls.includes('loaded') || cls.includes('rendered')) return true;

      return false;
    } catch {
      return false;
    }
  }

  // ==================== MAIN PAGE UI ====================
  function showMainButton() {
    if (q('#sd-floating-btn')) return;
    const docId = getDocId();
    if (!docId) return;

    const btn = document.createElement('button');
    btn.id = 'sd-floating-btn';
    btn.textContent = '📥 Download PDF';
    btn.addEventListener('click', startAutoDownload);
    document.body.appendChild(btn);
  }

  async function startAutoDownload() {
    const btn = q('#sd-floating-btn');
    const docId = getDocId();
    if (!docId) {
      alert('Cannot find document ID!');
      return;
    }
    const embedUrl = getEmbedUrl(docId);

    btn.classList.add('loading');
    btn.textContent = '⏳ Opening...';

    showAutoPopup(embedUrl);
  }

  function showAutoPopup(embedUrl) {
    const existing = q('#sd-popup');
    if (existing) existing.remove();

    const popup = document.createElement('div');
    popup.id = 'sd-popup';
    popup.innerHTML = `
      <div id="sd-popup-content">
        <h2>📚 Scribd Downloader</h2>
        <div class="sd-info">
          ✨ <strong>Auto mode:</strong> Opening embed page in new tab...
        </div>
        <div id="sd-url-display">${embedUrl}</div>
        <p style="color:#666;font-size:13px;margin:15px 0;">
          A new tab will open automatically.<br>
          Click the <strong style="color:#11998e;">green button</strong> there to download!
        </p>
        <div class="sd-btn-group">
          <button class="sd-btn sd-btn-success" id="sd-open-now">🚀 Open Now</button>
          <button class="sd-btn sd-btn-warning" id="sd-open-incognito">🕵️ Manual (Incognito)</button>
          <button class="sd-btn sd-btn-close"   id="sd-close-btn">Close</button>
        </div>
        <div class="sd-links">
          <a href="${ORIGINAL_REPO}" target="_blank" class="sd-link">⭐ Original repo</a>
        </div>
      </div>
    `;
    document.body.appendChild(popup);

    requestAnimationFrame(() => popup.classList.add('show'));

    const autoTimer = setTimeout(() => {
      openEmbedPage(embedUrl);
    }, 1500);

    q('#sd-open-now').onclick = () => {
      clearTimeout(autoTimer);
      openEmbedPage(embedUrl);
    };

    q('#sd-open-incognito').onclick = function () {
      clearTimeout(autoTimer);
      copyText(embedUrl);
      this.textContent = '✅ URL Copied!';
      showManualInstructions();
    };

    q('#sd-close-btn').onclick = () => {
      clearTimeout(autoTimer);
      closePopup();
    };

    popup.onclick = e => {
      if (e.target === popup) {
        clearTimeout(autoTimer);
        closePopup();
      }
    };
  }

  function openEmbedPage(url) {
    let opened = false;
    try {
      if (typeof GM_openInTab === 'function') {
        GM_openInTab(url, { active: false, insert: true, setParent: true });
        opened = true;
      }
    } catch (e) {}

    if (!opened) {
      const newTab = window.open(url, '_blank');
      if (newTab) {
        window.focus();
        opened = true;
      }
    }

    const btn = q('#sd-floating-btn');
    if (btn) {
      btn.classList.remove('loading');
      btn.textContent = opened ? '✅ Opened!' : '⚠️ Popup blocked';
      setTimeout(() => { btn.textContent = '📥 Download PDF'; }, 3000);
    }

    const content = q('#sd-popup-content');
    if (!content) return;

    if (opened) {
      content.innerHTML = `
        <h2>✅ Tab Opened!</h2>
        <div class="sd-info" style="background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%) !important;">
          🎉 <strong>Success!</strong> A new tab has been opened in the background.
        </div>
        <p style="color:#666;font-size:13px;margin:15px 0;">
          📌 <strong>Next steps:</strong><br>
          1. Switch to the new tab<br>
          2. Click the <strong style="color:#11998e;">green Download button</strong><br>
          3. Wait for all pages to load<br>
          4. Save as PDF
        </p>
        <div class="sd-btn-group">
          <button class="sd-btn sd-btn-close" id="sd-close-btn2">Got it!</button>
        </div>
        <div class="sd-links">
          <a href="${ORIGINAL_REPO}" target="_blank" class="sd-link">⭐ Original repo</a>
        </div>
      `;
    } else {
      content.innerHTML = `
        <h2>⚠️ Popup blocked</h2>
        <div class="sd-info">
          Your browser blocked the new tab.<br>
          Use <strong>Manual (Incognito)</strong> instead.
        </div>
        <div class="sd-btn-group">
          <button class="sd-btn sd-btn-warning" id="sd-open-incognito2">🕵️ Manual (Incognito)</button>
          <button class="sd-btn sd-btn-close"   id="sd-close-btn2">Close</button>
        </div>
      `;
      q('#sd-open-incognito2').onclick = () => {
        copyText(url);
        showManualInstructions();
      };
    }

    const closeBtn2 = q('#sd-close-btn2');
    if (closeBtn2) closeBtn2.onclick = closePopup;
  }

  function showManualInstructions() {
    const content = q('#sd-popup-content');
    if (!content) return;
    content.innerHTML = `
      <h2>🕵️ Manual Mode</h2>
      <div class="sd-info">
        ✅ <strong>URL copied!</strong> Follow these steps:
      </div>
      <ol style="text-align:left;color:#444;line-height:1.8;padding-left:20px;margin:20px 0;">
        <li>Press <strong>Ctrl+Shift+N</strong> (Incognito window)</li>
        <li>Paste the URL (<strong>Ctrl+V</strong>)</li>
        <li>Press <strong>Enter</strong></li>
        <li>Click the <strong style="color:#11998e;">green Download button</strong></li>
      </ol>
      <div class="sd-btn-group">
        <button class="sd-btn sd-btn-close" id="sd-close-btn2">Got it!</button>
      </div>
      <div class="sd-links">
        <a href="${ORIGINAL_REPO}" target="_blank" class="sd-link">⭐ Original repo</a>
      </div>
    `;
    q('#sd-close-btn2').onclick = closePopup;
  }

  function closePopup() {
    const popup = q('#sd-popup');
    const btn   = q('#sd-floating-btn');
    if (popup) {
      popup.classList.remove('show');
      setTimeout(() => popup.remove(), 300);
    }
    if (btn) {
      btn.classList.remove('loading');
      btn.textContent = '📥 Download PDF';
    }
  }

  // ==================== EMBED PAGE UI ====================
  function showEmbedButton() {
    if (q('#sd-download-btn')) return;

    const btn = document.createElement('button');
    btn.id = 'sd-download-btn';
    btn.textContent = '⬇️ Download PDF';
    btn.addEventListener('click', startDownload);
    document.body.appendChild(btn);

    if (document.referrer.includes('scribd.com')) {
      setTimeout(() => {
        const autoBtn = q('#sd-download-btn');
        if (autoBtn && !autoBtn.classList.contains('loading')) {
          autoBtn.textContent = '🚀 Starting...';
          setTimeout(startDownload, 500);
        }
      }, 2000);
    }
  }

  async function startDownload() {
    const btn = q('#sd-download-btn');
    if (!btn) return;

    btn.classList.add('loading');
    btn.textContent = '⏳ Processing...';

    const progress = document.createElement('div');
    progress.id = 'sd-progress-popup';
    progress.innerHTML = `
      <div id="sd-progress-content">
        <h2>📚 Preparing PDF...</h2>
        <div id="sd-progress-text">Loading pages...</div>
        <div id="sd-progress-bar">
          <div id="sd-progress-fill"></div>
        </div>
        <p style="color:#888;font-size:12px;margin-top:15px;">
          Please wait, this may take a moment...
        </p>
      </div>
    `;
    document.body.appendChild(progress);

    const fill = q('#sd-progress-fill');
    const text = q('#sd-progress-text');

    function setProgress(pct, msg) {
      if (fill) fill.style.width = `${pct}%`;
      if (text && msg) text.textContent = msg;
    }

    try {
      setProgress(5, '🔍 Detecting pages...');
      const scrollContainer =
        q('.document_scroller, [class*="scroller"]') || document.documentElement;
      const pages = getPageElements();
      const totalPages = pages.length;

      if (totalPages === 0) {
        setProgress(100, '❌ No pages detected. Scribd layout may have changed.');
        await sleep(1200);
        throw new Error('No pages detected');
      }

      let loadedCount = 0;
      for (let i = 0; i < totalPages; i++) {
        const page = pages[i];
        page.scrollIntoView({ behavior: 'instant', block: 'start' });
        if (scrollContainer && scrollContainer !== document.documentElement) {
          scrollContainer.scrollTop = page.offsetTop;
        }

        const start = performance.now();
        while (!isPageLoaded(page) &&
               performance.now() - start < PAGE_LOAD_TIMEOUT_MS) {
          await sleep(250);
        }
        loadedCount++;

        const pct = 10 + Math.round((loadedCount / totalPages) * 35);
        setProgress(pct, `📄 Loading page ${i + 1}/${totalPages}...`);
      }

      if (loadedCount < totalPages * 0.9) {
        setProgress(100, '⚠️ Some pages may be incomplete. Check print preview.');
        await sleep(1500);
      }

      setProgress(50, '🧹 Removing toolbars...');
      await sleep(200);
      const toolbarTop    = q('.toolbar_top');
      const toolbarBottom = q('.toolbar_bottom');
      if (toolbarTop) toolbarTop.remove();
      if (toolbarBottom) toolbarBottom.remove();

      setProgress(65, '🧹 Removing overlays...');
      await sleep(200);
      const junkSelectors = [
        '.promo_div',
        '[class*="paywall"]',
        '[class*="upsell"]',
        '[class*="signup"]',
        '.ReactModalPortal',
        '[data-testid*="paywall"]',
        '[data-testid*="overlay"]',
        '[class*="modal"]',
        '[class*="banner"]',
        '[class*="pay-wall"]'
      ];
      junkSelectors.forEach(sel => {
        try { qa(sel).forEach(el => el.remove()); } catch (e) {}
      });

      setProgress(80, '✨ Optimizing layout...');
      await sleep(200);
      const scrollers = qa('.document_scroller, [class*="scroller"]');
      scrollers.forEach(el => {
        el.style.overflow = 'visible';
        el.style.height = 'auto';
        el.style.maxHeight = 'none';
      });

      // --------- PATCH 3: only add page breaks to real pages ----------
      const printPages = getPageElements();
      printPages.forEach(page => {
        page.style.pageBreakAfter = 'always';
        page.style.pageBreakInside = 'avoid';
        page.style.breakAfter = 'page';
        page.style.breakInside = 'avoid';
      });

      window.scrollTo(0, 0);
      if (scrollContainer && scrollContainer !== document.documentElement) {
        scrollContainer.scrollTop = 0;
      }

      setProgress(100, '✅ Ready! Opening print dialog...');
      await sleep(500);
      progress.remove();
      btn.remove();

      window.print();

      const newBtn = document.createElement('button');
      newBtn.id = 'sd-download-btn';
      newBtn.textContent = '✅ Done! Print again?';
      newBtn.onclick = startDownload;
      document.body.appendChild(newBtn);

      setTimeout(() => {
        const b = q('#sd-download-btn');
        if (b) b.textContent = '⬇️ Download PDF';
      }, 5000);
    } catch (err) {
      console.error('[Scribd Downloader] Download error:', err);
      progress.remove();
      btn.classList.remove('loading');
      btn.textContent = '❌ Error - Try again';
      setTimeout(() => { btn.textContent = '⬇️ Download PDF'; }, 3000);
    }
  }

  // ==================== INIT ====================
  function init() {
    if (!window.location.hostname.includes('scribd.com')) return;
    setTimeout(() => {
      if (isEmbed()) {
        showEmbedButton();
      } else if (getDocId()) {
        showMainButton();
      }
    }, BUTTON_DELAY);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


