import uuid
from datetime import datetime, timedelta, timezone
from flask import render_template, request, redirect, url_for, flash, session
from app import app
from app.model import usuarios

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

@app.route("/cadastrar_aluno")
@login_required
def cadastrar_aluno():
    return render_template("cadastrar_aluno.html")

@app.route("/consulta_aluno")
@login_required
def consulta_aluno():
    return render_template("consulta_aluno.html")

@app.route("/painel_financeiro")
@login_required
def painel_financeiro():
    return render_template("painel_financeiro.html")

@app.route("/incluir_pagamento")
@login_required
def incluir_pagamento():
    return render_template("incluir_pagamento.html")

@app.route("/consultar_pagamento")
@login_required
def consultar_pagamento():
    return render_template("consultar_pagamento.html")

@app.route("/usuarios", methods=['GET', 'POST'])
@login_required
def gerenciar_usuarios():
    usuarios_armazenados = usuarios.carregar_usuarios()
    
    if request.method == 'POST':
        novo_usuario = request.form.get('usuario', '').strip().lower()
        nova_senha = request.form.get('senha', '').strip()

        # Validações
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
