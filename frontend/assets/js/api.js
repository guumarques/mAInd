/* Cliente da API do mAInd.

Contrato esperado do backend (Flask):
  GET  /api/saude     -> { status: "ok", modelo: { encoder, classificador, limiar_confianca, ... } }
  POST /api/mensagem  body { texto, sessao_id? }
                      -> { sessao_id, resposta, acao: "encaminhar" | "pedir_detalhes" | "crise" | "conversa",
                           tema: { id, nome } | null, confianca, limiar,
                           probabilidades: [{ id, nome, p }], latencia_ms }

Se o backend não responder, o chat entra em MODO DEMONSTRAÇÃO: um classificador simples
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

  // ------------------------------------------------------------ API pública
  window.MaindAPI = {
    modo: "verificando",   // "modelo" | "demo" | "verificando"
    info: null,
    limiar: 0.5,

    async verificar() {
      try {
        const r = await fetchJSON(`${cfg.API_URL}/api/saude`);
        this.modo = "modelo"; this.info = r.modelo || {};
        if (typeof this.info.limiar_confianca === "number") this.limiar = this.info.limiar_confianca;
      } catch {
        this.modo = "demo"; this.info = null;
      }
      return this.modo;
    },

    async enviar(texto, sessaoId) {
      if (this.modo === "modelo") {
        try {
          return await fetchJSON(`${cfg.API_URL}/api/mensagem`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ texto, sessao_id: sessaoId }),
          });
        } catch {
          this.modo = "demo";   // backend caiu durante a conversa
        }
      }
      await new Promise((r) => setTimeout(r, 450 + Math.random() * 400));   // latência simulada
      return demoResponder(texto, this.limiar);
    },
  };
})();
