import mysql.connector

def criar_banco_e_tabelas():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678"
    )

    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS cleannmaster")
    cursor.execute("USE cleannmaster")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha VARCHAR(100) NOT NULL
        )
    """)

    print("Banco de dados e tabela 'usuarios' criados com sucesso!")


    cursor.close()
    conn.close()

# Executa a criação quando rodar o arquivo
if __name__ == "__main__":
    criar_banco_e_tabelas()
