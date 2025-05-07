import mysql.connector
from mysql.connector import Error

def criar_banco_e_tabelas():
    try:
        # Conectar ao MySQL sem especificar um banco de dados inicialmente
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
                tipo_usuario ENUM('free', 'premium') DEFAULT 'free',
                permissao INT DEFAULT 0,
                data_expiracao DATE DEFAULT NULL
            )
        """)

        # Verificar e adicionar colunas faltantes na tabela 'usuarios'
        columns_to_check = [
            ("permissao", "ALTER TABLE usuarios ADD COLUMN permissao INT DEFAULT 0"),
            ("data_expiracao", "ALTER TABLE usuarios ADD COLUMN data_expiracao DATE DEFAULT NULL")
        ]
        for column, alter_query in columns_to_check:
            cursor.execute(f"SHOW COLUMNS FROM usuarios LIKE '{column}'")
            if cursor.fetchone() is None:
                cursor.execute(alter_query)
                print(f"Coluna '{column}' adicionada à tabela 'usuarios'.")
            else:
                print(f"A coluna '{column}' já existe na tabela 'usuarios'.")

        # Tabela de chaves
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS chaves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chave VARCHAR(20) NOT NULL UNIQUE,
                usada BOOLEAN DEFAULT FALSE,
                ativa BOOLEAN DEFAULT TRUE,
                tipo_licenca ENUM('30_dias', '90_dias', 'vitalicia') NOT NULL,
                data_uso DATETIME DEFAULT NULL,
                data_expiracao DATE DEFAULT NULL,
                usuario_id INT DEFAULT NULL,
                usada_por INT DEFAULT NULL,
                email_usuario VARCHAR(100) DEFAULT NULL,
                data_ativacao DATE DEFAULT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            )
        """)

        # Verificar e adicionar colunas faltantes na tabela 'chaves'
        columns_to_check = [
            ("data_ativacao", "ALTER TABLE chaves ADD COLUMN data_ativacao DATE DEFAULT NULL"),
            ("data_expiracao", "ALTER TABLE chaves ADD COLUMN data_expiracao DATE DEFAULT NULL"),
            ("usada_por", "ALTER TABLE chaves ADD COLUMN usada_por INT DEFAULT NULL"),
            ("email_usuario", "ALTER TABLE chaves ADD COLUMN email_usuario VARCHAR(100) DEFAULT NULL")
        ]
        for column, alter_query in columns_to_check:
            cursor.execute(f"SHOW COLUMNS FROM chaves LIKE '{column}'")
            if cursor.fetchone() is None:
                cursor.execute(alter_query)
                print(f"Coluna '{column}' adicionada à tabela 'chaves'.")
            else:
                print(f"A coluna '{column}' já existe na tabela 'chaves'.")

        # Tabela de mensagens de chat
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS chat_mensagens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chat_id VARCHAR(50) NOT NULL,
                usuario_id INT NOT NULL,
                mensagem TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Verificar e adicionar colunas faltantes na tabela 'chat_mensagens'
        columns_to_check = [
            ("is_admin", "ALTER TABLE chat_mensagens ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
        ]
        for column, alter_query in columns_to_check:
            cursor.execute(f"SHOW COLUMNS FROM chat_mensagens LIKE '{column}'")
            if cursor.fetchone() is None:
                cursor.execute(alter_query)
                print(f"Coluna '{column}' adicionada à tabela 'chat_mensagens'.")
            else:
                print(f"A coluna '{column}' já existe na tabela 'chat_mensagens'.")

        # Confirmar as alterações
        conn.commit()
        print("Banco de dados e tabelas criados com sucesso!")

    except Error as e:
        print(f"Erro ao criar banco de dados ou tabelas: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Conexão com o banco de dados fechada.")

# Executa a função
criar_banco_e_tabelas()