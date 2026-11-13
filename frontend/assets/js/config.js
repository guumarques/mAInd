/* Configuração do frontend. Altere a URL se o servidor rodar em outro endereço. */
window.MAIND_CONFIG = {
  // Servido pelo próprio servidor (python -m servidor, porta 8000): mesma origem.
  // Aberto direto do disco ou por outro servidor: procura a API em 127.0.0.1:8000.
  API_URL: location.port === "8000" ? "" : "http://127.0.0.1:8000",
  // Tempo máximo esperando o servidor começar a responder antes de usar o modo demonstração
  TIMEOUT_MS: 15000,
};
