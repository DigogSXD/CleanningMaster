import mysql.connector
from datetime import datetime, timedelta
import random
import string

# Função para gerar a chave de ativação
def gerar_chave(tipo_licenca):
    # Gerar chave aleatória
    chave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    # Calcular data de expiração
    if tipo_licenca in ['30_dias', '90_dias']:
        dias = 30 if tipo_licenca == '30_dias' else 90
        data_expiracao = datetime.now() + timedelta(days=dias)
    else:
        data_expiracao = None  # Licença vitalícia

    # Conexão com o banco de dados
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="cleannmaster"
    )

    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO chaves (chave, tipo_licenca, data_expiracao)
        VALUES (%s, %s, %s)
    """, (chave, tipo_licenca, data_expiracao))

    conn.commit()
    cursor.close()
    conn.close()

    return chave, data_expiracao

# Função para validar a chave de ativação
def validar_chave(chave):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="cleannmaster"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT tipo_licenca, data_expiracao, ativa FROM chaves WHERE chave = %s", (chave,))
    resultado = cursor.fetchone()

    if resultado:
        tipo_licenca, data_expiracao, ativa = resultado
        if not ativa:
            return "Chave desativada!"
        if tipo_licenca != 'vitalicia' and data_expiracao < datetime.now():
            return "Chave expirada!"
        return "Chave válida!"
    
    cursor.close()
    conn.close()
    return "Chave inválida!"
