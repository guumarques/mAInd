# mAInd · Divisão do trabalho

## Sobre o projeto

### O que é

A disciplina C318 pede um projeto prático de machine learning que resolva um problema de negócio escolhido pelo grupo. O professor avalia o caminho completo: entender o problema, conseguir e analisar dados, criar e avaliar modelos e apresentar os resultados. As entregas são o código, a documentação e a apresentação. O escopo oficial está no arquivo `Projeto_C318.pdf`.

O projeto do grupo é o **mAInd**, um chatbot de acolhimento para pessoas que estão passando por ansiedade, depressão, estresse e outros sofrimentos. Ele conversa como um amigo, ajuda a pessoa a entender o que está sentindo e mostra caminhos de apoio. Ele não faz diagnóstico e não substitui um profissional.

### Objetivo final

A pessoa abre o site, escreve com as próprias palavras como está se sentindo, e o bot responde de forma natural, lembrando o que já foi dito, com informação confiável e com cuidado especial se houver sinal de crise. Além de funcionar, o grupo precisa provar com números que o bot funciona e que é melhor que a versão antiga.

### O que o professor autorizou

O grupo pode usar uma IA pronta que escreve texto (do tipo ChatGPT) para redigir as respostas do bot, desde que a parte que a disciplina avalia, os modelos de machine learning que entendem a mensagem, seja feita e avaliada pelo próprio grupo. Por isso cada integrante tem uma parte de machine learning ou de análise com resultado medido.

### Como o chatbot vai funcionar

Cada mensagem passa por 5 etapas, sempre nesta ordem:

```
 mensagem da pessoa
        │
 1. SEGURANÇA ......... é uma situação de crise? Se for, o bot responde na hora         (Integrante 2)
        │               com uma mensagem de apoio pronta (CVV 188, SAMU 192).
 2. ENTENDIMENTO ...... sobre qual tema a pessoa fala? O que ela quer agora           (Integrantes 1 e 4)
        │               (desabafar, pedir informação, só dizer "oi")?
 3. CONHECIMENTO ...... busca, numa biblioteca de textos confiáveis escritos          (Integrante 3)
        │               pelo grupo, o que ajuda naquele assunto.
 4. CONVERSA .......... a IA escreve a resposta com jeito de amigo, usando o que      (Integrante 4)
        │               já foi conversado e os textos encontrados.
 5. REVISÃO ........... antes de aparecer, a resposta é conferida: sem diagnóstico,   (Integrante 2)
        │               sem remédio, sem promessas.
        ▼
 resposta no site                                                                    (Integrante 5 liga
                                                                                      tudo e cuida do site)
```

### O que já existe hoje

Repositório: **https://github.com/guumarques/mAInd**

- **Pasta `frontend`: o site, pronto visualmente.** Tem página inicial, página de chat e páginas de conteúdo sobre cada tema. O chat tem um painel lateral, "Análise do modelo", que mostra como o bot entendeu a última mensagem. Como ainda não existe o servidor novo, o chat funciona em "modo demonstração": as respostas são simuladas a partir de palavras-chave, e a tela avisa isso. Para ver o site, basta entrar na pasta `frontend` pelo terminal, rodar `python -m http.server 8080` e abrir `http://127.0.0.1:8080`. O `README.md` dessa pasta descreve como o site espera conversar com o servidor. Alguns textos do site e os números de exemplo da página inicial descrevem um modelo de teste que não existe mais e precisam ser atualizados.
- **Pasta `backend`: a versão antiga do bot.** Faz 24 perguntas de "sim" ou "não" e, no final, um modelo simples escolhe um entre 5 rótulos e responde com uma frase escrita à mão. Não há nenhuma IA escrevendo texto, por isso a conversa parece um formulário. A pasta tem duas bases de dados:
  - `dataset.csv`: parece grande (40.960 linhas), mas são só 5 linhas diferentes repetidas milhares de vezes. Não serve para treinar nada.
  - `data_to_be_cleansed.csv`: cerca de 6 mil posts do Reddit, em inglês, separados em 5 temas numerados de 0 a 4. O arquivo não diz o que cada número significa; pelas palavras mais comuns, parecem ser 0 estresse, 1 depressão, 2 bipolaridade, 3 transtorno de personalidade e 4 ansiedade. O tema de cada post é o fórum onde ele foi publicado, não um diagnóstico. Tem duplicados e posts que não são relatos pessoais.

### Como o trabalho acontece em paralelo

Cada parte do sistema é feita por uma pessoa diferente, mas todas precisam se encaixar. Para ninguém ficar parado esperando outra pessoa:

- **Logo no começo, cada integrante combina com o Integrante 5 o que a própria parte recebe e o que devolve.** A ideia geral está na tabela abaixo; os detalhes são decididos entre quem entrega e quem usa.
- **Logo no começo, cada parte também ganha uma versão provisória**, que finge funcionar (devolve sempre a mesma resposta). Com ela, o Integrante 5 já monta o chat inteiro. Depois a versão real entra no lugar, sem mexer no resto.

| Parte | Recebe | Devolve |
|---|---|---|
| Segurança na entrada (Integrante 2) | a mensagem e a conversa até ali | se é crise ou não, e por quê |
| Segurança na saída (Integrante 2) | a resposta que a IA escreveu | se pode ser mostrada ou não, e por quê |
| Tema (Integrante 1) | a mensagem e a conversa até ali | o tema mais provável, o quanto o modelo tem certeza e a chance de cada tema |
| Intenção (Integrante 4) | a mensagem | o que a pessoa quer naquele momento e o quanto o modelo tem certeza |
| Conhecimento (Integrante 3) | o que a pessoa disse e, se houver, o tema | alguns trechos úteis, cada um com título e link da fonte |
| Conversa com a IA (Integrante 4) | a conversa até ali e as orientações (tema, trechos, regras) | a resposta, que vai aparecendo aos poucos na tela |
| Servidor (Integrante 5) | a mensagem que vem do site | a resposta e as informações que o painel "Análise do modelo" mostra |

### O que não faz parte do projeto

Proteção contra ataques e invasões, login de usuários, aplicativo de celular, colocar o site no ar na internet e uso clínico real.

---

## O que cada integrante vai fazer

Cada integrante tem uma única tarefa, que vai do começo ao fim do projeto. As cinco têm carga parecida. Cada tarefa diz o que precisa existir no final e por quê; ferramentas, bibliotecas e o jeito de fazer são decisão de quem a assume. O que aparecer no caminho e não estiver aqui, o grupo decide junto.

---

### Integrante 1 · Tema da conversa e documentação do projeto

**Responsável:** ______

**Resumo:** o Integrante 1 ensina o bot a perceber sobre qual assunto a pessoa está falando e cuida da documentação do projeto, do documento de partida ao relatório final.

**Por que essa função existe:** o bot só consegue buscar o conteúdo certo e responder no assunto certo se souber do que a pessoa está falando. Esse modelo é o principal ponto de machine learning que o professor vai avaliar. E a documentação é um dos três entregáveis: é por ela que o professor vê o projeto inteiro.

**O que o Integrante 1 vai fazer:**

- **Escrever o documento de partida do projeto, logo no começo.** Um documento curto que deixa claro para o grupo e para o professor: qual é o problema e quem sofre com ele, o que o mAInd entrega para essas pessoas, o que os modelos precisam descobrir, quais perguntas de negócio o projeto responde, que tipo de machine learning é usado em cada parte, como o sucesso vai ser medido e o que fica de fora. O professor pede isso como primeira etapa (o `Projeto_C318.pdf` serve de roteiro). O grupo lê e aprova antes de seguir, porque esse documento é a referência de todo mundo.
- **Conseguir e preparar os dados.** Montar uma base de textos já marcados por tema, de preferência em português. No repositório já existe uma base que pode servir de ponto de partida: o arquivo `data_to_be_cleansed.csv`, na pasta `backend`, com cerca de 6 mil posts do Reddit em inglês, separados em 5 temas (mais detalhes em "O que já existe hoje"). Ela pode ser trocada por uma base melhor. É preciso limpar o que atrapalha (duplicados, textos vazios, posts que não são relatos) e descrever de onde os dados vieram e o que cada tema significa. Antes de qualquer análise, uma parte dos dados (cerca de 20%) é separada e fica guardada só para a conferência final; se essa parte for usada para tomar decisões, o resultado deixa de ser confiável. Se não houver boa base em português, vale treinar com uma em inglês, desde que o teste final use frases em português. O tema "solidão" aparece no site, mas não nas bases atuais; o Integrante 1 decide junto com o Integrante 3 se ele entra no modelo ou fica só como conteúdo informativo.
- **Criar e escolher o modelo de tema.** Comparar pelo menos três abordagens, incluindo uma bem simples que sirva de referência (por exemplo, sempre responder o tema mais comum), para mostrar quanto os modelos realmente melhoram. A medida usada é uma nota que equilibra os acertos de todos os temas (chamada F1 macro), para que um tema com muitos exemplos não esconda um tema em que o modelo vai mal. Exemplos reais de erro são analisados para entender em quais temas o modelo se confunde e por quê. A escolha final precisa ser justificada com números, e qualquer pessoa do grupo deve conseguir rodar a análise e chegar aos mesmos resultados.
- **Decidir quando o bot pode confiar no tema.** O modelo sempre dá uma resposta, mesmo quando não tem certeza. O Integrante 1 define, com base em dados, a partir de que nível de confiança o bot segue com o tema e abaixo de qual ele faz mais perguntas antes de sugerir algo. O modelo é testado com pelo menos 50 frases em português escritas pelo grupo especialmente para esse teste (frases inventadas, que nunca foram usadas no treino), porque é assim que ele vai ser usado de verdade.
- **Deixar o modelo pronto para o sistema usar.** Logo no começo, o Integrante 1 entrega ao Integrante 5 uma versão provisória da parte de tema: algo simples que recebe a mensagem e devolve sempre o mesmo resultado, só para o Integrante 5 conseguir montar o chat antes de o modelo existir. Quando o modelo estiver escolhido, ela é trocada pela versão real, que responde rápido (menos de 1 segundo por mensagem), tem testes automáticos simples e vem com instruções para qualquer pessoa do grupo treinar o modelo do zero.
- **Montar o relatório final.** Juntar num documento único o contexto, os dados, cada modelo do projeto e seus resultados, a avaliação com pessoas (feita pelo Integrante 4) e o experimento comparativo (feito pelo Integrante 5), as decisões importantes, as limitações e os cuidados éticos. Os resultados são contados de duas formas, como o professor pede: uma técnica e uma em linguagem simples para quem não é da área. O relatório inclui um diagrama de como o sistema funciona e mantém o mesmo tom do início ao fim. Entre as limitações, fica registrado que a avaliação com pessoas foi feita pelo próprio grupo.

**Depende de outros integrantes? Sim.**

- **Integrante 5, no começo:** o repositório organizado e o combinado de como a parte de tema recebe a mensagem e devolve o resultado. Sem isso, a versão provisória não tem onde nem como ser entregue. Enquanto isso, dá para adiantar o documento de partida e os dados.
- **Integrante 2, perto do fim:** os cuidados éticos e de privacidade do projeto, que entram no relatório.
- **Integrante 3, perto do fim:** a análise dos dados sem rótulos (o agrupamento automático), que entra no capítulo de dados do relatório.
- **Integrante 4 e Integrante 5, no fim:** os resultados da avaliação feita com pessoas (Integrante 4) e do experimento que compara versões do sistema (Integrante 5). Eles são o centro do capítulo de resultados.
- **Todos os integrantes, no fim:** a página que cada um escreve sobre a própria parte.

**Quem depende do Integrante 1:**

- **Todos:** o documento de partida é a referência do que o grupo está construindo.
- **Integrante 3:** precisa da base de textos limpa para fazer o agrupamento automático, e do relatório pronto para a conferência final da entrega.
- **Integrante 4:** precisa saber a partir de que confiança o bot pode seguir com o tema, para definir quando ele pergunta mais.
- **Integrante 5:** precisa da versão provisória da parte de tema no começo e da versão real no meio do projeto, para montar o sistema completo.

---

### Integrante 2 · Segurança da conversa e ética

**Responsável:** ______

**Resumo:** o Integrante 2 garante que o bot cuida de quem está em crise e nunca diz algo perigoso, define os cuidados éticos do projeto e monta os slides da apresentação.

**Por que essa função existe:** quem procura um chatbot de saúde mental pode estar em sofrimento grave. Um bot que não percebe uma crise, ou que dá um diagnóstico ou indica um remédio, pode fazer mal de verdade. Aqui "segurança" não tem nada a ver com ataque ou invasão: é cuidar de pessoas vulneráveis. Além disso, a apresentação é um dos três entregáveis, e quem define os limites do que o bot pode e não pode prometer é quem melhor consegue contar essa história.

**O que o Integrante 2 vai fazer:**

- **Definir o protocolo de crise, logo no começo.** Um documento curto que diz o que conta como sinal de crise (dito com todas as letras, dito de forma indireta ou falando de outra pessoa), qual é a resposta do bot nesses casos, o que ele nunca deve dizer e o que fazer se a pessoa disser depois que estava exagerando. A resposta de crise é um texto fixo, escrito e aprovado pelo grupo, com os contatos de apoio (CVV 188 e SAMU 192). Ela não é gerada pela IA, para não haver risco de erro. O protocolo se baseia em orientações confiáveis (como as do CVV e do Ministério da Saúde), com as fontes citadas. O grupo aprova antes de qualquer regra de conversa ser escrita.
- **Montar a lista de testes de segurança.** Pelo menos 60 mensagens difíceis, cada uma com a reação esperada do bot: crise dita claramente; crise dita de forma indireta, com gírias e jeitos comuns de falar; mensagens que parecem crise mas não são ("essa piada me mata de rir", "não quero me matar, só estou cansado"); crise de outra pessoa; pedidos de diagnóstico; pedidos de remédio ou dose; tentativas de fazer o bot ignorar as próprias regras. Essa lista é usada sempre que algo mudar no bot e é a prova de segurança do projeto no relatório. Uma parte dela fica separada e nunca é usada para ensinar o detector, só para testá-lo no final.
- **Construir o detector de sinais de risco.** Uma lista fixa de palavras pega o óbvio, mas deixa passar o indireto ("queria sumir", "não vejo mais sentido"). O detector combina regras com um modelo que aprende com exemplos. O Integrante 2 consegue os dados de que ele precisa (bases públicas, exemplos criados pelo grupo, ou os dois), cuidando da variedade. A base antiga do projeto (`dataset.csv`, na pasta `backend`) é o exemplo do que evitar: tem 40 mil linhas, mas só 5 frases diferentes repetidas, e por isso não ensina nada a um modelo. Aqui o pior erro é deixar passar uma crise real, então a prioridade é encontrar todas, mesmo que isso gere alguns alarmes falsos. O resultado é medido por quantas crises o detector encontrou do total (chamado recall) e quantos alarmes falsos deu. A meta é encontrar 100% das crises ditas claramente.
- **Deixar a segurança pronta para o sistema usar.** Logo no começo, o Integrante 2 entrega ao Integrante 5 uma versão provisória, que sempre responde "está tudo bem", só para o Integrante 5 conseguir montar o chat. Depois vem a versão real, que age em dois momentos: antes de responder (a mensagem da pessoa indica crise?) e depois que a IA escreve (a resposta pode ser mostrada?). Uma resposta não pode dar diagnóstico, citar nome de remédio ou dose, prometer resultado ("vai ficar tudo bem") nem ser longa demais. A lista de testes roda de forma automática contra essa parte.
- **Definir os cuidados éticos e de privacidade.** Decisões curtas e escritas sobre: o que o bot diz sobre si mesmo (que é uma IA, que não faz diagnóstico, que não substitui um profissional); se as conversas são guardadas e por quanto tempo; como o usuário apaga a conversa; e o que o grupo pode usar nos testes (nada de mensagens reais de outras pessoas). O Integrante 2 também escreve o texto do aviso que aparece no site antes da primeira conversa, em linguagem simples, e as limitações éticas do projeto para o relatório.
- **Montar os slides da apresentação.** Contar a história do projeto (problema, solução, como funciona, resultados, limitações e próximos passos) em duas camadas, como o professor pede: a de negócio (o valor para a pessoa, o que o bot faz e o que não faz) e a técnica (dados, modelos, avaliações e comparações). Os slides que cada integrante fizer sobre a própria parte entram na apresentação, com visual coerente com o site, dentro do tempo definido pelo professor.

**Depende de outros integrantes? Sim.**

- **Integrante 5, no começo:** o repositório organizado e o combinado de como a parte de segurança recebe e devolve as informações. Enquanto isso, dá para adiantar o protocolo de crise, a lista de testes e os cuidados éticos, que não dependem de ninguém.
- **Integrante 4 e Integrante 5, no fim:** os resultados da avaliação em que o grupo dá notas às respostas do bot (organizada pelo Integrante 4) e do experimento que compara versões do sistema com e sem cada parte (feito pelo Integrante 5). Eles vão para os slides.
- **Todos os integrantes, no fim:** os slides que cada um faz sobre a própria parte.

**Quem depende do Integrante 2:**

- **Integrante 4:** precisa do protocolo de crise e da lista de testes para escrever as regras de conversa do bot e testar se ele as respeita.
- **Integrante 5:** precisa da versão provisória da segurança no começo e da real no meio do projeto; dos cuidados éticos para decidir o que o servidor guarda e o que o site avisa; e da lista de testes para o experimento em que compara versões do sistema com e sem cada parte.
- **Integrante 1:** precisa dos cuidados éticos e dos resultados de segurança para o relatório.
- **Todos:** os slides são a base do ensaio da apresentação.

---

### Integrante 3 · Biblioteca de conhecimento

**Responsável:** ______

**Resumo:** o Integrante 3 cria a biblioteca de textos confiáveis que o bot consulta antes de responder, faz o bot encontrar o trecho certo, analisa os dados sem rótulos para descobrir padrões, cria exercícios guiados, prepara a demonstração e faz a conferência final da entrega.

**Por que essa função existe:** se o bot depender só do que a IA "sabe", ele pode errar ou inventar informação sobre saúde mental. Com uma biblioteca escrita e revisada pelo grupo, com fonte conhecida, as respostas ficam corretas e dá para mostrar de onde veio cada informação. Essa função também traz um segundo tipo de machine learning ao projeto (agrupar textos sem dizer o tema) e cuida de que o projeto funcione na apresentação e rode na máquina do professor.

**O que o Integrante 3 vai fazer:**

- **Escrever a biblioteca de conhecimento.** Um texto em português para cada tema (ansiedade, depressão, estresse, bipolaridade, transtorno de personalidade e solidão) explicando o que é, os sinais comuns, o que costuma ajudar e quando procurar um profissional. Linguagem simples e acolhedora, sem diagnosticar ninguém, baseada em fontes confiáveis (como CVV, Ministério da Saúde, OMS e SUS), com o link da fonte em cada texto. O site já tem uma página para cada tema, com textos que podem servir de ponto de partida; esse conteúdo está no arquivo `temas.js`, na pasta `frontend/assets/js`. Como site e bot vão usar o mesmo conteúdo, o Integrante 3 combina com o Integrante 5 para não existirem duas versões diferentes. Outra pessoa do grupo revisa os textos.
- **Fazer o bot encontrar o trecho certo.** O bot precisa achar o trecho certo mesmo quando a pessoa não usa as palavras do texto: quem escreve "meu coração dispara do nada" deve chegar ao trecho sobre ansiedade, mesmo sem a palavra "ansiedade" na mensagem. Logo no começo, o Integrante 3 entrega ao Integrante 5 uma versão provisória, que devolve sempre os mesmos trechos, só para o Integrante 5 conseguir montar o chat; depois vem a versão real. Para medir se funciona, o Integrante 3 cria pelo menos 30 perguntas de teste com o trecho certo já conhecido e verifica em quantas o trecho certo aparece entre os três primeiros que o bot encontra. A meta inicial é 80%, e os casos em que a busca falha são analisados.
- **Analisar os dados sem rótulos.** Os outros modelos aprendem com exemplos já marcados. Aqui é o contrário: o computador separa os textos por semelhança, sem saber o tema de nenhum, para descobrir o que os dados mostram por conta própria. Há subtemas que ninguém previu? Existe um grupo de "solidão"? Os grupos aparecem em pelo menos um gráfico, com uma interpretação em texto: o que cada um parece representar, se eles batem com os temas conhecidos e o que isso muda (ou não) no projeto. Isso enriquece a análise de dados que o professor avalia.
- **Criar os exercícios guiados.** Às vezes a melhor ajuda na hora é algo prático. O Integrante 3 cria dois exercícios curtos com passo a passo em linguagem acolhedora (sugestão: um de respiração e um para trazer a atenção de volta ao presente) e combina com o Integrante 4 quando o bot oferece um exercício e com o Integrante 5 como ele aparece no site. Texto passo a passo é suficiente.
- **Preparar a demonstração e o plano B.** Demonstração ao vivo falha por falta de internet, por limite de uso da IA ou por um erro inesperado. O Integrante 3 monta o roteiro do que mostrar, em que ordem e o que falar em cada momento, incluindo um caso de crise e um em que o bot pede mais detalhes. O plano B fica pronto: um vídeo gravado da tela com a demonstração funcionando e exemplos de conversas guardados. Também há uma lista do que conferir antes de apresentar, e o roteiro é testado pelo menos uma vez em condições parecidas com as da apresentação.
- **Fazer a conferência final da entrega.** Um projeto que só roda no computador de quem fez não vale como entrega. Como o Integrante 5 montou o repositório, a conferência fica com o Integrante 3: um olhar de fora encontra o que quem montou não vê. A conferência verifica que o projeto roda do zero em outro computador seguindo só as instruções do repositório; que não há arquivos esquecidos, senhas nem chaves de acesso; que o relatório está coerente com o que o projeto faz; que as análises podem ser reproduzidas; e que o que ficou de fora está registrado e justificado. Por fim, o Integrante 3 envia a entrega ao professor no formato e no prazo pedidos.

**Depende de outros integrantes? Sim.**

- **Integrante 5, no começo:** o repositório organizado e o combinado de como a parte de conhecimento recebe a pergunta e devolve os trechos. Enquanto isso, dá para adiantar a escrita da biblioteca.
- **Integrante 1, no meio do projeto:** a base de textos limpa, usada na análise dos dados sem rótulos.
- **Integrante 4, no meio do projeto:** as regras de quando o bot oferece um exercício.
- **Integrante 5, no fim:** o sistema completo e estável, e o site mostrando os exercícios, para montar e gravar a demonstração.
- **Integrante 1 e Integrante 5, no fim:** o relatório final pronto e o repositório na versão final, para a conferência da entrega.

**Quem depende do Integrante 3:**

- **Integrante 4:** precisa saber como os trechos chegam (título, texto, fonte) para orientar a IA a usá-los, e precisa dos exercícios para incluí-los na conversa.
- **Integrante 5:** precisa da versão provisória da busca no começo e da real no meio do projeto; do conteúdo revisado para as páginas de tema do site; e dos exercícios para mostrá-los na tela.
- **Integrante 1:** precisa da análise dos dados sem rótulos para o relatório.
- **Todos:** o roteiro da demonstração é usado no ensaio, e a conferência final é o que libera a entrega.

---

### Integrante 4 · Conversa

**Responsável:** ______

**Resumo:** o Integrante 4 faz o bot conversar como um amigo: escolhe a IA que escreve as respostas, define a personalidade do bot, conecta o sistema a essa IA, cria o modelo que entende o que a pessoa quer, define como a conversa flui e prova, com uma avaliação feita por pessoas, que o bot novo é melhor que o antigo.

**Por que essa função existe:** o que faz o mAInd parecer um amigo, e não um formulário, é o jeito de conversar: acolher antes de sugerir, não despejar informação, não julgar, saber quando perguntar mais. A IA só faz isso de forma consistente com boas instruções e uma conexão confiável. E é preciso provar que tudo isso deu certo: naturalidade e acolhimento só podem ser julgados por pessoas.

**O que o Integrante 4 vai fazer:**

- **Escolher qual IA vai escrever as respostas, logo no começo.** As IAs variam muito em qualidade de português, velocidade, custo e limite de uso gratuito. O Integrante 4 testa 2 ou 3 opções (na nuvem ou rodando no próprio computador) com os mesmos pedidos, incluindo uma mensagem de crise, um pedido de diagnóstico e um desabafo longo, compara os resultados e leva uma recomendação para o grupo decidir. Também fica definido como o grupo vai ter acesso: quem cria a conta, de onde vem o crédito e qual o limite de gasto aceito. A chave de acesso funciona como uma senha e nunca vai para o GitHub.
- **Definir a personalidade e as regras de conversa do bot.** Um documento com o jeito de falar do bot (tom, tamanho das respostas, o que ele valoriza) e as regras dele: admite que é uma IA quando perguntam, não faz diagnóstico, não indica remédio, não promete resultado, sugere procurar um profissional quando faz sentido e, quando a pessoa fala em se machucar, segue o protocolo de crise que o Integrante 2 vai escrever (as regras do que o bot faz e diz nesses casos). O documento traz exemplos de boas e de más respostas, com explicação. Com base nele, o Integrante 4 escreve as instruções que a IA recebe e testa em pelo menos 10 conversas, incluindo mensagens da lista de testes de segurança que o Integrante 2 vai montar (mensagens difíceis, cada uma com a reação esperada do bot).
- **Conectar o sistema à IA de forma confiável.** É a parte que de fato faz o bot falar. Logo no começo, o Integrante 4 entrega ao Integrante 5 uma versão provisória, que devolve sempre a mesma frase, só para o Integrante 5 conseguir montar o chat. A versão real recebe a conversa e as orientações (tema, trechos da biblioteca, regras) e devolve a resposta de um jeito que ela possa ir aparecendo aos poucos no site. Se a IA demorar, falhar ou ficar sem crédito, o bot responde com uma mensagem acolhedora de reserva, em vez de travar na frente do usuário. Deve ser possível trocar de IA sem mexer no resto do sistema. Essa é a peça que mais trava o projeto se atrasar: sem ela não existe conversa de verdade.
- **Fazer o bot entender o que a pessoa quer.** Nem toda mensagem é um desabafo: "oi", "obrigado", "pode me ensinar um exercício?" e "qual a capital da França?" pedem reações diferentes. Sem isso, o bot trataria um simples "oi" como um relato e responderia sem sentido. O Integrante 4 cria um modelo de machine learning que identifica a intenção da pessoa (cumprimentar, desabafar, pedir informação, pedir exercício, agradecer, assunto fora do tema, e outras que o grupo achar necessárias). Para isso, monta uma base de pelo menos 300 frases em português marcadas por intenção, com variedade de verdade; se a IA for usada para sugerir frases, tudo é revisado à mão. O modelo é avaliado com frases separadas só para teste, usando a mesma nota que equilibra os acertos de todas as categorias (F1 macro), com meta inicial de 0,80. Logo no começo, o Integrante 5 também recebe uma versão provisória dessa parte (por exemplo, que sempre responde "desabafar").
- **Definir como a conversa flui (as "regras de condução").** Um bot que responde bem a cada mensagem, mas não sabe conduzir a conversa, continua soando mecânico. As regras definem o que o bot faz quando não tem certeza do tema, quando e como sugere um profissional, quando oferece um exercício guiado, como abre e encerra a conversa e o que faz com mensagens fora do tema. Elas são implementadas junto com o Integrante 5, e uma conversa de 8 mensagens ou mais mostra a condução funcionando.
- **Provar com pessoas que o bot novo é melhor.** Esta é a principal medida de negócio do projeto. Naturalidade e acolhimento não se medem com uma fórmula; quem julga são pessoas lendo as respostas. Tudo aqui é novo e criado pelo Integrante 4:
  - **Um conjunto de conversas de teste.** São conversas de exemplo, inventadas pelo grupo. Cada uma é uma sequência curta de mensagens (de 1 a 4) que um usuário poderia mandar ao bot, como "tô muito ansioso com a prova de amanhã" seguida de "não consigo dormir". Sugestão: cerca de 40 conversas, com umas 6 para cada tema, alguns casos difíceis (mensagens vagas, assunto fora do tema) e algumas crises. O número é só uma sugestão: precisa ser grande o bastante para cobrir todos os temas e pequeno o bastante para 5 pessoas conseguirem avaliar. Nenhuma mensagem real de outras pessoas é usada.
  - **Os critérios de nota e a planilha de avaliação.** O grupo combina o que vai ser avaliado (por exemplo: naturalidade, empatia, utilidade, segurança e adequação ao tema, de 1 a 5), e uma planilha recebe as notas de cada avaliador.
  - **As respostas para avaliar.** As conversas passam pelo bot antigo e pelo novo, e as respostas são misturadas para que quem avalia não saiba de qual bot cada uma veio. Atenção: o bot antigo (o que está hoje na pasta `backend`) só entende "sim" e "não" às 24 perguntas dele, então não dá para mandar a mesma mensagem livre aos dois. O grupo precisa decidir como fazer essa comparação de forma justa, e a decisão vai para o relatório.
  - **A análise.** Com as notas dos 5 integrantes, a análise traz médias, gráficos e uma conclusão: em quantas comparações o novo ganhou, onde foi pior e por quê.

  As conversas de teste e a planilha precisam estar prontas antes da avaliação começar, porque o Integrante 5 usa as mesmas conversas e a mesma planilha no experimento comparativo.

**Depende de outros integrantes? Sim.**

- **Integrante 5, no começo:** o repositório organizado e o combinado de como a conexão com a IA e o modelo de intenção recebem e devolvem as informações. Enquanto isso, dá para escolher a IA e escrever a personalidade.
- **Integrante 2, no começo:** o protocolo de crise (o que o bot faz e diz quando alguém fala em se machucar) e a lista de testes de segurança (mensagens difíceis, cada uma com a reação esperada do bot). As regras de conversa precisam respeitar o protocolo e ser testadas com a lista.
- **Integrante 3, na primeira metade do projeto:** como os trechos da biblioteca chegam (título, texto, fonte), para orientar a IA a usá-los; e os exercícios guiados, para incluí-los na conversa.
- **Integrante 1, no meio do projeto:** o nível de confiança a partir do qual o bot segue com o tema, para definir quando ele pergunta mais.
- **Integrante 5, no meio e no fim:** a junção das partes, para implementar as regras de condução, e o sistema completo funcionando no site, para gerar as respostas da avaliação com pessoas.

**Quem depende do Integrante 4:**

- **Integrante 5:** precisa da conexão com a IA (provisória no começo, real logo em seguida), sem a qual não existe a primeira conversa de verdade; do modelo de intenção; das regras de condução; e das conversas de teste e da planilha de notas criadas para a avaliação, porque o experimento comparativo usa as mesmas.
- **Todos:** dão notas na avaliação com pessoas.
- **Integrante 1 e Integrante 2:** precisam dos resultados da avaliação para o relatório e para os slides.

---

### Integrante 5 · Plataforma

**Responsável:** ______

**Resumo:** o Integrante 5 organiza o repositório onde todos trabalham, constrói o servidor e a memória da conversa, junta as partes de todos numa única conversa, conecta o site ao chat de verdade e faz o experimento que mostra o que cada parte acrescenta ao bot.

**Por que essa função existe:** cada integrante entrega uma parte do sistema, e alguém precisa garantir que elas funcionem juntas, na ordem certa, aparecendo no site. É também quem garante que o professor consiga rodar o que o grupo entregar. E falta responder uma pergunta que o professor provavelmente vai fazer: se o machine learning desenvolvido pelo grupo realmente melhora o bot, ou se bastava a IA que escreve texto. O experimento comparativo responde com dados.

**O que o Integrante 5 vai fazer:**

- **Organizar o repositório e o ambiente, logo no começo.** Cinco pessoas mexendo no mesmo projeto sem combinar onde cada coisa fica geram conflito e retrabalho. A organização das pastas é definida com o grupo e fica explicada no repositório. O bot antigo (o código que está hoje na pasta `backend`, o do questionário de 24 perguntas) é guardado à parte, sem atrapalhar o novo: ele ainda vai ser usado na avaliação do Integrante 4, que compara o bot antigo com o novo. O repositório também traz a lista das bibliotecas necessárias, instruções para preparar um computador do zero e um modelo do arquivo de configuração sem senhas: cada pessoa cria o próprio arquivo com as próprias chaves, e o arquivo real nunca vai para o GitHub. O README explica como ligar o projeto, de preferência com um único comando, e outra pessoa do grupo testa seguindo só o README.
- **Combinar com cada integrante o que a parte dele recebe e devolve, logo no começo.** É o que permite cinco pessoas trabalharem ao mesmo tempo sem se travarem. O ponto de partida é a tabela "Parte / Recebe / Devolve", no início deste documento. O Integrante 5 recebe de cada integrante uma versão provisória da respectiva parte (uma versão simples que finge funcionar), para montar o chat antes de tudo estar pronto.
- **Construir o servidor e a memória da conversa.** O site precisa de um servidor para mandar a mensagem e receber a resposta, inclusive com a resposta aparecendo aos poucos. O site já foi programado para mandar a mensagem e esperar a resposta num formato específico, descrito no arquivo `README.md` da pasta `frontend`. O servidor segue esse formato ou, se precisar mudar, os dois lados mudam juntos. O bot precisa lembrar o que já foi dito, senão cada resposta ignora as anteriores e a conversa parece mecânica: a memória da conversa de cada pessoa continua existindo se o servidor reiniciar e pode ser apagada pelo usuário. Só o necessário é guardado, seguindo os cuidados éticos do Integrante 2. Mensagens de erro devem ser compreensíveis.
- **Juntar todas as partes numa única conversa.** Cada mensagem passa pelas 5 etapas, nesta ordem: segurança, entendimento (tema e intenção), conhecimento, conversa com a IA e revisão da resposta (o desenho completo está no início deste documento). A junção começa com as versões provisórias e troca cada uma pela real à medida que chegam. O objetivo do meio do projeto é a **primeira conversa de verdade pelo site**, com a IA escrevendo as respostas, memória e segurança funcionando, mesmo que outras partes ainda sejam provisórias. Se alguma parte falhar, o sistema segue com uma resposta acolhedora de reserva, em vez de travar. Deve ser possível ligar e desligar cada parte por configuração, o que é necessário para o experimento comparativo. Testes automáticos cobrem as situações principais: conversa normal, crise, mensagem curta e falha da IA.
- **Conectar o site ao chat de verdade.** O site foi feito mostrando uma conversa simulada; agora ele precisa refletir o sistema real. A resposta aparece aos poucos, e cada situação tem tratamento visual claro: crise (com destaque forte e um botão para ligar para o CVV 188), pedido de mais detalhes, tema identificado com as fontes usadas e exercícios guiados. O site mostra o aviso inicial definido pelo Integrante 2 e tem um botão para apagar a conversa. O chat tem um painel lateral, "Análise do modelo", que hoje mostra dados simulados de como o bot entendeu a mensagem; ele passa a mostrar dados reais do sistema (é um ótimo momento da apresentação). A página inicial mostra exemplos de conversa com porcentagens de um modelo de teste que não existe mais, e alguns textos do site descrevem esse modelo: tudo isso é atualizado para o sistema real. As páginas de tema usam o conteúdo revisado pelo Integrante 3. O site precisa funcionar bem no celular e no computador e, se o servidor estiver fora do ar, avisar de forma amigável. Hoje, sem servidor, o site já simula respostas e avisa na tela que está em "modo demonstração"; isso pode ser mantido para esse caso.
- **Fazer o experimento que mostra o que cada parte acrescenta.** O experimento usa as conversas de teste que o Integrante 4 vai criar para a avaliação com pessoas (conversas de exemplo, inventadas pelo grupo, com mensagens que um usuário poderia mandar) e as passa por três versões do sistema: só a IA; a IA com o modelo de tema; e a IA com o modelo de tema e a biblioteca de conhecimento. A segurança fica ligada nas três. As versões são comparadas em segurança (usando a lista de mensagens difíceis que o Integrante 2 vai montar, cada uma com a reação esperada do bot), velocidade de resposta e custo. Para a qualidade, uma amostra de 10 conversas das três versões recebe notas dos 5 integrantes, com os mesmos critérios e a mesma planilha da avaliação do Integrante 4, no mesmo momento. O experimento fecha com uma tabela e uma conclusão em texto: o que cada parte melhorou e quanto custou.

**Depende de outros integrantes? Sim.** Esta é a função que mais depende das outras, porque junta o trabalho de todos.

- **Todos os integrantes, no começo:** o combinado do que cada parte recebe e devolve e as versões provisórias (tema do Integrante 1, segurança do Integrante 2, busca do Integrante 3, conexão com a IA e intenção do Integrante 4). Sem elas, não dá para montar o chat. Enquanto isso, dá para organizar o repositório e construir o servidor.
- **Integrante 4, na primeira metade do projeto:** a conexão real com a IA. Sem ela não existe a primeira conversa de verdade.
- **Integrantes 1, 2, 3 e 4, no meio do projeto:** as versões reais das partes e as regras de condução da conversa (quando o bot pergunta mais, sugere um profissional ou oferece um exercício), definidas pelo Integrante 4.
- **Integrante 2:** os cuidados éticos (o que o servidor guarda e o aviso do site) e, no fim, a lista de testes de segurança (mensagens difíceis, cada uma com a reação esperada do bot), usada no experimento.
- **Integrante 3:** o conteúdo revisado para as páginas de tema e os exercícios guiados para mostrar no site.
- **Integrante 4, perto do fim:** as conversas de teste e a planilha de notas criadas para a avaliação com pessoas; o experimento usa as mesmas.

**Quem depende do Integrante 5:**

- **Todos, no começo:** o repositório organizado e o combinado de como cada parte se conecta ao servidor.
- **Integrante 4:** precisa do sistema completo funcionando no site para gerar as respostas da avaliação com pessoas, e da junção das partes para implementar as regras de condução.
- **Integrante 3:** precisa do sistema completo e estável para a demonstração e do repositório pronto para a conferência final.
- **Integrante 1 e Integrante 2:** precisam do resultado do experimento para o relatório e para os slides.
- **Todos, no fim:** dão notas na amostra do experimento.

---