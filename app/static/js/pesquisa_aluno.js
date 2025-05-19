document.getElementById('form-busca').addEventListener('submit', function(e) {
  e.preventDefault();

  const entrada = document.getElementById('input-busca').value.trim();
  const msgVazia = document.getElementById('mensagem-vazia');
  const naoEncontrado = document.getElementById('nao-encontrado');
  const cartaoAluno = document.getElementById('cartao-aluno');

  msgVazia.style.display = 'none';
  naoEncontrado.style.display = 'none';
  cartaoAluno.style.display = 'none';

  if (!entrada) {
    msgVazia.style.display = 'block';
    return;
  }
  naoEncontrado.style.display = 'block';
});
