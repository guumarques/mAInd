/* Conteúdo informativo de cada tema. Os ids batem com os temas que o modelo classifica
   (exceto "solidao", que é só conteúdo). Textos de caráter informativo: não substituem
   avaliação profissional. */
window.MAIND_TEMAS = {
  ansiedade: {
    nome: "Ansiedade",
    glow: "#5865F2",
    resumo: "Preocupação constante, coração acelerado, sensação de que algo ruim vai acontecer.",
    oQueE: "A ansiedade é uma emoção natural que funciona como um mecanismo de defesa, nos alertando para situações de perigo ou estresse. Quando ela se torna excessiva e constante, passa a interferir na qualidade de vida e pode caracterizar um transtorno de ansiedade.",
    sinais: {
      "Físicos": ["Taquicardia e falta de ar", "Sudorese e tremores", "Tensão muscular e dores de cabeça", "Insônia", "Problemas digestivos"],
      "Emocionais": ["Preocupação excessiva", "Irritabilidade", "Dificuldade de concentração", "Nervosismo constante", "Medo intenso, às vezes sem motivo aparente"],
    },
    ajuda: [
      ["Terapia", "A terapia cognitivo-comportamental (TCC) é uma das abordagens mais eficazes: ajuda a identificar e mudar pensamentos que alimentam a ansiedade."],
      ["Respiração e relaxamento", "Respiração lenta e profunda, relaxamento muscular progressivo e yoga reduzem a tensão no momento da crise."],
      ["Atenção plena", "Práticas de mindfulness e meditação ajudam a voltar ao presente quando a mente acelera."],
      ["Corpo em movimento", "Atividade física regular libera endorfinas e reduz o estresse."],
      ["Sono, cafeína e álcool", "Dormir bem e reduzir cafeína e álcool diminui a intensidade dos sintomas."],
    ],
    quandoBuscar: "Se a ansiedade atrapalha sua rotina, seus estudos, seu trabalho ou suas relações, procure um psicólogo ou psiquiatra. Em alguns casos, o médico pode indicar medicação.",
  },
  depressao: {
    nome: "Depressão",
    glow: "#7048E8",
    resumo: "Tristeza que não passa, cansaço, perda de interesse pelo que antes era bom.",
    oQueE: "A depressão é um transtorno mental que afeta a forma como você se sente, pensa e age. É muito mais do que se sentir triste por alguns dias: causa tristeza persistente e perda de interesse e prazer em atividades que antes eram agradáveis, afetando a vida diária.",
    sinais: {
      "Emocionais": ["Tristeza profunda e persistente", "Perda de interesse e prazer", "Culpa ou sensação de inutilidade", "Dificuldade de concentração e de decisão", "Pensamentos de morte"],
      "Físicos": ["Fadiga e perda de energia", "Mudanças no apetite", "Insônia ou sono em excesso", "Dores sem causa aparente"],
    },
    ajuda: [
      ["Ajuda profissional", "O tratamento costuma combinar psicoterapia e, quando indicado pelo médico, medicação. O diagnóstico é feito por um profissional."],
      ["Rotina", "Manter horários regulares de sono, alimentação e atividades dá estrutura aos dias mais difíceis."],
      ["Movimento", "Mesmo caminhadas curtas ajudam no humor."],
      ["Conexão", "Manter contato com amigos e familiares, mesmo que por pouco tempo, faz diferença."],
      ["Passos pequenos", "Divida tarefas em partes menores e reconheça cada uma que conseguir cumprir."],
    ],
    quandoBuscar: "Se os sintomas duram mais de duas semanas ou se surgirem pensamentos de morte, procure um profissional de saúde. Em uma emergência, ligue 188 (CVV) ou 192 (SAMU).",
  },
  estresse: {
    nome: "Estresse",
    glow: "#3B82F6",
    resumo: "Sobrecarga, pressão de prazos, sensação de estar sempre no limite.",
    oQueE: "O estresse é a reação natural do organismo a situações de ameaça ou pressão: libera hormônios que aumentam energia e atenção. Quando se torna crônico, persistente e excessivo, pode causar problemas de saúde física e mental.",
    sinais: {
      "Físicos": ["Dores de cabeça e tensão muscular", "Insônia e fadiga", "Problemas digestivos", "Alterações no apetite", "Taquicardia"],
      "Emocionais": ["Irritabilidade", "Sensação de sobrecarga", "Dificuldade em relaxar", "Mudanças de humor", "Sensação de estar sempre no limite"],
    },
    ajuda: [
      ["Organize o tempo", "Liste tarefas, defina prioridades e quebre o que é grande em partes menores."],
      ["Pausas de verdade", "Intervalos curtos e respiração profunda ao longo do dia evitam o acúmulo de tensão."],
      ["Corpo", "Atividade física regular e 7 a 8 horas de sono são os antídotos mais eficazes."],
      ["Limites", "Aprender a dizer não e a pedir ajuda reduz a sobrecarga."],
      ["Terapia", "Ajuda a identificar as causas do estresse e a criar estratégias para lidar com elas."],
    ],
    quandoBuscar: "Se o estresse está afetando sua saúde, seu sono ou suas relações de forma persistente, procure um profissional de saúde.",
  },
  solidao: {
    nome: "Solidão",
    glow: "#F472B6",
    resumo: "Sentir-se desconectado das pessoas, mesmo quando há gente por perto.",
    oQueE: "A solidão é um sentimento de desconexão e isolamento, mesmo quando se está rodeado de pessoas. É diferente da solitude, que é a escolha consciente de passar tempo sozinho. A solidão é um estado emocional que pode ser doloroso e afetar a saúde mental.",
    sinais: {
      "O que se sente": ["Tristeza e sensação de vazio", "Medo de rejeição", "Baixa autoestima", "Pensamentos negativos repetitivos"],
      "O que muda": ["Sono e apetite alterados", "Afastamento de atividades sociais", "Falta de interesse em sair ou conversar"],
    },
    ajuda: [
      ["Reconecte-se", "Retome o contato com amigos e familiares; uma mensagem curta já é um começo."],
      ["Grupos e interesses", "Cursos, clubes, voluntariado e grupos de interesse facilitam novas amizades."],
      ["Autocompaixão", "Seja gentil consigo mesmo: todos se sentem sozinhos de vez em quando."],
      ["Ajuda profissional", "Um terapeuta pode ajudar a entender as causas e a criar estratégias de conexão."],
    ],
    quandoBuscar: "Se a solidão vem acompanhada de tristeza persistente ou pensamentos de desistir, converse com alguém hoje: o CVV (188) atende 24 horas.",
  },
  bipolaridade: {
    nome: "Bipolaridade",
    glow: "#F59F00",
    resumo: "Oscilações intensas de humor e energia, entre fases de euforia e de depressão.",
    oQueE: "O transtorno bipolar é uma condição em que o humor e a energia alternam entre episódios de euforia ou irritabilidade (mania ou hipomania) e episódios de depressão, com períodos de estabilidade entre eles. Não é o mesmo que mudar de humor ao longo do dia: os episódios duram dias ou semanas.",
    sinais: {
      "Fase de euforia": ["Pouca necessidade de sono", "Fala e pensamento acelerados", "Impulsividade (gastos, decisões arriscadas)", "Autoconfiança exagerada", "Irritabilidade"],
      "Fase depressiva": ["Tristeza e falta de energia", "Perda de interesse", "Alterações de sono e apetite", "Pensamentos de morte"],
    },
    ajuda: [
      ["Acompanhamento médico", "O tratamento é contínuo e envolve psiquiatra; estabilizadores de humor são comuns e só devem ser ajustados pelo médico."],
      ["Psicoterapia", "Ajuda a reconhecer sinais de início de um episódio e a organizar a rotina."],
      ["Rotina de sono", "Horários regulares de sono são um dos fatores de proteção mais importantes."],
      ["Diário de humor", "Registrar humor, sono e energia ajuda o paciente e o profissional a perceber padrões."],
      ["Rede de apoio", "Pessoas próximas podem ajudar a perceber mudanças antes que se agravem."],
    ],
    quandoBuscar: "Se você percebe fases de energia e euforia fora do comum alternadas com fases de depressão, procure um psiquiatra. Em crise, ligue 188 (CVV) ou 192 (SAMU).",
  },
  personalidade: {
    nome: "Personalidade",
    glow: "#0F9D58",
    resumo: "Padrões persistentes de relacionamento e emoção que trazem sofrimento.",
    oQueE: "Os transtornos de personalidade envolvem padrões duradouros de pensar, sentir e se relacionar que causam sofrimento e dificuldades. Exemplos são o transtorno de personalidade borderline, marcado por emoções intensas e instáveis e medo de abandono, e o evitativo, marcado por forte medo de rejeição e isolamento.",
    sinais: {
      "Emoções": ["Emoções muito intensas e que mudam rápido", "Sensação crônica de vazio", "Raiva difícil de controlar"],
      "Relações": ["Medo intenso de abandono ou rejeição", "Relações instáveis e intensas", "Evitar contato social por medo de crítica", "Impulsividade"],
    },
    ajuda: [
      ["Psicoterapia especializada", "Abordagens como a terapia comportamental dialética (DBT) têm boa evidência, principalmente para o borderline."],
      ["Regulação emocional", "Aprender a nomear emoções e a atravessar picos de intensidade sem agir por impulso."],
      ["Rede de apoio", "Relações estáveis e grupos de apoio ajudam a reduzir o isolamento."],
      ["Paciência com o processo", "O tratamento é gradual, e a melhora é real com acompanhamento."],
    ],
    quandoBuscar: "O diagnóstico só pode ser feito por um profissional de saúde mental. Se você se identifica com esses padrões e eles trazem sofrimento, procure um psicólogo ou psiquiatra.",
  },
};

/* Ordem de exibição na página inicial */
window.MAIND_TEMAS_ORDEM = ["ansiedade", "depressao", "estresse", "bipolaridade", "personalidade", "solidao"];
