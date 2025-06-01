document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('cadastroForm');
  const nomeInput = document.getElementById('nome');
  const cpfInput = document.getElementById('cpf');
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

  [nomeInput, cidadeInput, estadoInput, telefoneInput, cpfInput].forEach(input => limparEspacosInicio(input));
  soLetras(nomeInput);
  soLetras(cidadeInput);
  soLetras(estadoInput);

  estadoInput.addEventListener('input', () => {
    estadoInput.value = estadoInput.value.toUpperCase().slice(0, 2);
  });

  telefoneInput.addEventListener('input', () => {
    let digits = telefoneInput.value.replace(/\D/g, '').slice(0, 11);

    if (digits.length === 11) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
    } else if (digits.length === 10) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
    } else if (digits.length > 2) {
      telefoneInput.value = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
    } else if (digits.length > 0) {
      telefoneInput.value = `(${digits}`;
    } else {
      telefoneInput.value = '';
    }
  });

  cpfInput.addEventListener('input', () => {
    let digits = cpfInput.value.replace(/\D/g, '').slice(0, 11);
    let formatted = '';

    if (digits.length <= 3) {
      formatted = digits;
    } else if (digits.length <= 6) {
      formatted = `${digits.slice(0, 3)}.${digits.slice(3)}`;
    } else if (digits.length <= 9) {
      formatted = `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
    } else {
      formatted = `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
    }

    cpfInput.value = formatted;
  });

  const formatDateBR = (dateString) => {
    if (!dateString) return '';

    const parts = dateString.split('-');
    if (parts.length !== 3) return '';

    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);

    const date = new Date(year, month, day);
    if (isNaN(date)) return '';

    const dayStr = day.toString().padStart(2, '0');
    const monthStr = (month + 1).toString().padStart(2, '0');
    return `${dayStr}/${monthStr}/${year}`;
  };

  const todayISO = () => {
    const hoje = new Date();
    const y = hoje.getFullYear();
    const m = (hoje.getMonth() + 1).toString().padStart(2, '0');
    const d = hoje.getDate().toString().padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  const addDays = (dateString, days) => {
    const date = new Date(dateString);
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  };

  dataMatriculaInput.type = 'date';
  dataMatriculaInput.value = todayISO();

  dataMatriculaInput.addEventListener('input', () => {
    if (dataMatriculaInput.value) {
      const vencimentoISO = addDays(dataMatriculaInput.value, 30);
      dataVencimentoInput.value = formatDateBR(vencimentoISO);
    } else {
      dataVencimentoInput.value = '';
    }
  });

  dataVencimentoInput.readOnly = true;
  const vencimentoInicial = addDays(dataMatriculaInput.value, 30);
  dataVencimentoInput.value = formatDateBR(vencimentoInicial);

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

    const cpfNumeros = cpfInput.value.replace(/\D/g, '');
    const cpfValido = /^\d{11}$/.test(cpfNumeros) && !/^0+$/.test(cpfNumeros);
    if (!cpfValido) {
      cpfInput.classList.add('is-invalid');
      valido = false;
    } else {
      cpfInput.classList.remove('is-invalid');
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

    const telefoneNumeros = telefoneInput.value.replace(/\D/g, '');
    const telefoneValido = /^(\d{10}|\d{11})$/.test(telefoneNumeros) && !/^0+$/.test(telefoneNumeros);
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
      alert('Formulário válido e enviado com sucesso!');
      form.submit();
    }
  });
});
