/* Lógica da página de conversa: mensagens, digitação e painel de análise do modelo. */
document.addEventListener("DOMContentLoaded", async () => {
  const I = window.MAIND_ICONS;
  const $ = (id) => document.getElementById(id);
  const shell = $("shell"), inner = $("messages-inner"), scroller = $("messages");
  const form = $("form"), input = $("input"), send = $("send");
  const panelBtn = $("panel-btn"), resetBtn = $("reset-btn");

  const NOMES = ["Estresse", "Depressão", "Bipolaridade", "Personalidade", "Ansiedade"];
  const SUGESTOES = [
    "Ando muito ansioso com as provas, meu coração dispara à noite",
    "Faz semanas que não sinto vontade de fazer nada",
    "Estou sobrecarregado com trabalho e faculdade",
    "Meu humor muda muito: semanas de euforia e depois fico mal",
  ];

  let sessaoId = null;
  let ocupado = false;
  const historico = [];

  // ---------- botões e ícones ----------
  send.innerHTML = I.send;
  resetBtn.innerHTML = `${I.reset}<span class="lbl">Nova conversa</span>`;
  panelBtn.innerHTML = `${I.panel}<span class="lbl">Análise do modelo</span>`;
  panelBtn.setAttribute("aria-label", "Mostrar ou esconder a análise do modelo");
  resetBtn.setAttribute("aria-label", "Nova conversa");
  $("chips").innerHTML = SUGESTOES.map((s) => `<button class="btn btn-outline-2" type="button">${s}</button>`).join("");
  $("chips").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) { input.value = b.textContent; autosize(); enviar(); }
  });

  // painel aberto por padrão no desktop, fechado em telas menores
  function setPanel(on) {
    shell.classList.toggle("panel-off", !on);
    panelBtn.setAttribute("aria-pressed", String(on));
  }
  setPanel(window.innerWidth >= 1024);
  panelBtn.addEventListener("click", () => setPanel(shell.classList.contains("panel-off")));
  $("scrim").addEventListener("click", () => setPanel(false));

  resetBtn.addEventListener("click", () => {
    sessaoId = null; historico.length = 0;
    inner.querySelectorAll(".msg").forEach((m) => m.remove());
    $("empty").style.display = "";
    limparPainel();
    input.focus();
  });

  // ---------- status do backend ----------
  const statusEl = $("status");
  const modo = await MaindAPI.verificar();
  function atualizarStatus() {
    const live = MaindAPI.modo === "modelo";
    statusEl.innerHTML = live
      ? '<span class="dot live"></span>modelo conectado'
      : '<span class="dot demo"></span>modo demonstração';
    $("demo-note").innerHTML = live ? "" :
      '<div class="demo-note"><b>Modo demonstração.</b> O backend não respondeu, então um classificador simples de palavras-chave está rodando no navegador. Inicie a API para usar o modelo treinado.</div>';
    $("limiar-txt").textContent = `${Math.round(MaindAPI.limiar * 100)}%`;
    renderTrace(null);
  }
  atualizarStatus();
  limparPainel();

  // ---------- composer ----------
  function autosize() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
    send.disabled = ocupado || !input.value.trim();
  }
  input.addEventListener("input", autosize);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); }
  });
  form.addEventListener("submit", (e) => { e.preventDefault(); enviar(); });
  input.focus();

  // ---------- mensagens ----------
  const hora = () => new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  function scrollFim() { scroller.scrollTop = scroller.scrollHeight; }

  function msgUsuario(texto) {
    const el = document.createElement("div");
    el.className = "msg user";
    el.innerHTML = '<div class="body"><div class="bubble"></div><div class="meta"></div></div>';
    el.querySelector(".bubble").textContent = texto;
    el.querySelector(".meta").textContent = hora();
    inner.appendChild(el); scrollFim();
  }

  function digitando() {
    const el = document.createElement("div");
    el.className = "msg bot typing";
    el.innerHTML = '<div class="avatar"><img src="assets/img/logo-mark.png" alt=""></div><div class="body"><div class="bubble"><i></i><i></i><i></i></div></div>';
    inner.appendChild(el); scrollFim();
    return el;
  }

  function msgBot(r) {
    const el = document.createElement("div");
    el.className = "msg bot";
    let extra = "";
    if (r.acao === "encaminhar" && r.tema && MAIND_TEMAS[r.tema.id]) {
      const t = MAIND_TEMAS[r.tema.id];
      extra = `<a class="route" href="tema.html?t=${r.tema.id}" target="_blank" rel="noopener">
          <div class="t"><strong>${t.nome}</strong><span>${t.resumo}</span></div>
          <span class="btn btn-outline">Ler ${I.arrow}</span></a>`;
    } else if (r.acao === "crise") {
      extra = `<div class="route crise">
          <div class="t"><span class="caption">Apoio agora · 24h · gratuito</span><div class="num" style="margin-top:6px">CVV 188</div></div>
          <a class="btn btn-lg btn-primary" href="tel:188">${I.phone} Ligar</a></div>`;
    }
    const tag = r.acao === "encaminhar" && r.tema
      ? `<span class="tag-tema">${r.tema.nome} · ${(r.confianca * 100).toFixed(0)}%</span>`
      : r.acao === "pedir_detalhes" ? '<span class="tag-tema">confiança baixa</span>' : "";
    el.innerHTML = `<div class="avatar"><img src="assets/img/logo-mark.png" alt=""></div>
      <div class="body"><div class="bubble"></div>${extra}<div class="meta">mAInd · ${hora()} ${tag}</div></div>`;
    el.querySelector(".bubble").textContent = r.resposta;
    inner.appendChild(el); scrollFim();
  }

  async function enviar() {
    const texto = input.value.trim();
    if (!texto || ocupado) return;
    ocupado = true;
    $("empty").style.display = "none";
    input.value = ""; autosize();
    msgUsuario(texto);
    const typing = digitando();
    const t0 = performance.now();
    let r;
    try {
      r = await MaindAPI.enviar(texto, sessaoId);
    } catch {
      r = { acao: "pedir_detalhes", resposta: "Tive um problema para responder agora. Pode tentar de novo?", tema: null, probabilidades: [] };
    }
    const espera = 700 - (performance.now() - t0);   // tempo mínimo de "digitando" para soar natural
    if (espera > 0) await new Promise((res) => setTimeout(res, espera));
    typing.remove();
    sessaoId = r.sessao_id || sessaoId;
    if (r.demo || MaindAPI.modo !== "modelo") atualizarStatus();
    msgBot(r);
    atualizarPainel(texto, r);
    ocupado = false; autosize(); input.focus();
  }

  // ---------- painel ----------
  function limparPainel() {
    $("result-block").innerHTML = '<div class="panel-empty">Envie uma mensagem para ver as probabilidades de cada tema.</div>';
    renderProbs($("probs"), NOMES.map((n) => ({ nome: n, p: 0 })), MaindAPI.limiar);
    $("history").innerHTML = '<span class="b-xs faint">Nada ainda.</span>';
    renderTrace(null);
  }

  function renderTrace(r) {
    const live = MaindAPI.modo === "modelo";
    const enc = (MaindAPI.info && MaindAPI.info.encoder) ? MaindAPI.info.encoder.split("/").pop() : "multilingual-MiniLM";
    const passos = live ? [
      ["01", "regra de crise (palavras de risco)"],
      ["02", "limpeza do texto"],
      ["03", `embedding · ${enc}`],
      ["04", "regressão logística · predict_proba"],
      ["05", `limiar de confiança · ${Math.round(MaindAPI.limiar * 100)}%`],
    ] : [
      ["01", "regra de crise (palavras de risco)"],
      ["02", "contagem de palavras-chave (demo)"],
      ["03", "softmax das contagens (demo)"],
      ["04", `limiar de confiança · ${Math.round(MaindAPI.limiar * 100)}%`],
    ];
    $("trace").innerHTML = passos.map(([n, t], i) =>
      `<li><b>${n}</b><span class="step-txt">${t}</span>${r && i === passos.length - 1 && r.latencia_ms != null ? `<span class="ms">${r.latencia_ms} ms</span>` : ""}</li>`).join("");
  }

  function atualizarPainel(texto, r) {
    const decisao = {
      encaminhar: '<span class="pill enc">Encaminhar</span> confiança acima do limiar',
      pedir_detalhes: '<span class="pill">Pedir mais detalhes</span> confiança abaixo do limiar',
      crise: '<span class="pill">Protocolo de crise</span> regra fixa, fora do modelo',
      conversa: '<span class="pill">Conversa</span> mensagem curta: o modelo foi treinado com relatos longos',
    }[r.acao] || "";

    if (r.acao === "conversa") {
      $("result-block").innerHTML = `<div class="card result"><span class="caption">Sem classificação</span>
        <div class="tema-nome" style="margin-top:6px">Mensagem curta</div>
        <div class="decision">${decisao}</div></div>`;
      renderProbs($("probs"), NOMES.map((n) => ({ nome: n, p: 0 })), MaindAPI.limiar);
    } else if (r.acao === "crise") {
      $("result-block").innerHTML = `<div class="card result"><span class="caption">Sinal de risco detectado</span>
        <div class="tema-nome" style="margin-top:6px">Encaminhar ao CVV</div>
        <div class="decision">${decisao}</div></div>`;
      renderProbs($("probs"), NOMES.map((n) => ({ nome: n, p: 0 })), MaindAPI.limiar);
    } else if (r.probabilidades && r.probabilidades.length) {
      $("result-block").innerHTML = `<div class="card result">
        <div class="row"><span class="caption">${r.acao === "encaminhar" ? "Tema identificado" : "Tema incerto"}</span><span class="conf">${(r.confianca * 100).toFixed(1)}%</span></div>
        ${r.acao === "encaminhar"
          ? `<div class="tema-nome">${r.tema.nome}</div>`
          : `<div class="tema-nome">Sem tema claro</div><div class="incerto">mais provável: ${r.tema ? r.tema.nome : "—"}</div>`}
        <div class="decision">${decisao}</div></div>`;
      renderProbs($("probs"), r.probabilidades, r.limiar ?? MaindAPI.limiar);
    }
    renderTrace(r);

    historico.unshift({ texto, r });
    $("history").innerHTML = historico.slice(0, 8).map(({ texto, r }) => {
      const lado = r.acao === "crise" ? "crise" : r.acao === "conversa" ? "conversa"
        : r.acao === "pedir_detalhes" ? `incerto ${(r.confianca * 100).toFixed(0)}%`
        : `${r.tema.nome} ${(r.confianca * 100).toFixed(0)}%`;
      return `<div class="item"><span title="${texto.replace(/"/g, "&quot;")}">${texto.replace(/</g, "&lt;")}</span><span>${lado}</span></div>`;
    }).join("");
  }
});
