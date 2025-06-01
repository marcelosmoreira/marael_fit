import uuid
from datetime import datetime, timedelta, timezone
from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from app.model import usuarios
from app.model.aluno import Aluno
from app.model.pagamento import Pagamento
from sqlalchemy.orm import joinedload

sessoes_ativas = {}
session_TIMEOUT = timedelta(minutes=30)

def criar_token_session():
    return str(uuid.uuid4())

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token or token not in sessoes_ativas:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            session.clear()
            return redirect(url_for('login'))

        session_info = sessoes_ativas[token]

        if session_info['ip'] != request.remote_addr or session_info['agente_usuario'] != request.headers.get('Agente-Usuario'):
            sessoes_ativas.pop(token, None)
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'danger')
            return redirect(url_for('login'))

        if datetime.now(timezone.utc) - session_info['ultimo_ativo'] > session_TIMEOUT:
            sessoes_ativas.pop(token, None)
            session.clear()
            flash('Sessão expirada. Faça login novamente.', 'warning')
            return redirect(url_for('login'))

        session_info['ultimo_ativo'] = datetime.now(timezone.utc)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        usuarios_armazenados = usuarios.carregar_usuarios()

        if usuario in usuarios_armazenados and usuarios_armazenados[usuario] == senha:
            token = criar_token_session()
            session.clear()
            session['token'] = token
            session.permanent = False

            sessoes_ativas[token] = {
                'usuario': usuario,
                'ip': request.remote_addr,
                'agente_usuario': request.headers.get('Agente-Usuario'),
                'ultimo_ativo': datetime.now(timezone.utc)
            }
            return redirect(url_for('pagina_principal'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
            return redirect(url_for('login'))

    token = session.get('token')
    if token in sessoes_ativas:
        return redirect(url_for('pagina_principal'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    token = session.get('token')
    if token:
        sessoes_ativas.pop(token, None)
    session.clear()
    flash('Você saiu da sessão.', 'info')
    return redirect(url_for('login'))

@app.route('/pagina_principal')
@login_required
def pagina_principal():
    token = session.get('token')
    usuario = sessoes_ativas[token]['usuario']
    return render_template('pagina_principal.html', usuario=usuario)

@app.route("/cadastrar_aluno", methods=['GET', 'POST'])
@login_required
def cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        telefone = request.form.get('telefone')

        cpf_existente = Aluno.query.filter_by(cpf=cpf).first()
        if cpf_existente:
            flash("CPF já cadastrado para outro aluno.", "danger")
            return redirect(url_for('cadastrar_aluno'))

        try:
            novo_aluno = Aluno(
                nome=nome,
                cpf=cpf,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                telefone=telefone
            )

            db.session.add(novo_aluno)
            db.session.commit()

            valor_plano = 150.0
            Pagamento.registrar_pagamento(novo_aluno.id_aluno, valor_plano, "dinheiro")

            flash("Aluno cadastrado com sucesso!", "success")
            return redirect(url_for('ficha_aluno'))

        except Exception as erro:
            db.session.rollback()
            flash(f"Erro ao cadastrar aluno: {erro}", "danger")
            return redirect(url_for('cadastrar_aluno'))
    return render_template("cadastrar_aluno.html")


from sqlalchemy.sql import exists, and_
from datetime import date

@app.route('/ficha_aluno')
@login_required
def ficha_aluno():
    query = request.args.get('query', '').strip()
    status = request.args.get('status', '').strip()

    filtros = []
    if query:
        filtros.append(Aluno.nome.ilike(f'{query}%'))
    if status:
        filtros.append(Aluno.status == status)

    if filtros:
        alunos = Aluno.query.filter(*filtros).all()
    else:
        alunos = Aluno.query.all()

    return render_template('ficha_aluno.html', alunos=alunos, query=query, status=status)

@app.route('/aluno/<int:id_aluno>')
@login_required
def detalhes_aluno(id_aluno):
    aluno = Aluno.query.filter_by(id_aluno=id_aluno).first()

    if not aluno:
        return render_template('ficha_aluno.html', alunos=[], query='')

    return render_template('detalhes_aluno.html', aluno=aluno)

@app.route('/aluno/editar/<int:id_aluno>', methods=['GET', 'POST'])
@login_required
def editar_aluno(id_aluno):
    aluno = Aluno.query.get(id_aluno)
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('ficha_aluno'))

    if request.method == 'POST':
        try:
            aluno.nome = request.form['nome']
            aluno.cpf = request.form['cpf']
            aluno.endereco = request.form['endereco']
            aluno.cidade = request.form['cidade']
            aluno.estado = request.form['estado'].upper()
            aluno.telefone = request.form['telefone']
            aluno.data_matricula = datetime.strptime(request.form['data_matricula'], '%Y-%m-%d').date()
            aluno.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()

            status = request.form['status']
            aluno.status = status

            if status == 'Ativo':
                aluno.data_desligamento = None
            else:
                if aluno.data_desligamento is None:
                    aluno.data_desligamento = datetime.today().date()

            db.session.commit()
            flash('Dados do aluno atualizados com sucesso.', 'success')
            return redirect(url_for('ficha_aluno'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar aluno: {e}', 'danger')

    return render_template('editar_aluno.html', aluno=aluno)

@app.route('/financeiro')
def financeiro():
    return render_template('financeiro.html')


@app.route('/pagamento/novo', methods=['GET', 'POST'])
@login_required
def novo_pagamento():
    if request.method == 'POST':
        aluno = request.form['aluno_nome']
        data_ven = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        valor = float(request.form['valor'])
        status = request.form['status']

        novo = Pagamento(aluno_nome=aluno, data_vencimento=data_ven, valor=valor, status=status)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('financeiro'))

    return render_template('novo_pagamento.html')

@app.route('/pagamento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_pagamento(id):
    pagamento = Pagamento.query.get_or_404(id)

    if request.method == 'POST':
        pagamento.aluno_nome = request.form['aluno_nome']
        pagamento.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        pagamento.valor = float(request.form['valor'])
        pagamento.status = request.form['status']
        db.session.commit()
        return redirect(url_for('financeiro'))

    return render_template('editar_pagamento.html', pagamento=pagamento)

@app.route('/pagamento/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_pagamento(id):
    pagamento = Pagamento.query.get_or_404(id)
    db.session.delete(pagamento)
    db.session.commit()
    return redirect(url_for('financeiro'))

@app.route("/usuarios", methods=['GET', 'POST'])
@login_required
def gerenciar_usuarios():
    usuarios_armazenados = usuarios.carregar_usuarios()
    
    if request.method == 'POST':
        novo_usuario = request.form.get('usuario', '').strip().lower()
        nova_senha = request.form.get('senha', '').strip()

        if len(usuarios_armazenados) >= 3:
            flash('Limite de 3 usuários atingido.', 'warning')
        elif not novo_usuario or not nova_senha:
            flash('Usuário e senha são obrigatórios.', 'warning')
        elif len(novo_usuario) < 3:
            flash('O nome de usuário deve ter pelo menos 3 caracteres.', 'warning')
        elif len(nova_senha) < 5 or len(nova_senha) > 20:
            flash('A senha deve ter entre 5 e 20 caracteres.', 'warning')
        elif novo_usuario in usuarios_armazenados:
            flash('Usuário já existe.', 'danger')
        else:
            usuarios_armazenados[novo_usuario] = nova_senha
            usuarios.salvar_usuarios(usuarios_armazenados)
            flash(f'Usuário "{novo_usuario}" cadastrado com sucesso!', 'success')

        return redirect(url_for('gerenciar_usuarios'))

    return render_template("usuarios.html", usuarios=usuarios_armazenados)

@app.route("/usuarios/remover/<usuario>", methods=['POST'])
@login_required
def remover_usuario_route(usuario):
    usuarios_armazenados = usuarios.carregar_usuarios()
    usuario = usuario.lower()

    if usuario == 'admin':
        flash('O usuário "admin" não pode ser removido.', 'danger')
        return redirect(url_for('gerenciar_usuarios'))

    if usuario in usuarios_armazenados:
        usuarios_armazenados.pop(usuario)
        usuarios.salvar_usuarios(usuarios_armazenados)
        flash(f'Usuário {usuario} removido.', 'success')
    else:
        flash(f'Usuário {usuario} não encontrado.', 'danger')

    return redirect(url_for('gerenciar_usuarios'))
