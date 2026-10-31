/* Partes compartilhadas por todas as páginas: cabeçalho, rodapé, tema claro/escuro,
   ícones e animação de revelação ao rolar. */
(function () {
  const ICONS = {
    sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    panel: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/></svg>',
    reset: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>',
    external: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
  };
  window.MAIND_ICONS = ICONS;

  // ---------- tema claro/escuro (preferência salva só neste navegador) ----------
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* sem armazenamento: ignora */ } },
  };
  const savedTheme = store.get("maind-theme");
  if (savedTheme === "light") document.documentElement.setAttribute("data-theme", "light");

  function toggleTheme() {
    const light = document.documentElement.getAttribute("data-theme") === "light";
    if (light) document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", "light");
    store.set("maind-theme", light ? "dark" : "light");
    renderThemeIcon();
  }
  function renderThemeIcon() {
    const btn = document.getElementById("theme-btn");
    if (!btn) return;
    const light = document.documentElement.getAttribute("data-theme") === "light";
    btn.innerHTML = light ? ICONS.moon : ICONS.sun;
    btn.setAttribute("aria-label", light ? "Ativar tema escuro" : "Ativar tema claro");
  }

  // ---------- cabeçalho e rodapé ----------
  const page = document.body.dataset.page || "";
  const links = [
    ["index.html#como-funciona", "Como funciona", "home"],
    ["index.html#temas", "Temas", "temas"],
    ["index.html#modelo", "O modelo", "modelo"],
  ];

  function header() {
    const nav = links.map(([href, label, id]) =>
      `<a href="${href}"${page === id ? ' aria-current="page"' : ""}>${label}</a>`).join("");
    return `
      <div class="container">
        <a class="brand" href="index.html" aria-label="mAInd, página inicial">
          <img src="assets/img/logo-mark.png" alt="" width="26" height="22">
          <span>m<span class="ai">AI</span>nd</span>
        </a>
        <nav class="nav" aria-label="Principal">${nav}</nav>
        <div class="header-actions">
          <a class="btn btn-outline-2 hide-sm" href="tel:188" title="CVV, apoio emocional 24h">${ICONS.phone} CVV 188</a>
          <button class="icon-btn" id="theme-btn" type="button"></button>
          ${page === "chat" ? "" : `<a class="btn btn-filled" href="chat.html">Conversar</a>`}
          <button class="icon-btn menu-toggle" id="menu-btn" type="button" aria-label="Abrir menu" aria-expanded="false">${ICONS.menu}</button>
        </div>
      </div>
      <nav class="mobile-nav" id="mobile-nav" aria-label="Menu">
        ${links.map(([href, label]) => `<a href="${href}">${label}</a>`).join("")}
        <a href="chat.html">Conversar com o mAInd</a>
        <a href="tel:188">Ligar para o CVV (188)</a>
      </nav>`;
  }

  function footer() {
    return `
      <div class="container">
        <div style="max-width:420px">
          <a class="brand" href="index.html"><img src="assets/img/logo-mark.png" alt="" width="26" height="22"><span>m<span class="ai">AI</span>nd</span></a>
          <p class="b-sm muted" style="margin-top:12px">O mAInd é um projeto acadêmico de Machine Learning (C318, Inatel). Não faz diagnóstico e não substitui um profissional de saúde.</p>
          <p class="b-xs faint" style="margin-top:8px">Em emergência: CVV 188 (24h, gratuito) · SAMU 192</p>
        </div>
        <div class="footer-cols">
          <div><span class="caption">Produto</span><a href="chat.html">Conversar</a><a href="index.html#temas">Temas</a><a href="index.html#como-funciona">Como funciona</a></div>
          <div><span class="caption">Projeto</span><a href="index.html#modelo">O modelo</a><a href="https://cvv.org.br" target="_blank" rel="noopener">CVV</a></div>
        </div>
      </div>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const h = document.getElementById("site-header");
    if (h) { h.className = "site-header"; h.innerHTML = header(); }
    const f = document.getElementById("site-footer");
    if (f) { f.className = "site-footer"; f.innerHTML = footer(); }

    renderThemeIcon();
    document.getElementById("theme-btn")?.addEventListener("click", toggleTheme);

    const menuBtn = document.getElementById("menu-btn");
    const mobileNav = document.getElementById("mobile-nav");
    menuBtn?.addEventListener("click", () => {
      const open = mobileNav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    mobileNav?.addEventListener("click", (e) => { if (e.target.closest("a")) mobileNav.classList.remove("open"); });

    // revelação ao rolar
    const els = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
      }, { threshold: 0.12 });
      els.forEach((el) => io.observe(el));
    } else {
      els.forEach((el) => el.classList.add("in"));
    }
  });

  // utilitário: barras de probabilidade (página inicial e chat)
  window.renderProbs = function (container, probs, limiar) {
    const max = Math.max(...probs.map((p) => p.p));
    const topIdx = max > 0 ? probs.findIndex((p) => p.p === max) : -1;
    container.innerHTML = probs.map((p, i) => `
      <div class="prob${i === topIdx ? " top" : ""}">
        <span class="prob-name">${p.nome}</span>
        <span class="prob-track">
          <span class="prob-fill" style="display:block"></span>
          ${limiar != null ? `<span class="prob-threshold" style="left:${limiar * 100}%" title="limiar de confiança"></span>` : ""}
        </span>
        <span class="prob-val">${(p.p * 100).toFixed(0)}%</span>
      </div>`).join("");
    requestAnimationFrame(() => requestAnimationFrame(() => {
      container.querySelectorAll(".prob-fill").forEach((el, i) => { el.style.width = (probs[i].p * 100).toFixed(1) + "%"; });
    }));
  };
})();
