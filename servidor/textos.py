"""Textos fixos do bot: nunca passam pela IA.

PROVISÓRIOS: a resposta de crise definitiva é escrita pelo Integrante 2 e aprovada pelo grupo
(protocolo de crise). Quando ela existir, substitua `RESPOSTA_CRISE` aqui.
"""

RESPOSTA_CRISE = (
    "Sinto muito que você esteja passando por isso. Você não está sozinho e merece ajuda agora. "
    "Ligue para o CVV no 188 (gratuito, 24h) ou acesse cvv.org.br. "
    "Se for uma emergência, ligue 192 (SAMU)."
)

# Usada quando alguma parte falha, a IA não responde ou a revisão barra a resposta.
RESPOSTA_RESERVA = (
    "Desculpa, tive um problema para responder agora, mas continuo aqui com você. "
    "Pode me contar de novo, com suas palavras, o que está acontecendo? "
    "Se precisar conversar com alguém agora, o CVV atende 24h pelo 188."
)
