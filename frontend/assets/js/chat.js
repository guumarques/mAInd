/* Lógica da página de conversa: mensagens (resposta aparecendo aos poucos) e painel de análise. */
document.addEventListener("DOMContentLoaded", async () => {
  const I = window.MAIND_ICONS;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
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

  const STATUS_TXT = { ok: "", falhou: "falhou", desligada: "desligada", pulada: "pulada" };

  let sessaoId = null;
  let ocupado = false;
  const historico = [];

  // ---------- botões e ícones ----------
  send.innerHTML = I.send;
  resetBtn.innerHTML = `${I.reset}<span class="lbl">Apagar conversa</span>`;
  panelBtn.innerHTML = `${I.panel}<span class="lbl">Análise do modelo</span>`;
  panelBtn.setAttribute("aria-label", "Mostrar ou esconder a análise do modelo");
  resetBtn.setAttribute("aria-label", "Apagar a conversa e começar de novo");
  resetBtn.title = "Apaga esta conversa do servidor e começa uma nova";
  $("chips").innerHTML = SUGESTOES.map((s) => `<button class="btn btn-outline-2" type="button">${esc(s)}</button>`).join("");
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

  resetBtn.addEventListener("click", async () => {
    if (ocupado) return;
    await MaindAPI.apagar(sessaoId);
    sessaoId = null; historico.length = 0;
    inner.querySelectorAll(".msg").forEach((m) => m.remove());
    $("empty").style.display = "";
    limparPainel();
    input.focus();
  });

  // ---------- status do servidor ----------
  const statusEl = $("status");
  await MaindAPI.verificar();
  function atualizarStatus() {
    const live = MaindAPI.modo === "servidor";
    const provisorio = live && MaindAPI.info && MaindAPI.info.modelo && MaindAPI.info.modelo.provisorio;
    statusEl.innerHTML = live
      ? '<span class="dot live"></span>servidor conectado'
      : '<span class="dot demo"></span>modo demonstração';
    if (!live) {
      $("demo-note").innerHTML = '<div class="demo-note"><b>Modo demonstração.</b> O servidor não respondeu, então um classificador simples de palavras-chave está rodando no navegador. Inicie o servidor (<code>python -m servidor</code>) para usar o sistema real.</div>';
    } else if (provisorio) {
      const prov = Object.values(MaindAPI.info.partes || {}).filter((p) => p.provisoria).length;
      $("demo-note").innerHTML = `<div class="demo-note"><b>Partes provisórias.</b> ${prov} etapa(s) ainda devolvem resultados fixos enquanto os modelos reais não chegam. Veja abaixo, em Pipeline.</div>`;
    } else {
      $("demo-note").innerHTML = "";
    }
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

  /* Cria a mensagem do bot vazia; o texto vai chegando com escrever() e finalizar() completa o resto. */
  function msgBot(substituirEl) {
    const el = document.createElement("div");
    el.className = "msg bot";
    el.innerHTML = `<div class="avatar"><img src="assets/img/logo-mark.png" alt=""></div>
      <div class="body"><div class="bubble streaming"></div><div class="extra"></div><div class="meta"></div></div>`;
    if (substituirEl) substituirEl.replaceWith(el); else inner.appendChild(el);
    const bubble = el.querySelector(".bubble");
    let texto = "";
    return {
      el,
      escrever(pedaco) { texto += pedaco; bubble.textContent = texto; scrollFim(); },
      substituir(t) { texto = t; bubble.textContent = t; scrollFim(); },
      finalizar(r) {
        bubble.classList.remove("streaming");
        if (r.acao === "crise") el.classList.add("crise");
        el.querySelector(".extra").innerHTML = extras(r);
        const tag = r.acao === "encaminhar" && r.tema
          ? `<span class="tag-tema">${esc(r.tema.nome)} · ${(r.confianca * 100).toFixed(0)}%</span>`
          : r.acao === "pedir_detalhes" ? '<span class="tag-tema">confiança baixa</span>' : "";
        el.querySelector(".meta").innerHTML = `mAInd · ${hora()} ${tag}`;
        scrollFim();
      },
    };
  }

  function extras(r) {
    let html = "";
    if (r.acao === "encaminhar" && r.tema && MAIND_TEMAS[r.tema.id]) {
      const t = MAIND_TEMAS[r.tema.id];
      html += `<a class="route" href="tema.html?t=${encodeURIComponent(r.tema.id)}" target="_blank" rel="noopener">
          <div class="t"><strong>${esc(t.nome)}</strong><span>${esc(t.resumo)}</span></div>
          <span class="btn btn-outline">Ler ${I.arrow}</span></a>`;
    } else if (r.acao === "crise") {
      html += `<div class="route crise">
          <div class="t"><span class="caption">Apoio agora · 24h · gratuito</span><div class="num" style="margin-top:6px">CVV 188</div></div>
          <a class="btn btn-lg btn-primary" href="tel:188">${I.phone} Ligar</a></div>`;
    }
    if (r.trechos && r.trechos.length) {
      const links = r.trechos.map((t) => /^https?:\/\//.test(t.fonte_url)
        ? `<a href="${esc(t.fonte_url)}" target="_blank" rel="noopener">${esc(t.titulo)}</a>`
        : esc(t.titulo)).join("");
      html += `<div class="fontes"><span class="caption">Fontes</span>${links}</div>`;
    }
    return html;
  }

  async function enviar() {
    const texto = input.value.trim();
    if (!texto || ocupado) return;
    ocupado = true;
    $("empty").style.display = "none";
    input.value = ""; autosize();
    msgUsuario(texto);
    const typing = digitando();
    let bot = null;
    const garantirBot = () => (bot = bot || msgBot(typing));
    let r;
    try {
      r = await MaindAPI.enviar(texto, sessaoId, {
        onAnalise: (a) => { if (a.sessao_id) sessaoId = a.sessao_id; atualizarPainel(texto, a, false); },
        onTexto: (p) => garantirBot().escrever(p),
        onSubstituir: (t) => garantirBot().substituir(t),
      });
    } catch (e) {
      const msg = e instanceof MaindAPI.ErroAmigavel ? e.message : "Tive um problema para responder agora. Pode tentar de novo?";
      r = { acao: "erro", resposta: msg, tema: null, probabilidades: [] };
      garantirBot().substituir(msg);
    }
    if (!bot) garantirBot().substituir(r.resposta);
    sessaoId = r.sessao_id || sessaoId;
    if (r.demo || MaindAPI.modo !== "servidor") atualizarStatus();
    bot.finalizar(r);
    if (r.acao !== "erro") atualizarPainel(texto, r, true);
    ocupado = false; autosize(); input.focus();
  }

  // ---------- painel ----------
  function limparPainel() {
    $("result-block").innerHTML = '<div class="panel-empty">Envie uma mensagem para ver o que o mAInd entendeu.</div>';
    renderProbs($("probs"), NOMES.map((n) => ({ nome: n, p: 0 })), MaindAPI.limiar);
    $("history").innerHTML = '<span class="b-xs faint">Nada ainda.</span>';
    renderTrace(null);
  }

  function renderTrace(r) {
    const live = MaindAPI.modo === "servidor";
    let passos;
    if (live && r && r.etapas) {
      passos = r.etapas.map((e) => ({
        nome: e.nome, desc: [e.descricao, e.detalhe].filter(Boolean).join(" · "),
        status: e.status, ms: e.ms, prov: e.provisoria,
      }));
    } else if (live && MaindAPI.info && MaindAPI.info.partes) {
      const nomes = { seguranca_entrada: "Segurança na entrada", intencao: "Intenção", tema: "Tema",
                      conhecimento: "Conhecimento", ia: "Conversa com a IA", seguranca_saida: "Revisão da resposta" };
      passos = Object.entries(MaindAPI.info.partes).map(([id, p]) => ({
        nome: nomes[id] || id, desc: p.descricao, status: p.ligada ? "" : "desligada", ms: null, prov: p.provisoria,
      }));
    } else {
      passos = [
        { nome: "regra de crise (palavras de risco)" },
        { nome: "contagem de palavras-chave (demo)" },
        { nome: "softmax das contagens (demo)" },
        { nome: `limiar de confiança · ${Math.round(MaindAPI.limiar * 100)}%` },
      ];
    }
    $("trace").innerHTML = passos.map((p, i) => {
      const st = STATUS_TXT[p.status] || "";
      return `<li class="${p.status === "pulada" || p.status === "desligada" ? "off" : ""}${p.status === "falhou" ? " falhou" : ""}">
        <b>${String(i + 1).padStart(2, "0")}</b>
        <span class="step-txt">${esc(p.nome)}${p.prov ? ' <span class="prov">provisória</span>' : ""}${p.desc ? `<small>${esc(p.desc)}</small>` : ""}</span>
        ${st ? `<span class="ms">${st}</span>` : p.ms != null ? `<span class="ms">${p.ms} ms</span>` : ""}</li>`;
    }).join("") + (r && r.latencia_ms != null ? `<li class="total"><b>Σ</b><span class="step-txt">tempo total</span><span class="ms">${r.latencia_ms} ms</span></li>` : "");
  }

  function atualizarPainel(texto, r, final) {
    const intencao = r.intencao ? `intenção: ${esc(r.intencao.nome)}` : "sem classificação de tema";
    const decisao = {
      encaminhar: '<span class="pill enc">Encaminhar</span> confiança acima do limiar',
      pedir_detalhes: '<span class="pill">Pedir mais detalhes</span> confiança abaixo do limiar',
      crise: '<span class="pill">Protocolo de crise</span> resposta fixa, fora da IA',
      conversa: `<span class="pill">Conversa</span> ${intencao}`,
    }[r.acao] || "";

    if (r.acao === "conversa") {
      $("result-block").innerHTML = `<div class="card result"><span class="caption">Sem tema</span>
        <div class="tema-nome" style="margin-top:6px">${r.intencao ? esc(r.intencao.nome) : "Conversa livre"}</div>
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
          ? `<div class="tema-nome">${esc(r.tema.nome)}</div>`
          : `<div class="tema-nome">Sem tema claro</div><div class="incerto">mais provável: ${r.tema ? esc(r.tema.nome) : "—"}</div>`}
        <div class="decision">${decisao}</div></div>`;
      renderProbs($("probs"), r.probabilidades, r.limiar ?? MaindAPI.limiar);
    }
    renderTrace(final ? r : null);
    if (!final) return;

    historico.unshift({ texto, r });
    $("history").innerHTML = historico.slice(0, 8).map(({ texto, r }) => {
      const lado = r.acao === "crise" ? "crise" : r.acao === "conversa" ? "conversa"
        : r.acao === "pedir_detalhes" ? `incerto ${(r.confianca * 100).toFixed(0)}%`
        : `${esc(r.tema.nome)} ${(r.confianca * 100).toFixed(0)}%`;
      return `<div class="item"><span title="${esc(texto)}">${esc(texto)}</span><span>${lado}</span></div>`;
    }).join("");
  }
});
