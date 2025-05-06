import os
import shutil
import psutil
import tkinter as tk
import mysql.connector
from tkinter import messagebox, simpledialog
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash



# Cores do tema azul escuro
bg_color = "#1e1e2f"
fg_color = "#ffffff"
button_bg = "#3a3a5c"
entry_bg = "#2a2a3d"

# Simulação de banco (substitua por MySQL depois)
usuarios = {"admin@email.com": "1234"}

# Funções do CleanningMaster
def limpar_temp():
    temp_dirs = [os.environ.get('TEMP'), os.environ.get('TMP')]
    erros = 0
    for temp in temp_dirs:
        if temp and os.path.exists(temp):
            for file in os.listdir(temp):
                file_path = os.path.join(temp, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception:
                    erros += 1
    if erros == 0:
        messagebox.showinfo("Sucesso", "Arquivos temporários limpos com sucesso!")
    else:
        messagebox.showwarning("Aviso", f"Alguns arquivos não puderam ser removidos ({erros} falhas).")

def listar_processos():
    processos = "\n".join([f"{proc.info['pid']} - {proc.info['name']}" for proc in psutil.process_iter(['pid', 'name'])])
    janela_listagem = tk.Toplevel()
    janela_listagem.title("Processos em Execução")
    janela_listagem.configure(bg=bg_color)
    text_box = tk.Text(janela_listagem, height=25, width=60, bg=entry_bg, fg=fg_color)
    text_box.pack()
    text_box.insert(tk.END, processos)

def encerrar_processo():
    nome = simpledialog.askstring("Encerrar processo", "Digite o nome do processo (ex: chrome.exe):")
    if not nome:
        return
    encerrados = 0
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == nome:
            try:
                proc.kill()
                encerrados += 1
            except Exception as e:
                print(f"Erro: {e}")
    if encerrados > 0:
        messagebox.showinfo("Encerrado", f"{encerrados} processo(s) {nome} encerrado(s).")
    else:
        messagebox.showwarning("Não encontrado", f"Nenhum processo com o nome '{nome}' foi encerrado.")

def agendar_desligamento():
    minutos = simpledialog.askinteger("Agendar Desligamento", "Digite em quantos minutos deseja desligar o PC:")
    if minutos is not None and minutos > 0:
        segundos = minutos * 60
        os.system(f"shutdown /s /t {segundos}")
        messagebox.showinfo("Agendado", f"Desligamento agendado para {minutos} minuto(s).")

def cancelar_desligamento():
    os.system("shutdown /a")
    messagebox.showinfo("Cancelado", "Desligamento agendado foi cancelado.")


# Tela principal CleanningMaster
def abrir_cleanning_master():
    root = tk.Tk()
    root.title("CleanningMaster")
    root.geometry("600x400")
    root.configure(bg=bg_color)

    tk.Label(root, text="CleanningMaster", font=("Arial", 16), bg=bg_color, fg=fg_color).pack(pady=10)

    tk.Button(root, text="🧹 Limpar Arquivos Temporários", command=limpar_temp, width=30, bg=button_bg, fg=fg_color).pack(pady=5)
    tk.Button(root, text="📋 Listar Processos", command=listar_processos, width=30, bg=button_bg, fg=fg_color).pack(pady=5)
    tk.Button(root, text="⛔ Encerrar Processo por Nome", command=encerrar_processo, width=30, bg=button_bg, fg=fg_color).pack(pady=5)
    tk.Button(root, text="⏲️ Agendar Desligamento", command=agendar_desligamento, width=30, bg=button_bg, fg=fg_color).pack(pady=5)
    tk.Button(root, text="❌ Cancelar Desligamento", command=cancelar_desligamento, width=30, bg=button_bg, fg=fg_color).pack(pady=5)


    tk.Label(root, text="Desenvolvido em Python", font=("Arial", 10), bg=bg_color, fg=fg_color).pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

# Tela de login
def abrir_login():
    global login_window, email_entry, senha_entry

    font_title = ("Arial", 20, "bold")
    font_label = ("Arial", 14)
    font_entry = ("Arial", 14)
    font_button = ("Arial", 14)

    login_window = tk.Tk()
    login_window.title("Login - CleanningMaster")
    login_window.geometry("500x400")  # Janela maior
    login_window.configure(bg=bg_color)

    tk.Label(login_window, text="Login", font=font_title, bg=bg_color, fg=fg_color).pack(pady=20)

    tk.Label(login_window, text="Email:", font=font_label, bg=bg_color, fg=fg_color).pack()
    email_entry = tk.Entry(login_window, font=font_entry, bg=entry_bg, fg=fg_color, width=30)
    email_entry.pack(pady=5)

    tk.Label(login_window, text="Senha:", font=font_label, bg=bg_color, fg=fg_color).pack()
    senha_entry = tk.Entry(login_window, show="*", font=font_entry, bg=entry_bg, fg=fg_color, width=30)
    senha_entry.pack(pady=5)

    tk.Button(login_window, text="Entrar", command=fazer_login, font=font_button,
              bg=button_bg, fg=fg_color, width=25, height=2).pack(pady=15)

    tk.Button(login_window, text="Registrar", command=abrir_registro, font=font_button,
              bg=button_bg, fg=fg_color, width=25, height=2).pack()

    login_window.mainloop()


def fazer_login():
    email = email_entry.get()
    senha = senha_entry.get()

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="cleannmaster"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (email,))
        resultado = cursor.fetchone()

        if resultado:
            senha_hash = resultado[0]
            if check_password_hash(senha_hash, senha):
                login_window.destroy()
                abrir_cleanning_master()
            else:
                messagebox.showerror("Erro de login", "Email ou senha incorretos.")
        else:
            messagebox.showerror("Erro de login", "Email ou senha incorretos.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        messagebox.showerror("Erro de conexão", f"Ocorreu um erro ao conectar com o banco de dados:\n{e}")


# Tela de registro
def abrir_registro():
    login_window.destroy()

    registro_window = tk.Tk()
    registro_window.title("Registro")
    registro_window.geometry("400x400")
    registro_window.configure(bg=bg_color)

    font_title = ("Arial", 20)
    font_label = ("Arial", 14)
    font_entry = ("Arial", 14)
    font_button = ("Arial", 14)

    tk.Label(registro_window, text="Registro", font=font_title, bg=bg_color, fg=fg_color).pack(pady=10)

    # Campo Nome
    tk.Label(registro_window, text="Nome:", bg=bg_color, fg=fg_color, font=font_label).pack()
    nome_entry = tk.Entry(registro_window, bg=entry_bg, fg=fg_color, width=30, font=font_entry)
    nome_entry.pack(pady=2)

    # Campo Email
    tk.Label(registro_window, text="Email:", bg=bg_color, fg=fg_color, font=font_label).pack()
    novo_email_entry = tk.Entry(registro_window, bg=entry_bg, fg=fg_color, width=30, font=font_entry)
    novo_email_entry.pack(pady=2)

    # Campo Senha
    tk.Label(registro_window, text="Senha:", bg=bg_color, fg=fg_color, font=font_label).pack()
    nova_senha_entry = tk.Entry(registro_window, show="*", bg=entry_bg, fg=fg_color, width=30, font=font_entry)
    nova_senha_entry.pack(pady=2)

    def registrar():
        nome = nome_entry.get()
        email = novo_email_entry.get()
        senha = nova_senha_entry.get()

        if not nome or not email or not senha:
            messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
            return

        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha_hash))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", "Usuário registrado com sucesso.")
            registro_window.destroy()
            abrir_login()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Email já está registrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")



    def voltar_login():
        registro_window.destroy()
        abrir_login()

    tk.Button(registro_window, text="Registrar", command=registrar, bg=button_bg, fg=fg_color,
              width=25, height=2, font=font_button).pack(pady=5)
    tk.Button(registro_window, text="Voltar para Login", command=voltar_login, bg=button_bg, fg=fg_color,
              width=25, height=2, font=font_button).pack(pady=5)

    registro_window.mainloop()


# Iniciar o app com a tela de login
abrir_login()
