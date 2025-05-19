document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('cadastroForm');
  const nomeInput = document.getElementById('nome');
  const cidadeInput = document.getElementById('cidade');
  const estadoInput = document.getElementById('estado');
  const telefoneInput = document.getElementById('telefone');
  const dataMatriculaInput = document.getElementById('dataMatricula');
  const dataVencimentoInput = document.getElementById('dataVencimento');

  const limparEspacosInicio = (input) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/^\s+/, '');
    });
  };

  const soLetras = (input) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/[^a-zA-ZÀ-ÿ\s]/g, '');
    });
  };

  [nomeInput, cidadeInput, estadoInput, telefoneInput].forEach(input => limparEspacosInicio(input));
  soLetras(nomeInput);
  soLetras(cidadeInput);
  soLetras(estadoInput);

  estadoInput.addEventListener('input', () => {
    estadoInput.value = estadoInput.value.toUpperCase().slice(0, 2);
  });
  telefoneInput.addEventListener('input', () => {
    let digits = telefoneInput.value.replace(/\D/g, '').slice(0, 11);

    if (digits.length >= 11) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
    } else if (digits.length >= 7) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
    } else if (digits.length >= 3) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    } else if (digits.length > 0) {
      telefoneInput.value = `(${digits}`;
    } else {
      telefoneInput.value = '';
    }
  });
  const hoje = new Date();
  const formatDate = (data) => data.toLocaleDateString('pt-BR');

  dataMatriculaInput.value = formatDate(hoje);
  dataVencimentoInput.value = formatDate(hoje)

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    event.stopPropagation();

    let valido = true;

    if (nomeInput.value.trim().length < 2) {
      nomeInput.classList.add('is-invalid');
      valido = false;
    } else {
      nomeInput.classList.remove('is-invalid');
    }

    if (cidadeInput.value.trim().length < 2) {
      cidadeInput.classList.add('is-invalid');
      valido = false;
    } else {
      cidadeInput.classList.remove('is-invalid');
    }

    if (estadoInput.value.trim().length !== 2) {
      estadoInput.classList.add('is-invalid');
      valido = false;
    } else {
      estadoInput.classList.remove('is-invalid');
    }

    const telefoneValido = /^\(\d{2}\) \d{5}-\d{4}$/.test(telefoneInput.value);
    if (!telefoneValido) {
      telefoneInput.classList.add('is-invalid');
      valido = false;
    } else {
      telefoneInput.classList.remove('is-invalid');
    }

    if (!form.checkValidity()) {
      valido = false;
    }

    form.classList.add('was-validated');

    if (valido) {
      alert('Formulário válido e pronto para envio!');
    }
  });
});
