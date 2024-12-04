from flask import Flask, render_template, request, redirect, url_for, flash
import bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_secreta'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '8900',
    'database': 'senhas'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Usuário já cadastrado!", "error")
            return redirect(url_for('cadastro'))

        query = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(query, (nome, email, hashed_senha))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('login'))  

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT nome, senha FROM usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and bcrypt.checkpw(senha.encode('utf-8'), result[1].encode('utf-8')):
            nome = result[0]
            return redirect(url_for('entrada', nome=nome))  
        else:
            flash("Usuário ou senha incorretos!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/entrada')
def entrada():
    nome = request.args.get('nome')
    return render_template('entrada.html', nome=nome)

if __name__ == '__main__':
    app.run(debug=True)
