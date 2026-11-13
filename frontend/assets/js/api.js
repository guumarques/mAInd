/* Cliente da API do mAInd.

Contrato com o servidor: ver frontend/README.md (rotas /api/saude, /api/mensagem/stream e /api/sessao).

Se o servidor não responder, o chat entra em MODO DEMONSTRAÇÃO: um classificador simples
de palavras-chave roda no navegador, só para a interface poder ser mostrada sem servidor.
Ele NÃO é o modelo do projeto, e a interface deixa isso visível. */
(function () {
  const cfg = window.MAIND_CONFIG;
  const TEMAS = [
    ["estresse", "Estresse"], ["depressao", "Depressão"], ["bipolaridade", "Bipolaridade"],
    ["personalidade", "Personalidade"], ["ansiedade", "Ansiedade"],
  ];

  async function fetchJSON(url, opts = {}) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), cfg.TIMEOUT_MS);
    try {
      const r = await fetch(url, { ...opts, signal: ctrl.signal });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } finally { clearTimeout(timer); }
  }

  // ------------------------------------------------------------ modo demonstração
  const CRISE = /suic[ií]d|me matar|tirar (a )?minha (pr[oó]pria )?vida|n[aã]o quero mais viver|quero morrer|acabar com tudo|me machucar|automutila|me cortar/i;
  const PALAVRAS = {
    estresse: ["estress", "sobrecarreg", "prazo", "pressão", "pressao", "trabalho", "chefe", "provas", "faculdade", "cansad", "exaust", "correria", "contas", "não consigo relaxar", "nao consigo relaxar", "burnout"],
    depressao: ["triste", "vazio", "sem vontade", "sem sentido", "chorar", "choro", "desânimo", "desanimo", "sem esperança", "sem esperanca", "cama", "perdi o interesse", "nada tem graça", "nada tem graca", "depress", "inútil", "inutil", "sozinho"],
    bipolaridade: ["euforia", "eufóric", "euforic", "mania", "maníac", "maniac", "bipolar", "lítio", "litio", "não durmo há dias", "gastei", "impulso", "humor alterna", "altos e baixos", "muita energia"],
    personalidade: ["abandon", "rejeiç", "rejeic", "rejeitar", "relações instáveis", "relacoes instaveis", "borderline", "personalidade", "emoções intensas", "emocoes intensas", "evito contato", "medo de ser deixad", "explodo"],
    ansiedade: ["ansios", "ansiedade", "pânico", "panico", "coração dispara", "coracao dispara", "sem ar", "falta de ar", "preocupad", "nervos", "medo", "tremo", "suando", "crise", "pior"],
  };
  const RESPOSTAS = {
    encaminhar: {
      estresse: "Parece que você está carregando muita coisa ao mesmo tempo. Separei algumas ideias para aliviar o estresse e organizar a rotina.",
      depressao: "Obrigado por confiar em mim. O que você descreve pesa muito. Separei um conteúdo sobre depressão, com sinais e caminhos de ajuda.",
      bipolaridade: "Essas oscilações de humor e energia merecem atenção. Separei um conteúdo sobre bipolaridade e sobre quando procurar um psiquiatra.",
      personalidade: "Relações e emoções tão intensas cansam. Separei um conteúdo que pode te ajudar a entender esses padrões.",
      ansiedade: "Isso parece bem angustiante. O que você descreve tem a ver com ansiedade. Separei o que costuma ajudar, inclusive durante uma crise.",
    },
    pedir_detalhes: "Quero entender melhor para te ajudar. Pode me contar um pouco mais? Por exemplo: há quanto tempo está assim e o que mais tem pesado no seu dia?",
    crise: "Sinto muito que você esteja passando por isso. Você não está sozinho e merece ajuda agora. Ligue para o CVV no 188 (gratuito, 24h) ou acesse cvv.org.br. Em emergência, ligue 192.",
  };

  const SAUDACAO = /^(oi+|ol[aá]+|e a[ií]|opa|hey|hello|bom dia|boa tarde|boa noite|tudo bem\??|tudo bom\??)[\s!.,?]*$/i;
  const AGRADECIMENTO = /^(muito )?(obrigad[oa]|brigad[oa]|valeu|vlw)[\s!.,?]*$/i;

  function demoClassificar(texto) {
    const t = texto.toLowerCase();
    if (CRISE.test(t)) return { acao: "crise", probs: null };
    const scores = TEMAS.map(([id]) => PALAVRAS[id].reduce((s, w) => s + (t.includes(w) ? 1 : 0), 0));
    const temp = 0.7;
    const ex = scores.map((s) => Math.exp(s / temp));
    const soma = ex.reduce((a, b) => a + b, 0);
    return { acao: null, probs: ex.map((v) => v / soma) };
  }

  let demoSessao = null;
  function demoResponder(texto, limiar) {
    const t0 = performance.now();
    demoSessao = demoSessao || `demo-${Math.random().toString(36).slice(2, 8)}`;
    const conversa = (resposta) => ({ sessao_id: demoSessao, acao: "conversa", resposta, tema: null, confianca: null,
      limiar, probabilidades: [], latencia_ms: Math.round(performance.now() - t0), demo: true });
    const limpo = texto.trim();
    if (SAUDACAO.test(limpo)) return conversa("Oi! Eu sou o mAInd. Como você está se sentindo hoje? Pode escrever do seu jeito.");
    if (AGRADECIMENTO.test(limpo)) return conversa("Fico feliz em ajudar. Estou por aqui se quiser conversar mais. Cuide-se, e lembre que o CVV (188) atende 24 horas.");
    if (!CRISE.test(limpo) && limpo.split(/\s+/).length < 4) return conversa("Estou aqui para te ouvir. Pode me contar um pouco mais do que está acontecendo?");
    const { acao, probs } = demoClassificar(texto);
    if (acao === "crise") {
      return { sessao_id: demoSessao, acao: "crise", resposta: RESPOSTAS.crise, tema: null, confianca: null,
               limiar, probabilidades: [], latencia_ms: Math.round(performance.now() - t0), demo: true };
    }
    const k = probs.indexOf(Math.max(...probs));
    const conf = probs[k];
    const enc = conf >= limiar;
    return {
      sessao_id: demoSessao,
      acao: enc ? "encaminhar" : "pedir_detalhes",
      resposta: enc ? RESPOSTAS.encaminhar[TEMAS[k][0]] : RESPOSTAS.pedir_detalhes,
      tema: { id: TEMAS[k][0], nome: TEMAS[k][1] },
      confianca: conf, limiar,
      probabilidades: TEMAS.map(([id, nome], i) => ({ id, nome, p: probs[i] })),
      latencia_ms: Math.round(performance.now() - t0), demo: true,
    };
  }

  // ------------------------------------------------------------ resposta aos poucos (SSE via fetch)
  class ErroAmigavel extends Error {}

  async function lerEventos(resp, aoEvento) {
    const leitor = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await leitor.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      buf = buf.replace(/\r\n/g, "\n");
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const bloco = buf.slice(0, i); buf = buf.slice(i + 2);
        let evento = "message", dados = "";
        for (const linha of bloco.split("\n")) {
          if (linha.startsWith("event: ")) evento = linha.slice(7);
          else if (linha.startsWith("data: ")) dados += linha.slice(6);
        }
        aoEvento(evento, dados ? JSON.parse(dados) : null);
      }
    }
  }

  async function enviarAoServidor(texto, sessaoId, cb) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), cfg.TIMEOUT_MS);   // só até a resposta começar
    let resp;
    try {
      resp = await fetch(`${cfg.API_URL}/api/mensagem/stream`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto, sessao_id: sessaoId }), signal: ctrl.signal,
      });
    } finally { clearTimeout(timer); }
    if (!resp.ok) {
      let msg = "Não consegui enviar sua mensagem. Pode tentar de novo?";
      try { msg = (await resp.json()).erro || msg; } catch {}
      throw new ErroAmigavel(msg);
    }
    const r = {};
    await lerEventos(resp, (evento, d) => {
      if (evento === "analise") { Object.assign(r, d); cb.onAnalise && cb.onAnalise(r); }
      else if (evento === "texto") { cb.onTexto && cb.onTexto(d); }
      else if (evento === "substituir") { cb.onSubstituir && cb.onSubstituir(d); }
      else if (evento === "fim") { Object.assign(r, d); }
      else if (evento === "erro") { throw new ErroAmigavel(d.erro); }
    });
    if (!r.resposta) throw new ErroAmigavel("A resposta foi interrompida. Pode tentar de novo?");
    return r;
  }

  // ------------------------------------------------------------ API pública
  window.MaindAPI = {
    modo: "verificando",   // "servidor" | "demo" | "verificando"
    info: null,
    limiar: 0.5,
    ErroAmigavel,

    async verificar() {
      try {
        const r = await fetchJSON(`${cfg.API_URL}/api/saude`);
        this.modo = "servidor"; this.info = r;
        const lim = r.modelo && r.modelo.limiar_confianca;
        if (typeof lim === "number") this.limiar = lim;
      } catch {
        this.modo = "demo"; this.info = null;
      }
      return this.modo;
    },

    /* Envia a mensagem. A resposta chega aos poucos pelos callbacks:
       onAnalise(r) quando o servidor decide o que fazer, onTexto(pedaço) a cada trecho revisado,
       onSubstituir(texto) se o que já apareceu precisar ser trocado. Devolve a resposta completa. */
    async enviar(texto, sessaoId, cb = {}) {
      if (this.modo === "servidor") {
        try {
          return await enviarAoServidor(texto, sessaoId, cb);
        } catch (e) {
          if (e instanceof ErroAmigavel) throw e;
          this.modo = "demo";   // servidor caiu ou não respondeu a tempo
        }
      }
      await new Promise((res) => setTimeout(res, 450 + Math.random() * 400));   // latência simulada
      const r = demoResponder(texto, this.limiar);
      cb.onAnalise && cb.onAnalise(r);
      for (const palavra of r.resposta.split(" ")) {
        await new Promise((res) => setTimeout(res, 25));
        cb.onTexto && cb.onTexto(palavra + " ");
      }
      return r;
    },

    async apagar(sessaoId) {
      if (this.modo !== "servidor" || !sessaoId) return;
      try { await fetch(`${cfg.API_URL}/api/sessao/${encodeURIComponent(sessaoId)}`, { method: "DELETE" }); } catch {}
    },
  };
})();
