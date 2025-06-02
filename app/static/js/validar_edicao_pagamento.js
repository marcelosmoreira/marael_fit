document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const formaPagamento = document.getElementById('forma_pagamento');
  const dataPagamento = document.getElementById('data_pagamento');

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const forma = formaPagamento.value;
    const data = dataPagamento.value;

    if ((forma === 'Dinheiro' || forma === 'Cartão') && !data) {
      alert('Por favor, preencha a Data do Pagamento para essa forma de pagamento.');
      dataPagamento.focus();
      return;
    }

    if (confirm('Deseja salvar a Edição do Pagamento?')) {
      alert('Edição do Pagamento enviado com sucesso!');
      form.submit();
    }
  });
});