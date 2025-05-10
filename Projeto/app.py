import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_session import Session
from criar_banco import criar_banco_e_tabelas
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

# Configurações do MySQL aa
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'cleannmaster'
mysql = MySQL(app)

# Sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
Session(app)

def usuario_logado():
    return 'usuario_nome' in session

@app.context_processor
def inject_user():
    return dict(usuario_nome=session.get('usuario_nome'), usuario_id=session.get('usuario_id'))

# Gera chave estilo XXXX-XXXX-XXXX
def gerar_chave():
    return '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))

@app.route('/gerar-chave')
def gerar_chave_endpoint():
    chave = gerar_chave()
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO chaves (chave) VALUES (%s)", (chave,))
    mysql.connection.commit()
    cursor.close()
    return f"Chave gerada e salva no banco: {chave}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        senha = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s OR nome = %s", (identifier, identifier))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario and check_password_hash(usuario[3], senha):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['usuario_email'] = usuario[2]
            flash("Login bem-sucedido!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Nome, email ou senha incorretos!", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        senha = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Este e-mail já está cadastrado.", "danger")
            cursor.close()
            return redirect(url_for('register'))
        senha_hash = generate_password_hash(senha)
        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)", (nome, email, senha_hash, 'free'))
        mysql.connection.commit()
        cursor.close()
        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if not usuario_logado():
        flash("Você precisa estar logado!", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logout feito com sucesso.", "info")
    return redirect(url_for('login'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/cleanmasters')
def free_version():
    if not usuario_logado():
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for('login'))
    return render_template('free_version.html')

@app.route('/download')
def paid_version():
    return render_template('paid_version.html')

@app.route('/compra')
def pagina_de_compra():
    return render_template('compra.html')

@app.route('/ativar-key', methods=['GET', 'POST'])
def ativar_key():
    if request.method == 'POST':
        chave = request.form['key'].strip().upper()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, chave, ativa, usada_por, tipo_licenca, data_expiracao FROM chaves WHERE chave = %s", (chave,))
        dados_chave = cursor.fetchone()

        if not dados_chave:
            flash("Chave inválida.", "danger")
        elif not dados_chave[2]:
            flash("Esta chave já foi usada.", "warning")
        elif dados_chave[3] is not None:
            flash("Esta chave já foi ativada por outro usuário.", "warning")
        elif not usuario_logado():
            flash("Você precisa estar logado para ativar uma chave.", "warning")
        else:
            tipo_licenca = dados_chave[4]
            data_expiracao = dados_chave[5]
            ultimos_digitos = dados_chave[1][-4:]
            data_expiracao_formatada = data_expiracao.strftime('%d/%m/%Y') if data_expiracao else "Sem data de expiração"

            cursor.execute("""UPDATE chaves SET usada = TRUE, ativa = FALSE, usada_por = %s, email_usuario = %s, data_ativacao = NOW() WHERE id = %s""", (session['usuario_id'], session['usuario_nome'], dados_chave[0]))
            mysql.connection.commit()

            cursor.execute("UPDATE usuarios SET tipo_usuario = 'premium' WHERE id = %s", (session['usuario_id'],))
            mysql.connection.commit()

            flash(f"Chave ativada com sucesso! Últimos 4 dígitos: {ultimos_digitos}. Licença: {tipo_licenca}. Expiração: {data_expiracao_formatada}.", "success")
        cursor.close()
    return render_template('ativar_key.html')

@app.route('/licencas-ativas')
def licencas_ativas():
    if not usuario_logado():
        flash("Você precisa estar logado para acessar as licenças.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT chave, tipo_licenca, data_expiracao FROM chaves WHERE usada_por = %s AND usada = TRUE""", (session['usuario_id'],))
    licencas = cursor.fetchall()
    cursor.close()

    licencas_info = []
    for licenca in licencas:
        chave, tipo_licenca, data_expiracao = licenca
        if data_expiracao:
            tempo_restante = data_expiracao - datetime.now()
            tempo_restante_str = str(tempo_restante).split('.')[0]
        else:
            tempo_restante_str = "Sem expiração"

        licencas_info.append({
            'chave': chave,
            'tipo_licenca': tipo_licenca,
            'tempo_restante': tempo_restante_str
        })

    return render_template('licencas_ativas.html', licencas_info=licencas_info)

@app.route('/usuario')
def usuario():
    if not usuario_logado():
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nome, email, tipo_usuario FROM usuarios WHERE id = %s", (session['usuario_id'],))
    usuario_info = cursor.fetchone()

    if not usuario_info:
        flash("Usuário não encontrado.", "danger")
        cursor.close()
        return redirect(url_for('home'))

    nome, email, tipo_usuario = usuario_info
    cursor.execute("""SELECT chave, tipo_licenca, data_expiracao, data_ativacao FROM chaves WHERE usada_por = %s AND usada = TRUE""", (session['usuario_id'],))

    licencas = cursor.fetchall()
    licencas_vinculadas = []
    for licenca in licencas:
        chave, tipo_licenca, data_expiracao, data_ativacao = licenca
        if data_expiracao:
            duracao = (data_expiracao - datetime.now()).days
        else:
            duracao = "Sem expiração"

        licencas_vinculadas.append({
            'chave': chave,
            'tipo_licenca': tipo_licenca,
            'data_ativacao': data_ativacao,
            'duracao': duracao
        })

    # Verificação e atualização do tipo de usuário para 'premium'
    if tipo_usuario != 'premium' and licencas_vinculadas:
        cursor.execute("UPDATE usuarios SET tipo_usuario = 'premium' WHERE id = %s", (session['usuario_id'],))
        mysql.connection.commit()

    cursor.close()

    return render_template('informacoes_usuario.html', nome=nome, email=email, tipo_usuario=tipo_usuario, licencas_vinculadas=licencas_vinculadas)

@app.route('/atualizar_usuario', methods=['POST'])
def atualizar_usuario():
    if not usuario_logado():
        flash("Você precisa estar logado para atualizar suas informações.", "warning")
        return redirect(url_for('login'))

    nome = request.form.get('nome')
    senha = request.form.get('senha')
    usuario_id = session['usuario_id']

    # Validações
    if not nome and not senha:
        flash("Pelo menos um campo (nome ou senha) deve ser preenchido.", "warning")
        return redirect(url_for('usuario'))

    try:
        cursor = mysql.connection.cursor()

        # Verifica se o novo nome já existe (se fornecido)
        if nome:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nome = %s AND id != %s", (nome, usuario_id))
            nome_existe = cursor.fetchone()[0]
            if nome_existe > 0:
                flash("Nome de usuário já cadastrado. Escolha outro nome.", "danger")
                cursor.close()
                return redirect(url_for('usuario'))

        # Monta a query de atualização dinamicamente
        query = "UPDATE usuarios SET "
        params = []
        if nome:
            query += "nome = %s"
            params.append(nome)
        if senha:
            if len(senha) < 6:
                flash("A senha deve ter pelo menos 6 caracteres.", "warning")
                cursor.close()
                return redirect(url_for('usuario'))
            senha_hash = generate_password_hash(senha)
            if nome:
                query += ", "
            query += "senha = %s"
            params.append(senha_hash)
        query += " WHERE id = %s"
        params.append(usuario_id)

        cursor.execute(query, params)
        mysql.connection.commit()

        # Atualiza o nome na sessão, se alterado
        if nome:
            session['usuario_nome'] = nome

        flash("Informações atualizadas com sucesso!", "success")
        cursor.close()
    except Exception as e:
        flash(f"Erro ao atualizar informações: {e}", "danger")

    return redirect(url_for('usuario'))

@app.route('/remover-licenca/<int:licenca_id>') 
def remover_licenca(licenca_id):
    if not usuario_logado():
        flash("Você precisa estar logado para acessar esta página.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tipo_usuario FROM usuarios WHERE id = %s", (session['usuario_id'],))
    tipo_usuario_atual = cursor.fetchone()[0]

    cursor.execute("""UPDATE chaves SET usada = FALSE, ativa = TRUE, usada_por = NULL, email_usuario = NULL, data_ativacao = NULL WHERE id = %s""", (licenca_id,))
    mysql.connection.commit()

    cursor.execute("""SELECT COUNT(*) FROM chaves WHERE usada_por = %s AND tipo_licenca = 'premium'""", (session['usuario_id'],))
    licencas_premium = cursor.fetchone()[0]

    if licencas_premium == 0 and tipo_usuario_atual == 'premium':
        cursor.execute("UPDATE usuarios SET tipo_usuario = 'free' WHERE id = %s", (session['usuario_id'],))
        mysql.connection.commit()

    cursor.close()
    flash("Licença removida com sucesso!", "info")
    return redirect(url_for('usuario'))

@app.route('/admin-panel')
def admin_panel():
    if not usuario_logado():
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT permissao FROM usuarios WHERE id = %s", (session['usuario_id'],))
    permissao = cursor.fetchone()

    if not permissao or permissao[0] != 1:
        flash("Acesso negado. Você não é administrador.", "danger")
        cursor.close()
        return redirect(url_for('dashboard'))

    # Busca todos os usuários
    cursor.execute("SELECT id, nome, email, tipo_usuario, permissao FROM usuarios")
    usuarios = cursor.fetchall()

    # Busca todas as licenças
    cursor.execute("""SELECT chave, tipo_licenca, usada, usada_por, data_expiracao, data_ativacao FROM chaves""")
    licencas = cursor.fetchall()

    cursor.close()

    return render_template('admin_panel.html', usuarios=usuarios, licencas=licencas)

@app.route('/tipo-usuario')
def tipo_usuario():
    if not usuario_logado():
        flash("Você precisa estar logado para acessar esta página.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tipo_usuario FROM usuarios WHERE id = %s", (session['usuario_id'],))
    tipo_usuario = cursor.fetchone()
    cursor.close()

    return render_template('tipo_usuario.html', tipo_usuario=tipo_usuario[0])

@app.route('/panel')
def panel():
    if not usuario_logado():
        flash("Você precisa estar logado para acessar o painel.", "warning")
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/tornar-admin/<email>')
def tornar_admin(email):
    if not usuario_logado():
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE usuarios SET permissao = 1 WHERE email = %s", (email,))
    mysql.connection.commit()
    cursor.close()

    flash(f"O usuário {email} agora é administrador.", "success")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    criar_banco_e_tabelas()
    app.run(debug=True)