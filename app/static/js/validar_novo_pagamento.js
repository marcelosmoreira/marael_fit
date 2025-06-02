document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('formPagamento');

  form.addEventListener('submit', function(event) {
    event.preventDefault();

    const aluno = form.querySelector('#aluno');
    const valor = form.querySelector('#valor');
    const dataVencimento = form.querySelector('#data_vencimento');

    if (!aluno.value) {
      alert('Por favor, selecione um aluno.');
      aluno.focus();
      return;
    }

    const valorNum = parseFloat(valor.value);
    if (isNaN(valorNum) || valorNum <= 0) {
      alert('Por favor, informe um valor válido maior que zero.');
      valor.focus();
      return;
    }

    if (!dataVencimento.value) {
      alert('Por favor, informe a data de vencimento.');
      dataVencimento.focus();
      return;
    }

    if (confirm('Deseja enviar o Novo Pagamento?')) {
      alert('Novo pagamento enviado com sucesso!');
      form.submit();
    } else {
      return;
    }
  });
});