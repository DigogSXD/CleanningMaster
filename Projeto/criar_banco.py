import mysql.connector

def criar_banco_e_tabelas():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678"
    )

    cursor = conn.cursor()

    # Criação do banco de dados
    cursor.execute("CREATE DATABASE IF NOT EXISTS cleannmaster")
    cursor.execute("USE cleannmaster")

    # Tabela de usuários
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha VARCHAR(255) NOT NULL,
            tipo_usuario ENUM('free', 'premium') DEFAULT 'free'
        )
    """)

    # Verifica se a coluna 'permissao' existe, se não, adiciona
    cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'permissao'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao INT DEFAULT 0")
        print("Coluna 'permissao' adicionada à tabela 'usuarios'.")
    else:
        print("A coluna 'permissao' já existe na tabela 'usuarios'.")

    # Tabela de chaves
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS chaves (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chave VARCHAR(20) NOT NULL UNIQUE,
            usada BOOLEAN DEFAULT FALSE,
            ativa BOOLEAN DEFAULT TRUE,
            tipo_licenca ENUM('30_dias', '90_dias', 'vitalicia') NOT NULL,
            data_uso DATETIME,
            data_expiracao DATETIME,
            usuario_id INT,
            usada_por INT,
            email_usuario VARCHAR(100),
            data_ativacao DATETIME,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Verificar se a coluna 'data_ativacao' existe
    cursor.execute(""" 
        SHOW COLUMNS FROM chaves LIKE 'data_ativacao';
    """)
    result = cursor.fetchone()

    if result is None:
        cursor.execute(""" 
            ALTER TABLE chaves ADD COLUMN data_ativacao DATETIME;
        """)
        print("Coluna 'data_ativacao' adicionada à tabela 'chaves'.")
    else:
        print("A coluna 'data_ativacao' já existe na tabela 'chaves'.")

    print("Banco de dados, tabela 'usuarios' e tabela 'chaves' criados com sucesso!")

    cursor.close()
    conn.close()

# Executa a função
criar_banco_e_tabelas()
