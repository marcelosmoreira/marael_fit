from app import app

def carregar_usuarios(caminho_arquivo='usuarios.txt'):
    usuarios = {}
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and ':' in linha:
                    usuario, senha = linha.split(':', 1)
                    usuarios[usuario.strip().lower()] = senha.strip()
    except FileNotFoundError:
        print(f"Aviso: arquivo {caminho_arquivo} não encontrado.")
    return usuarios

def salvar_usuarios(usuarios, caminho_arquivo='usuarios.txt'):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            for usuario, senha in usuarios.items():
                f.write(f"{usuario}:{senha}\n")
    except Exception as e:
        print(f"Erro ao salvar usuários: {e}")
