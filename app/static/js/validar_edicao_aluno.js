document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('editarAlunoForm');
  const nomeInput = document.getElementById('nome');
  const cpfInput = document.getElementById('cpf');
  const cidadeInput = document.getElementById('cidade');
  const estadoInput = document.getElementById('estado');
  const telefoneInput = document.getElementById('telefone');
  const dataMatriculaInput = document.getElementById('data_matricula');
  const dataVencimentoInput = document.getElementById('data_vencimento');

  cpfInput.addEventListener('input', () => {
    let val = cpfInput.value.replace(/\D/g, '').slice(0, 11);
    val = val.replace(/(\d{3})(\d)/, '$1.$2');
    val = val.replace(/(\d{3})(\d)/, '$1.$2');
    val = val.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    cpfInput.value = val;
  });

  telefoneInput.addEventListener('input', () => {
    let val = telefoneInput.value.replace(/\D/g, '');
    if (val.length > 11) val = val.slice(0, 11);

    if (val.length > 10) {
      val = val.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
    } else if (val.length > 5) {
      val = val.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
    } else if (val.length > 2) {
      val = val.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
    } else {
      val = val.replace(/^(\d*)/, '($1');
    }

    telefoneInput.value = val;
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    event.stopPropagation();

    let valido = true;

    [nomeInput, cpfInput, cidadeInput, estadoInput, telefoneInput, dataMatriculaInput, dataVencimentoInput]
      .forEach(input => input.classList.remove('is-invalid'));

    if (nomeInput.value.trim().length < 2) {
      nomeInput.classList.add('is-invalid');
      valido = false;
    }
    const cpfNumeros = cpfInput.value.replace(/\D/g, '');
    if (
      cpfNumeros.length !== 11 ||
      /^(\d)\1{10}$/.test(cpfNumeros)
    ) {
      cpfInput.classList.add('is-invalid');
      valido = false;
    }
    if (cidadeInput.value.trim().length < 2) {
      cidadeInput.classList.add('is-invalid');
      valido = false;
    }
    if (!/^[A-Z]{2}$/.test(estadoInput.value.trim().toUpperCase())) {
      estadoInput.classList.add('is-invalid');
      valido = false;
    }
    const telefoneNumeros = telefoneInput.value.replace(/\D/g, '');
    if (
      (telefoneNumeros.length !== 10 && telefoneNumeros.length !== 11) ||
      /^(\d)\1{9,10}$/.test(telefoneNumeros)
    ) {
      telefoneInput.classList.add('is-invalid');
      valido = false;
    }
    if (!dataMatriculaInput.value) {
      dataMatriculaInput.classList.add('is-invalid');
      valido = false;
    }

    if (!dataVencimentoInput.value) {
      dataVencimentoInput.classList.add('is-invalid');
      valido = false;
    }
    if (valido) {
      alert('Formulário válido e enviado com sucesso!');
      form.submit();
    }
  });
});
