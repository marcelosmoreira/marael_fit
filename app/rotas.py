import re
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import (
    abort, jsonify, render_template, request, redirect, 
    url_for, flash, session
)
from sqlalchemy import or_
from app import app, db, Pagamento
from app.model import usuarios
from app.model.aluno import Aluno

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

        if session_info['ip'] != request.remote_addr or session_info['agente_usuario'] != request.headers.get('User-Agent'):
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
                'agente_usuario': request.headers.get('User-Agent'),
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

@app.route('/verificar_cpf', methods=['POST'])
@login_required
def verificar_cpf():
    cpf = request.json.get('cpf', '')
    cpf = re.sub(r'\D', '', cpf)

    cpf_existente = Aluno.query.filter_by(cpf=cpf).first()
    if cpf_existente:
        return jsonify({'existe': True})

    return jsonify({'existe': False})

@app.route("/cadastrar_aluno", methods=['GET', 'POST'])
@login_required
def cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf', '')
        cpf = re.sub(r'\D', '', cpf)
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        telefone = request.form.get('telefone')
        data_matricula_str = request.form.get('dataMatricula')

        try:
            data_matricula = datetime.strptime(data_matricula_str, '%Y-%m-%d').date()
        except Exception:
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

            data_vencimento = data_matricula + timedelta(days=30)

            novo_pag = Pagamento.cadastrar_pagamento(
                id_aluno=novo_aluno.id_aluno,
                valor=100.00,
                data_vencimento=data_vencimento,
                forma_pagamento='Não definida'
            )
            db.session.add(novo_pag)
            db.session.commit()

            return redirect(url_for('ficha_aluno'))

        except Exception:
            db.session.rollback()
            return redirect(url_for('cadastrar_aluno'))

    return render_template("cadastrar_aluno.html")

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
        return redirect(url_for('ficha_aluno'))

    if request.method == 'POST':
        try:
            aluno.nome = request.form['nome']

            cpf = request.form['cpf']
            cpf = re.sub(r'\D', '', cpf)
            aluno.cpf = cpf

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
            return redirect(url_for('ficha_aluno'))
        except Exception:
            db.session.rollback()

    return render_template('editar_aluno.html', aluno=aluno)

@app.route('/financeiro')
@login_required
def financeiro():
    busca = request.args.get('busca', '').strip()
    filtro_status = request.args.get('status', 'todos')
    ordenar_por = request.args.get('ordenar_por', '')

    query = db.session.query(Pagamento, Aluno).join(Aluno, Pagamento.id_aluno == Aluno.id_aluno)

    if filtro_status != 'todos':
        query = query.filter(Pagamento.status_pagamento == filtro_status)

    if busca:
        busca_like = f'%{busca}%'
        query = query.filter(
            or_(
                Pagamento.id_pagamento.cast(db.String).ilike(busca_like),
                Aluno.nome.ilike(busca_like),
                Pagamento.id_aluno.cast(db.String).ilike(busca_like)
            )
        )

    if ordenar_por == 'id_asc':
        query = query.order_by(Pagamento.id_pagamento.asc())
    elif ordenar_por == 'id_desc':
        query = query.order_by(Pagamento.id_pagamento.desc())
    elif ordenar_por == 'data_asc':
        query = query.order_by(Pagamento.data_vencimento.asc())
    elif ordenar_por == 'data_desc':
        query = query.order_by(Pagamento.data_vencimento.desc())
    else:
        query = query.order_by(Pagamento.id_pagamento.desc())

    dados = query.all()
    dados_formatados = []
    for pagamento, aluno in dados:
        dados_formatados.append({
            'id_pagamento': pagamento.id_pagamento,
            'id_aluno': pagamento.id_aluno,
            'nome': aluno.nome,
            'valor': pagamento.valor,
            'data_pagamento': pagamento.data_pagamento,
            'data_vencimento': pagamento.data_vencimento,
            'forma_pagamento': pagamento.forma_pagamento,
            'status_pagamento': pagamento.status_pagamento,
        })

    return render_template('financeiro.html', dados=dados_formatados, busca=busca, filtro_status=filtro_status)

@app.route('/novo_pagamento', methods=['GET', 'POST'])
@login_required
def novo_pagamento():
    if request.method == 'POST':
        try:
            id_aluno_str = request.form.get('id_aluno')
            if not id_aluno_str:
                flash("Por favor, selecione um aluno.", "danger")
                return redirect(url_for('novo_pagamento'))

            id_aluno = int(id_aluno_str)
            valor = float(request.form['valor'])
            data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()

            aluno = Aluno.query.get(id_aluno)
            if not aluno:
                flash("Aluno não encontrado.", "danger")
                return redirect(url_for('novo_pagamento'))

            novo_pag = Pagamento(
                id_aluno=id_aluno,
                valor=valor,
                data_vencimento=data_vencimento,
                forma_pagamento='Não definida',
                data_pagamento=None
            )

            db.session.add(novo_pag)
            db.session.commit()

            flash('Pagamento criado com sucesso!', 'success')
            return redirect(url_for('financeiro'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar pagamento: {e}', 'danger')
            return redirect(url_for('novo_pagamento'))

    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template('novo_pagamento.html', alunos=alunos)

@app.route('/pagamento/editar/<int:id_pagamento>', methods=['GET', 'POST'])
@login_required
def editar_pagamento(id_pagamento):
    pagamento = Pagamento.query.get_or_404(id_pagamento)

    if request.method == 'POST':
        pagamento.valor = float(request.form['valor'])
        pagamento.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()

        forma_pagamento = request.form['forma_pagamento']
        pagamento.forma_pagamento = forma_pagamento.capitalize() if forma_pagamento.capitalize() in Pagamento.FORMAS_VALIDAS else 'Não definida'

        if pagamento.forma_pagamento != 'Não definida':
            pagamento.data_pagamento = datetime.strptime(request.form['data_pagamento'], '%Y-%m-%d').date()
        else:
            pagamento.data_pagamento = None

        pagamento.atualizar_status()
        db.session.commit()
        return redirect(url_for('financeiro'))
    
    nome_aluno = pagamento.aluno.nome if pagamento.aluno else 'Aluno não encontrado'
    return render_template('editar_pagamento.html', pagamento=pagamento, nome_aluno=nome_aluno)

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
