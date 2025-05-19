const botaoSair = document.querySelector('.logout-btn');

if (botaoSair) {
  botaoSair.addEventListener('click', function (e) {
    e.preventDefault();

    const confirmarSaida = confirm('Deseja realmente sair da sessão?');
    if (confirmarSaida) {
      alertaAtivo = false;
      window.location.href = botaoSair.href;
    }
  });
}
