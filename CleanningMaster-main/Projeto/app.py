from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from criar_banco import criar_banco_e_tabelas
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import flash, redirect

app = Flask(__name__)

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'cleannmaster'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario and check_password_hash(usuario[3], senha): 
            flash("Login bem-sucedido!", "success")
            return redirect(url_for('home')) 
        else:
            flash("Email ou senha incorretos!", "danger")
            return render_template('login.html')

    return render_template('login.html')



# Exemplo na rota de cadastro:
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        senha = request.form['password']
        
        # Gera a hash da senha usando o método pbkdf2:sha256
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha_hash))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')

# Rotas adicionais para a navegação da navbar
@app.route('/usodomestico')
def uso_domestico():
    return render_template('UsoDomestico.html')

@app.route('/usocomercial')
def uso_comercial():
    return render_template('UsoComercial.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')  # <- Certifique-se que este arquivo está na pasta "templates"

if __name__ == '__main__':
    criar_banco_e_tabelas()
    app.run(debug=True)
