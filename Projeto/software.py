import customtkinter as ctk
import psutil
import os
import shutil
import mysql.connector
from tkinter import messagebox
from werkzeug.security import generate_password_hash, check_password_hash
import time
import threading
import math
import uuid
from datetime import datetime, date, timedelta
from criar_banco import criar_banco_e_tabelas
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def verificar_licenca(usuario_id):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="cleannmaster"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT chave, tipo_licenca, data_ativacao, data_expiracao 
            FROM chaves
            WHERE usuario_id = %s AND ativa = TRUE AND data_expiracao >= CURDATE()
            ORDER BY data_expiracao DESC
            LIMIT 1
        """, (usuario_id,))
        licenca = cursor.fetchone()
        cursor.close()
        conn.close()
        return licenca
    except Exception as e:
        print(f"Erro ao verificar licença: {e}")
        return None

def ease_in_out(t):
    return 0.5 * (1 - math.cos(math.pi * t))

def animate_slide_with_fade(widget, start_pos, end_pos, axis='x', duration=500, delay=0, layout_manager='pack', layout_args=None):
    if layout_args is None:
        layout_args = {}

    if axis == 'x':
        widget.place(x=start_pos, rely=0.5, anchor='center')
    else:
        widget.place(relx=0.5, y=start_pos, anchor='center')

    opacity_supported = True
    try:
        widget.configure(alpha=0.0)
    except:
        opacity_supported = False

    frames = duration // 10
    step = (end_pos - start_pos) / frames if frames > 0 else (end_pos - start_pos)

    def animate(current_frame=0):
        if current_frame >= frames:
            if layout_manager == 'pack':
                widget.pack(**layout_args)
            elif layout_manager == 'grid':
                widget.grid(**layout_args)
            elif layout_manager == 'place':
                widget.place(**layout_args)
            if opacity_supported:
                widget.configure(alpha=1.0)
            return

        progress = ease_in_out(current_frame / frames)
        new_pos = start_pos + (end_pos - start_pos) * progress
        alpha = progress if opacity_supported else 1.0

        if axis == 'x':
            widget.place(x=new_pos, rely=0.5, anchor='center')
        else:
            widget.place(relx=0.5, y=new_pos, anchor='center')
        if opacity_supported:
            widget.configure(alpha=alpha)

        widget.after(10, lambda: animate(current_frame + 1))

    widget.after(delay, animate)

def interface_agendamentos(frame):
    countdown_thread = None
    is_running = False
    progress_frame = None
    progress_bar = None
    progress_label = None

    acao_var = ctk.StringVar(value="Encerrar")
    tempo_entry = ctk.CTkEntry(frame, placeholder_text="Digite o tempo em minutos", width=200, corner_radius=8)
    cancel_var = ctk.IntVar()

    def agendar_acao():
        nonlocal countdown_thread, is_running, progress_frame, progress_bar, progress_label
        acao = acao_var.get()
        try:
            minutos = float(tempo_entry.get())
            if minutos <= 0:
                messagebox.showwarning("Aviso", "Por favor, insira um tempo maior que 0 minutos.")
                return
        except ValueError:
            messagebox.showwarning("Aviso", "Por favor, insira um valor numérico válido para o tempo.")
            return

        segundos = int(minutos * 60)
        acao_str = {"Encerrar": "Encerramento", "Hibernar": "Hibernação", "Reiniciar": "Reinicialização"}[acao]

        progress_frame = ctk.CTkFrame(frame, corner_radius=10)
        progress_frame.pack(fill="x", pady=10, padx=20)
        
        progress_label = ctk.CTkLabel(progress_frame, text=f"Agendando {acao_str.lower()} em {minutos} minutos...", font=("Arial", 14))
        progress_label.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill="x", padx=10)
        progress_bar.set(0)

        is_running = True
        cancel_var.set(0)

        def executar_contagem():
            nonlocal is_running
            start_time = time.time()
            total_time = segundos

            while is_running:
                elapsed_time = time.time() - start_time
                progress = elapsed_time / total_time
                if progress >= 1:
                    progress = 1
                    progress_bar.set(1)
                    progress_label.configure(text=f"{acao_str} concluído!")
                    
                    try:
                        if acao == "Encerrar":
                            os.system(f"shutdown /s /t 1")
                        elif acao == "Hibernar":
                            os.system("shutdown /h")
                        elif acao == "Reiniciar":
                            os.system(f"shutdown /r /t 1")
                    except Exception as e:
                        messagebox.showerror("Erro", f"Falha ao executar {acao_str.lower()}: {e}")
                        return

                    messagebox.showinfo("Sucesso", f"Processo {acao_str.lower()} concluído com o tempo de {minutos} minutos.")
                    break

                progress_bar.set(progress)
                progress_label.configure(text=f"{acao_str} em {int((total_time - elapsed_time))} segundos...")
                frame.update()
                time.sleep(0.1)

            if not is_running and progress < 1:
                progress_label.configure(text="Agendamento cancelado.")
                progress_bar.set(0)

        countdown_thread = threading.Thread(target=executar_contagem, daemon=True)
        countdown_thread.start()

    def cancelar_acao():
        nonlocal is_running, countdown_thread, progress_frame, progress_bar, progress_label
        if not is_running:
            messagebox.showinfo("Info", "Nenhum agendamento ativo para cancelar.")
            return

        if not cancel_var.get():
            messagebox.showwarning("Aviso", "Por favor, marque a caixa de seleção para confirmar o cancelamento.")
            return

        is_running = False
        if countdown_thread:
            countdown_thread.join()

        try:
            os.system("shutdown /a")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cancelar agendamento: {e}")
            return

        messagebox.showinfo("Sucesso", "Agendamento cancelado com sucesso.")
        cancel_var.set(0)

    titulo = ctk.CTkLabel(frame, text="⏰ Agendamentos", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    acao_label = ctk.CTkLabel(frame, text="Selecione a ação:", font=("Arial", 14))
    animate_slide_with_fade(acao_label, -300, 0, axis='x', delay=150, layout_args={'pady': 5})

    acao_menu = ctk.CTkOptionMenu(frame, values=["Encerrar", "Hibernar", "Reiniciar"], variable=acao_var, width=200, corner_radius=8)
    animate_slide_with_fade(acao_menu, -300, 0, axis='x', delay=200, layout_args={'pady': 10})

    tempo_label = ctk.CTkLabel(frame, text="Tempo (minutos):", font=("Arial", 14))
    animate_slide_with_fade(tempo_label, -300, 0, axis='x', delay=250, layout_args={'pady': 5})

    animate_slide_with_fade(tempo_entry, -300, 0, axis='x', delay=300, layout_args={'pady': 10})

    btn_agendar = ctk.CTkButton(frame, text="Agendar ⏳", command=agendar_acao, width=200, corner_radius=8, font=("Arial", 14))
    animate_slide_with_fade(btn_agendar, -300, 0, axis='x', delay=350, layout_args={'pady': 10})

    cancel_checkbox = ctk.CTkCheckBox(frame, text="Confirmar cancelamento", variable=cancel_var, font=("Arial", 14))
    animate_slide_with_fade(cancel_checkbox, -300, 0, axis='x', delay=400, layout_args={'pady': 5})

    btn_cancelar = ctk.CTkButton(frame, text="Cancelar 🚫", command=cancelar_acao, width=200, corner_radius=8, font=("Arial", 14))
    animate_slide_with_fade(btn_cancelar, -300, 0, axis='x', delay=450, layout_args={'pady': 10})

    def on_enter(e):
        e.widget.configure(fg_color="#1f6aa5")
    
    def on_leave(e):
        e.widget.configure(fg_color="#14375e")

    btn_agendar.bind("<Enter>", on_enter)
    btn_agendar.bind("<Leave>", on_leave)
    btn_cancelar.bind("<Enter>", on_enter)
    btn_cancelar.bind("<Leave>", on_leave)

def interface_limpar_temp(frame):
    def limpar_temp():
        temp_dirs = [os.environ.get('TEMP'), os.environ.get('TMP')]
        erros = 0
        
        progress_frame = ctk.CTkFrame(frame, corner_radius=10)
        progress_frame.pack(fill="x", pady=10, padx=20)
        
        progress_label = ctk.CTkLabel(progress_frame, text="Limpando arquivos temporários...", font=("Arial", 14))
        progress_label.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill="x", padx=10)
        progress_bar.set(0)
        
        def animar_progresso():
            progress = 0
            while progress < 1:
                progress += 0.01
                progress_bar.set(progress)
                progress_label.configure(text=f"Limpando... {int(progress*100)}%")
                frame.update()
                time.sleep(0.03)
            
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
            
            progress_bar.set(1)
            progress_label.configure(text="Limpeza concluída!")
            
            if erros == 0:
                messagebox.showinfo("Sucesso", "Arquivos temporários limpos com sucesso!")
            else:
                messagebox.showwarning("Aviso", f"{erros} arquivos não puderam ser excluídos.")
        
        threading.Thread(target=animar_progresso, daemon=True).start()

    titulo = ctk.CTkLabel(frame, text="🧹 Limpeza de Arquivos Temporários", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    btn_limpar = ctk.CTkButton(frame, text="Limpar Agora 🔥", command=limpar_temp, width=200, corner_radius=8, font=("Arial", 14))
    animate_slide_with_fade(btn_limpar, -300, 0, axis='x', delay=150, layout_args={'pady': 20})

    def on_enter(e):
        e.widget.configure(fg_color="#1f6aa5")
    
    def on_leave(e):
        e.widget.configure(fg_color="#14375e")

    btn_limpar.bind("<Enter>", on_enter)
    btn_limpar.bind("<Leave>", on_leave)

def interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio):
    sort_column = "name"
    sort_reverse = False

    def fetch_processes():
        batch = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'cpu_times', 'status']):
            try:
                proc_info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'cpu_times', 'status'])
                proc_info['cpu_percent'] = proc.cpu_percent(interval=0.5)
                proc_info['memory_mb'] = proc_info['memory_info'].rss / 1024 / 1024
                proc_info['cpu_time'] = proc_info['cpu_times'].user + proc_info['cpu_times'].system
                batch.append(proc_info)
                if len(batch) >= 15:
                    yield batch
                    batch = []
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        if batch:
            yield batch

    def atualizar_lista_processos(scroll_frame):
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="#14375e", corner_radius=8)
        header_frame.pack(fill="x", pady=5, padx=5)
        
        headers = [
            ("Nome", "name", 0, 0.35),
            ("PID", None, 1, 0.1),
            ("CPU (%)", "cpu_percent", 2, 0.1),
            ("Memória (MB)", "memory_mb", 3, 0.15),
            ("CPU Time (s)", None, 4, 0.15),
            ("Status", None, 5, 0.1),
            ("Usuário", None, 6, 0.15),
            ("", None, 7, 0.1)
        ]
        for text, col_key, col, relwidth in headers:
            label = ctk.CTkLabel(header_frame, text=text, font=("Arial", 14, "bold"))
            label.grid(row=0, column=col, padx=2, pady=5, sticky="w")
            label.grid_columnconfigure(col, weight=1, uniform="header")
            header_frame.grid_columnconfigure(col, weight=int(relwidth * 100), uniform="header")
            if col_key:
                label.configure(cursor="hand2")
                label.bind("<Button-1>", lambda e, key=col_key: sort_by_column(key))
        
        all_processos = []
        
        def load_batch(processos, start_index):
            nonlocal all_processos
            all_processos.extend(processos)
            
            if sort_column == "name":
                all_processos.sort(key=lambda x: x['name'].lower(), reverse=sort_reverse)
            elif sort_column == "cpu_percent":
                all_processos.sort(key=lambda x: x['cpu_percent'], reverse=not sort_reverse)
            elif sort_column == "memory_mb":
                all_processos.sort(key=lambda x: x['memory_mb'], reverse=not sort_reverse)
            
            for widget in scroll_frame.winfo_children():
                if widget != header_frame:
                    widget.destroy()
            
            if not all_processos:
                ctk.CTkLabel(scroll_frame, text="Nenhum processo encontrado.", font=("Arial", 14)).pack(pady=20)
                return
            
            for i, proc in enumerate(all_processos):
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b", corner_radius=8)
                
                name_label = ctk.CTkLabel(row_frame, text=proc['name'], font=("Arial", 12), anchor="w")
                name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(0, weight=35, uniform="row")
                
                pid_label = ctk.CTkLabel(row_frame, text=str(proc['pid']), font=("Arial", 12), anchor="w")
                pid_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(1, weight=10, uniform="row")
                
                cpu_label = ctk.CTkLabel(row_frame, text=f"{proc['cpu_percent']:.1f}", font=("Arial", 12), anchor="w")
                cpu_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(2, weight=10, uniform="row")
                
                mem_label = ctk.CTkLabel(row_frame, text=f"{proc['memory_mb']:.1f}", font=("Arial", 12), anchor="w")
                mem_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(3, weight=15, uniform="row")
                
                cpu_time_label = ctk.CTkLabel(row_frame, text=f"{proc['cpu_time']:.1f}", font=("Arial", 12), anchor="w")
                cpu_time_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(4, weight=15, uniform="row")
                
                status_label = ctk.CTkLabel(row_frame, text=proc['status'], font=("Arial", 12), anchor="w")
                status_label.grid(row=0, column=5, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(5, weight=10, uniform="row")
                
                user_label = ctk.CTkLabel(row_frame, text=proc['username'] or "N/A", font=("Arial", 12), anchor="w")
                user_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(6, weight=15, uniform="row")
                
                details_btn = ctk.CTkButton(row_frame, text="Detalhes", width=80, corner_radius=8, font=("Arial", 12),
                                          command=lambda p=proc: mostrar_detalhes(p))
                details_btn.grid(row=0, column=7, padx=5, pady=5)
                details_btn.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
                details_btn.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
                row_frame.grid_columnconfigure(7, weight=10, uniform="row")
                
                def on_row_enter(e):
                    row_frame.configure(fg_color="#1f6aa5")
                
                def on_row_leave(e):
                    row_frame.configure(fg_color="#2b2b2b")
                
                row_frame.bind("<Enter>", on_row_enter)
                row_frame.bind("<Leave>", on_row_leave)
                for child in row_frame.winfo_children():
                    child.bind("<Enter>", on_row_enter)
                    child.bind("<Leave>", on_row_leave)
                
                row_frame.pack(fill='x', pady=2, padx=5)

        def load_processes():
            process_generator = fetch_processes()
            start_index = 0
            try:
                for batch in process_generator:
                    scroll_frame.after(0, load_batch, batch, start_index)
                    start_index += len(batch)
                    scroll_frame.update()
                    time.sleep(0.1)
            except Exception as e:
                print(f"Erro ao carregar processos: {e}")

        threading.Thread(target=load_processes, daemon=True).start()

    def sort_by_column(column):
        nonlocal sort_column, sort_reverse
        if sort_column == column:
            sort_reverse = not sort_reverse
        else:
            sort_column = column
            sort_reverse = False
        atualizar_lista_processos(scroll_frame)

    def mostrar_detalhes(processo):
        for widget in frame.winfo_children():
            widget.destroy()
        
        main_frame = ctk.CTkFrame(frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        btn_voltar = ctk.CTkButton(main_frame, text="⬅️ Voltar", 
                                 command=lambda: atualizar_conteudo(lambda frame: interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio)),
                                 corner_radius=8)
        btn_voltar.pack(anchor="nw", padx=10, pady=10)
        btn_voltar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
        btn_voltar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
        
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"🔹 Processo: {processo['name']}", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"🆔 PID: {processo['pid']}", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"👤 Usuário: {processo['username'] or 'N/A'}", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"⏳ Status: {processo['status']}", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        
        medidores_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        medidores_frame.pack(pady=10, padx=20, fill="x")
        
        cpu_frame = ctk.CTkFrame(medidores_frame, corner_radius=8)
        cpu_frame.pack(side="left", expand=True, padx=10)
        ctk.CTkLabel(cpu_frame, text="Uso de CPU", font=("Arial", 14)).pack(pady=5)
        cpu_canvas = ctk.CTkCanvas(cpu_frame, width=200, height=150, bg="#2b2b2b", highlightthickness=0)
        cpu_canvas.pack()
        cpu_label = ctk.CTkLabel(cpu_frame, text="0%", font=("Arial", 12))
        cpu_label.pack(pady=5)
        
        mem_frame = ctk.CTkFrame(medidores_frame, corner_radius=8)
        mem_frame.pack(side="left", expand=True, padx=10)
        ctk.CTkLabel(mem_frame, text="Uso de Memória", font=("Arial", 14)).pack(pady=5)
        mem_canvas = ctk.CTkCanvas(mem_frame, width=200, height=150, bg="#2b2b2b", highlightthickness=0)
        mem_canvas.pack()
        mem_label = ctk.CTkLabel(mem_frame, text="0 MB", font=("Arial", 12))
        mem_label.pack(pady=5)
        
        controles_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        controles_frame.pack(pady=10, padx=20, fill="x")
        
        btn_encerrar = ctk.CTkButton(controles_frame, text="❌ Encerrar Processo", 
                                    command=lambda: encerrar_processo(processo), corner_radius=8)
        btn_encerrar.pack(side="left", padx=10)
        btn_encerrar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
        btn_encerrar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
        
        running = True
        
        def draw_gauge(canvas, percentage, color, label, is_memory=False):
            canvas.delete("all")
            percentage = min(max(percentage, 0), 100) if not is_memory else percentage
            
            canvas.create_arc(10, 10, 190, 190, start=0, extent=180, 
                            fill="#343638", outline="", style="pieslice")
            extent = -180 * (percentage / (100 if not is_memory else max(percentage, 1)))
            canvas.create_arc(10, 10, 190, 190, start=180, extent=extent, 
                            fill=color, outline="", style="pieslice")
            text = f"{percentage:.1f}%" if not is_memory else f"{percentage:.1f} MB"
            canvas.create_text(100, 100, text=text, font=("Arial", 20, "bold"), fill="white")
            label.configure(text=text)
        
        def atualizar_medidores():
            nonlocal running
            if not running:
                return
            
            try:
                p = psutil.Process(processo['pid'])
                cpu_percent = p.cpu_percent(interval=0.5)
                draw_gauge(cpu_canvas, cpu_percent, "#1f6aa5", cpu_label)
                
                mem_info = p.memory_info()
                mem_mb = mem_info.rss / 1024 / 1024
                draw_gauge(mem_canvas, mem_mb, "#2fa572", mem_label, is_memory=True)
                
                frame.after(1000, atualizar_medidores)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                running = False
                messagebox.showinfo("Info", "O processo não existe mais")
                atualizar_conteudo(lambda frame: interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio))
            except Exception as e:
                running = False
                messagebox.showerror("Erro", f"Erro ao monitorar processo: {e}")
        
        def encerrar_processo(p):
            nonlocal running
            running = False
            
            progress_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            progress_frame.pack(fill="x", pady=10, padx=20)
            
            progress_label = ctk.CTkLabel(progress_frame, text="Encerrando processo...", font=("Arial", 14))
            progress_label.pack(pady=5)
            
            progress_bar = ctk.CTkProgressBar(progress_frame)
            progress_bar.pack(fill="x", padx=10)
            progress_bar.set(0)
            
            def animar_encerramento():
                try:
                    progress = 0
                    while progress < 1:
                        progress += 0.01
                        progress_bar.set(progress)
                        progress_label.configure(text=f"Encerrando... {int(progress*100)}%")
                        frame.update()
                        time.sleep(0.03)
                    
                    proc = psutil.Process(p['pid'])
                    proc.terminate()
                    proc.wait(timeout=1)
                    
                    messagebox.showinfo("Sucesso", "Processo encerrado com sucesso!")
                    atualizar_conteudo(lambda frame: interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio))
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao encerrar processo: {e}")
                    atualizar_conteudo(lambda frame: interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio))
            
            threading.Thread(target=animar_encerramento, daemon=True).start()
        
        atualizar_medidores()
        animate_slide_with_fade(main_frame, -900, 0, axis='x', delay=0, layout_args={'fill': 'both', 'expand': True})

    scroll_frame = ctk.CTkScrollableFrame(frame, height=400, corner_radius=10)
    animate_slide_with_fade(scroll_frame, -300, 0, axis='x', delay=150, layout_args={'fill': 'both', 'expand': True, 'padx': 20, 'pady': 10})

    titulo = ctk.CTkLabel(frame, text="📋 Processos em Execução", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    btn_atualizar = ctk.CTkButton(frame, text="Atualizar 🔄", 
                                 command=lambda: atualizar_lista_processos(scroll_frame),
                                 corner_radius=8, font=("Arial", 14))
    animate_slide_with_fade(btn_atualizar, -300, 0, axis='x', delay=200, layout_args={'pady': 10})
    btn_atualizar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_atualizar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

    btn_voltar = ctk.CTkButton(frame, text="Voltar ⬅️", 
                              command=lambda: atualizar_conteudo(mostrar_inicio),
                              corner_radius=8, font=("Arial", 14))
    btn_voltar.pack(side="bottom", anchor="se", padx=10, pady=10)
    btn_voltar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_voltar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

    atualizar_lista_processos(scroll_frame)
    frame.after(5000, lambda: atualizar_lista_processos(scroll_frame))

def interface_suporte(frame, usuario_id, nome_usuario, is_admin, atualizar_conteudo, mostrar_inicio):
    def contar_admins_online():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE permissao = 1")
            total_admins = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return max(1, total_admins // 2)
        except Exception as e:
            print(f"Erro ao contar admins: {e}")
            return 1

    def carregar_mensagens(chat_id, chat_area):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT usuario_id, mensagem, timestamp, is_admin 
                FROM chat_mensagens 
                WHERE chat_id = %s 
                ORDER BY timestamp
            """, (chat_id,))
            mensagens = cursor.fetchall()
            cursor.close()
            conn.close()

            chat_area.delete("1.0", "end")
            for msg in mensagens:
                prefixo = "Admin" if msg['is_admin'] else nome_usuario
                timestamp = msg['timestamp'].strftime("%d/%m/%Y %H:%M:%S")
                chat_area.insert("end", f"[{timestamp}] {prefixo}: {msg['mensagem']}\n")
            chat_area.see("end")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mensagens: {e}")

    def enviar_mensagem(chat_id, chat_area, mensagem_entry):
        mensagem = mensagem_entry.get().strip()
        if not mensagem:
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_mensagens (chat_id, usuario_id, mensagem, timestamp, is_admin)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (chat_id, usuario_id, mensagem, is_admin))
            conn.commit()
            cursor.close()
            conn.close()

            mensagem_entry.delete(0, "end")
            carregar_mensagens(chat_id, chat_area)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar mensagem: {e}")

    def interface_chat_premium():
        chat_id = f"chat_{usuario_id}"
        chat_frame = ctk.CTkFrame(frame, corner_radius=10)
        chat_frame.pack(fill="both", expand=True, pady=10, padx=20)

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT COUNT(*) as new_messages
                FROM chat_mensagens
                WHERE chat_id = %s AND is_admin = TRUE AND timestamp > (
                    SELECT MAX(timestamp) FROM chat_mensagens WHERE usuario_id = %s AND is_admin = FALSE
                )
            """, (chat_id, usuario_id))
            new_messages = cursor.fetchone()['new_messages']
            cursor.close()
            conn.close()
            if new_messages > 0:
                messagebox.showinfo("Notificação", "Você recebeu uma nova resposta de um administrador!")
        except Exception as e:
            print(f"Erro ao verificar novas mensagens: {e}")

        chat_area = ctk.CTkTextbox(chat_frame, height=300, corner_radius=8, state="disabled")
        chat_area.pack(fill="both", expand=True, pady=5)
        chat_area.configure(state="normal")

        mensagem_entry = ctk.CTkEntry(chat_frame, placeholder_text="Digite sua mensagem...", width=400, corner_radius=8)
        mensagem_entry.pack(side="left", pady=5, padx=5)

        btn_enviar = ctk.CTkButton(chat_frame, text="Enviar 📤", command=lambda: enviar_mensagem(chat_id, chat_area, mensagem_entry), corner_radius=8)
        btn_enviar.pack(side="left", pady=5)
        btn_enviar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
        btn_enviar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

        def atualizar_chat():
            carregar_mensagens(chat_id, chat_area)
            frame.after(5000, atualizar_chat)

        carregar_mensagens(chat_id, chat_area)
        atualizar_chat()

    def interface_chat_admin():
        def carregar_chats():
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="12345678",
                    database="cleannmaster"
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT DISTINCT cm.chat_id, u.nome 
                    FROM chat_mensagens cm 
                    JOIN usuarios u ON cm.usuario_id = u.id 
                    WHERE u.tipo_usuario = 'premium'
                """)
                chats = cursor.fetchall()
                cursor.close()
                conn.close()

                for widget in chats_frame.winfo_children():
                    widget.destroy()

                for chat in chats:
                    chat_btn = ctk.CTkButton(
                        chats_frame,
                        text=f"Chat com {chat['nome']}",
                        command=lambda cid=chat['chat_id'], nome=chat['nome']: abrir_chat(cid, nome),
                        corner_radius=8
                    )
                    chat_btn.pack(fill="x", pady=2)
                    chat_btn.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
                    chat_btn.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar chats: {e}")

        def abrir_chat(chat_id, nome_usuario_chat):
            for widget in chat_area_frame.winfo_children():
                widget.destroy()

            chat_area = ctk.CTkTextbox(chat_area_frame, height=300, corner_radius=8, state="disabled")
            chat_area.pack(fill="both", expand=True, pady=5)
            chat_area.configure(state="normal")

            mensagem_entry = ctk.CTkEntry(chat_area_frame, placeholder_text="Digite sua resposta...", width=400, corner_radius=8)
            mensagem_entry.pack(side="left", pady=5, padx=5)

            btn_enviar = ctk.CTkButton(chat_area_frame, text="Enviar 📤", command=lambda: enviar_mensagem(chat_id, chat_area, mensagem_entry), corner_radius=8)
            btn_enviar.pack(side="left", pady=5)
            btn_enviar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
            btn_enviar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

            def atualizar_chat():
                carregar_mensagens(chat_id, chat_area)
                frame.after(5000, atualizar_chat)

            carregar_mensagens(chat_id, chat_area)
            atualizar_chat()

        main_frame = ctk.CTkFrame(frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        chats_frame = ctk.CTkFrame(main_frame, width=200, corner_radius=10)
        chats_frame.pack(side="left", fill="y", padx=10)

        chat_area_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        chat_area_frame.pack(side="right", fill="both", expand=True, padx=10)

        ctk.CTkLabel(chats_frame, text="Chats Ativos", font=("Arial", 16, "bold")).pack(pady=10)
        carregar_chats()

    titulo = ctk.CTkLabel(frame, text="💬 Suporte", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    admins_online = contar_admins_online()
    status_label = ctk.CTkLabel(frame, text=f"Admins Online: {admins_online}", font=("Arial", 14))
    status_label.pack(pady=10)

    if is_admin:
        interface_chat_admin()
    else:
        interface_chat_premium()

    btn_voltar = ctk.CTkButton(frame, text="Voltar ⬅️", 
                              command=lambda: atualizar_conteudo(mostrar_inicio),
                              corner_radius=8, font=("Arial", 14))
    btn_voltar.pack(side="bottom", anchor="se", padx=10, pady=10)
    btn_voltar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_voltar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

def interface_admin(frame, usuario_id, atualizar_conteudo, mostrar_inicio):
    def gerar_chave():
        tipo_var = tipo_chave.get()
        chave = str(uuid.uuid4()).replace("-", "").upper()[:16]
        data_expiracao = None
        if tipo_var == "30 Dias":
            data_expiracao = datetime.now() + timedelta(days=30)
        elif tipo_var == "90 Dias":
            data_expiracao = datetime.now() + timedelta(days=90)
        elif tipo_var == "Vitalícia":
            data_expiracao = None

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chaves (chave, tipo_licenca, data_expiracao, ativa, usada, usada_por, email_usuario, data_ativacao)
                VALUES (%s, %s, %s, TRUE, FALSE, NULL, NULL, NULL)
            """, (chave, tipo_var, data_expiracao))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Sucesso", f"Chave gerada: {chave}")
            chave_entry.delete(0, "end")
            chave_entry.insert(0, chave)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar chave: {e}")

    def pesquisar_usuario():
        email = email_pesquisa_entry.get().strip()
        if not email:
            messagebox.showwarning("Aviso", "Por favor, insira um email.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, email, tipo_usuario, permissao FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()

            for widget in resultado_frame.winfo_children():
                widget.destroy()

            if usuario:
                usuario_frame = ctk.CTkFrame(resultado_frame, corner_radius=10)
                usuario_frame.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(usuario_frame, text=f"Nome: {usuario['nome']}", font=("Arial", 14)).pack(anchor="w", pady=2)
                ctk.CTkLabel(usuario_frame, text=f"Email: {usuario['email']}", font=("Arial", 14)).pack(anchor="w", pady=2)
                ctk.CTkLabel(usuario_frame, text=f"Tipo: {usuario['tipo_usuario']}", font=("Arial", 14)).pack(anchor="w", pady=2)
                ctk.CTkLabel(usuario_frame, text=f"Permissão: {'Admin' if usuario['permissao'] == 1 else 'Normal'}", font=("Arial", 14)).pack(anchor="w", pady=2)

                def adicionar_licenca():
                    tipo_var = tipo_licenca_adicionar.get()
                    data_expiracao = None
                    if tipo_var == "30 Dias":
                        data_expiracao = datetime.now() + timedelta(days=30)
                    elif tipo_var == "90 Dias":
                        data_expiracao = datetime.now() + timedelta(days=90)
                    elif tipo_var == "Vitalícia":
                        data_expiracao = None

                    chave = str(uuid.uuid4()).replace("-", "").upper()[:16]
                    try:
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="12345678",
                            database="cleannmaster"
                        )
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO chaves (chave, tipo_licenca, data_expiracao, ativa, usada, usada_por, email_usuario, data_ativacao)
                            VALUES (%s, %s, %s, TRUE, TRUE, %s, %s, NOW())
                        """, (chave, tipo_var, data_expiracao, usuario['id'], usuario['email']))
                        cursor.execute("""
                            UPDATE usuarios SET tipo_usuario = 'premium', data_expiracao = %s WHERE id = %s
                        """, (data_expiracao, usuario['id']))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        messagebox.showinfo("Sucesso", f"Licença adicionada para {usuario['nome']} com chave: {chave}")
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao adicionar licença: {e}")

                def remover_licenca():
                    try:
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="12345678",
                            database="cleannmaster"
                        )
                        cursor = conn.cursor()
                        cursor.execute("UPDATE chaves SET ativa = FALSE, usada = FALSE, usada_por = NULL, email_usuario = NULL WHERE usada_por = %s", (usuario['id'],))
                        cursor.execute("UPDATE usuarios SET tipo_usuario = 'free', data_expiracao = NULL WHERE id = %s", (usuario['id'],))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        messagebox.showinfo("Sucesso", f"Licença removida de {usuario['nome']}")
                        for widget in resultado_frame.winfo_children():
                            widget.destroy()
                        pesquisar_usuario()
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao remover licença: {e}")

                tipo_licenca_adicionar = ctk.StringVar(value="30 Dias")
                ctk.CTkLabel(usuario_frame, text="Adicionar Licença:", font=("Arial", 14)).pack(anchor="w", pady=2)
                ctk.CTkOptionMenu(usuario_frame, values=["30 Dias", "90 Dias", "Vitalícia"], variable=tipo_licenca_adicionar).pack(anchor="w", pady=2)
                btn_adicionar = ctk.CTkButton(usuario_frame, text="Adicionar Licença", command=adicionar_licenca, corner_radius=8)
                btn_adicionar.pack(anchor="w", pady=2)
                btn_adicionar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
                btn_adicionar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

                btn_remover = ctk.CTkButton(usuario_frame, text="Remover Licença", command=remover_licenca, corner_radius=8)
                btn_remover.pack(anchor="w", pady=2)
                btn_remover.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
                btn_remover.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
            else:
                ctk.CTkLabel(resultado_frame, text="Usuário não encontrado.", font=("Arial", 14)).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao pesquisar usuário: {e}")

    titulo = ctk.CTkLabel(frame, text="👑 Painel de Administração", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    tipo_chave = ctk.StringVar(value="30 Dias")
    ctk.CTkLabel(frame, text="Gerar Chave de Licença:", font=("Arial", 14)).pack(pady=5)
    ctk.CTkOptionMenu(frame, values=["30 Dias", "90 Dias", "Vitalícia"], variable=tipo_chave).pack(pady=5)
    chave_entry = ctk.CTkEntry(frame, placeholder_text="Chave será exibida aqui", width=200, corner_radius=8)
    chave_entry.pack(pady=5)
    btn_gerar = ctk.CTkButton(frame, text="Gerar Chave", command=gerar_chave, corner_radius=8)
    btn_gerar.pack(pady=10)
    btn_gerar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_gerar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

    ctk.CTkLabel(frame, text="Pesquisar Usuário por Email:", font=("Arial", 14)).pack(pady=5)
    email_pesquisa_entry = ctk.CTkEntry(frame, placeholder_text="Digite o email", width=200, corner_radius=8)
    email_pesquisa_entry.pack(pady=5)
    btn_pesquisar = ctk.CTkButton(frame, text="Pesquisar", command=pesquisar_usuario, corner_radius=8)
    btn_pesquisar.pack(pady=10)
    btn_pesquisar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_pesquisar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

    resultado_frame = ctk.CTkScrollableFrame(frame, height=300, corner_radius=10)
    resultado_frame.pack(fill="both", expand=True, pady=10, padx=20)

    btn_voltar = ctk.CTkButton(frame, text="Voltar ⬅️", 
                              command=lambda: atualizar_conteudo(mostrar_inicio),
                              corner_radius=8, font=("Arial", 14))
    btn_voltar.pack(side="bottom", anchor="se", padx=10, pady=10)
    btn_voltar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
    btn_voltar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

def interface_suporte_remoto(frame, atualizar_conteudo, mostrar_inicio):
    def abrir_anydesk():
        # Typical AnyDesk installation path on Windows
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
        
        if os.path.exists(anydesk_path):
            try:
                os.startfile(anydesk_path)
                messagebox.showinfo("Sucesso", "AnyDesk aberto com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao abrir o AnyDesk: {e}")
        else:
            if messagebox.askyesno("AnyDesk não instalado", "AnyDesk não está instalado. Deseja visitar a página de download?"):
                webbrowser.open("https://anydesk.com/pt/downloads")
    
    # Interface elements
    titulo = ctk.CTkLabel(frame, text="🖥️ Suporte Remoto (AnyDesk)", font=("Arial", 18, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 20})

    instrucao_label = ctk.CTkLabel(frame, text="Clique no botão abaixo para abrir o AnyDesk ou baixá-lo se não estiver instalado.", font=("Arial", 14))
    animate_slide_with_fade(instrucao_label, -300, 0, axis='x', delay=150, layout_args={'pady': 10})

    btn_abrir_anydesk = ctk.CTkButton(frame, text="Abrir AnyDesk 📡", command=abrir_anydesk, width=200, corner_radius=8, font=("Arial", 14))
    animate_slide_with_fade(btn_abrir_anydesk, -300, 0, axis='x', delay=200, layout_args={'pady': 20})

    btn_voltar = ctk.CTkButton(frame, text="Voltar ⬅️", 
                              command=lambda: atualizar_conteudo(mostrar_inicio),
                              corner_radius=8, font=("Arial", 14))
    btn_voltar.pack(side="bottom", anchor="se", padx=10, pady=10)

    def on_enter(e):
        e.widget.configure(fg_color="#1f6aa5")
    
    def on_leave(e):
        e.widget.configure(fg_color="#14375e")

    btn_abrir_anydesk.bind("<Enter>", on_enter)
    btn_abrir_anydesk.bind("<Leave>", on_leave)
    btn_voltar.bind("<Enter>", on_enter)
    btn_voltar.bind("<Leave>", on_leave)


def abrir_cleanning_master(nome_usuario, status, usuario_id, email, is_premium, licenca, root=None):
    if root:
        root.destroy()

    root = ctk.CTk()
    root.title("CleanningMaster 💼")
    root.geometry("900x600")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    sidebar = ctk.CTkFrame(root, width=200, corner_radius=10, fg_color="#1a2634")
    sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    sidebar.grid_rowconfigure(6, weight=1)

    content_frame = ctk.CTkFrame(root, corner_radius=10)
    content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def atualizar_conteudo(funcao):
        for widget in content_frame.winfo_children():
            widget.destroy()
        frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        funcao(frame)
        animate_slide_with_fade(content_frame, -900, 0, axis='x', delay=0, layout_manager='grid', layout_args={'row': 0, 'column': 1, 'sticky': 'nsew', 'padx': 10, 'pady': 10})

    def criar_botao_sidebar(texto, comando, posicao):
        btn = ctk.CTkButton(
            sidebar, text=texto, command=comando, corner_radius=8, height=40,
            border_spacing=10, anchor="w", fg_color="#14375e", hover_color="#1f6aa5",
            font=("Arial", 14), border_width=2, border_color="#2b2b2b"
        )
        
        btn.original_width = btn.winfo_reqwidth()
        btn.original_height = btn.winfo_reqheight()
        scale_factor = 1.05

        def on_enter(e):
            btn.configure(fg_color="#1f6aa5", border_color="#1f6aa5")
            btn.configure(width=int(btn.original_width * scale_factor), height=int(btn.original_height * scale_factor))

        def on_leave(e):
            btn.configure(fg_color="#14375e", border_color="#2b2b2b")
            btn.configure(width=btn.original_width, height=btn.original_height)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        animate_slide_with_fade(
            btn, -200, 0, axis='x', delay=100 + posicao * 100,
            layout_manager='grid',
            layout_args={'row': posicao, 'column': 0, 'sticky': 'ew', 'padx': 10, 'pady': 5}
        )
        return btn

    posicao = 0
    btn_limpar = criar_botao_sidebar("🧹 Limpar Temporários", lambda: atualizar_conteudo(lambda frame: interface_limpar_temp(frame)), posicao)
    posicao += 1
    if is_premium or "Admin" in status:
        btn_processos = criar_botao_sidebar("📋 Listar Processos", lambda: atualizar_conteudo(lambda frame: interface_listar_processos(frame, atualizar_conteudo, mostrar_inicio)), posicao)
        posicao += 1
        btn_agendamentos = criar_botao_sidebar("⏰ Agendamentos", lambda: atualizar_conteudo(lambda frame: interface_agendamentos(frame)), posicao)
        posicao += 1
        btn_suporte = criar_botao_sidebar("💬 Suporte", lambda: atualizar_conteudo(lambda frame: interface_suporte(frame, usuario_id, nome_usuario, "Admin" in status, atualizar_conteudo, mostrar_inicio)), posicao)
        posicao += 1
        if "Admin" in status:
            btn_admin = criar_botao_sidebar("👑 Administração", lambda: atualizar_conteudo(lambda frame: interface_admin(frame, usuario_id, atualizar_conteudo, mostrar_inicio)), posicao)
            posicao += 1
        btn_suporte_remoto = criar_botao_sidebar("🖥️ Suporte Remoto", lambda: atualizar_conteudo(lambda frame: interface_suporte_remoto(frame, atualizar_conteudo, mostrar_inicio)), posicao)
        posicao += 1

    rodape = ctk.CTkFrame(root, height=40, fg_color="#1a2634")
    rodape.grid(row=1, column=0, columnspan=2, sticky="ew")
    rodape.grid_columnconfigure(0, weight=1)

    perfil_label = ctk.CTkLabel(rodape, text=f"👤 {nome_usuario} | {status}", cursor="hand2", font=("Arial", 14))
    perfil_label.pack(side="left", padx=10)

    def confirm_logout():
        if messagebox.askyesno("Confirmação", "Deseja realmente sair?"):
            root.destroy()
            abrir_login()

    logout_btn = ctk.CTkButton(rodape, text="Sair 🔓", command=confirm_logout, width=100, corner_radius=8, fg_color="#14375e", hover_color="#1f6aa5")
    logout_btn.pack(side="right", padx=10)

    def mostrar_perfil():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT permissao FROM usuarios WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()
            
            tipo_usuario = "Admin" if usuario['permissao'] == 1 else "Normal"
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar tipo de usuário: {e}")
            tipo_usuario = "Desconhecido"

        for widget in content_frame.winfo_children():
            widget.destroy()
        frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="📋 Perfil do Usuário", font=("Arial", 20, "bold")).pack(pady=20)
        
        info_frame = ctk.CTkFrame(frame, corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"👤 Nome: {nome_usuario}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(info_frame, text=f"📧 Email: {email}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(info_frame, text=f"💼 Status: {status}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
        ctk.CTkLabel(info_frame, text=f"👥 Tipo de Usuário: {tipo_usuario}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
        
        if licenca:
            chave = licenca['chave']
            censored_chave = f"{chave[:4]}****{chave[-4:]}"
            
            data_ativacao = licenca['data_ativacao']
            data_expiracao = licenca['data_expiracao']
            hoje = datetime.now().date()
            
            dias_restantes = (data_expiracao - hoje).days
            dias_totais = (data_expiracao - data_ativacao.date()).days
            
            ctk.CTkLabel(info_frame, text=f"🔑 Chave Ativa: {censored_chave}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
            ctk.CTkLabel(info_frame, text=f"📅 Tipo de Licença: {licenca['tipo_licenca']}", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
            ctk.CTkLabel(info_frame, text=f"⏳ Dias Restantes: {dias_restantes} dias", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
            ctk.CTkLabel(info_frame, text=f"📆 Duração Total: {dias_totais} dias", font=("Arial", 14)).pack(anchor="w", pady=5, padx=10)
        
        def ativar_chave():
            chave = chave_entry.get().strip().upper()
            if not chave:
                messagebox.showwarning("Aviso", "Por favor, insira uma chave.")
                return
            
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="12345678",
                    database="cleannmaster"
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id, chave, ativa, usada_por, tipo_licenca, data_expiracao 
                    FROM chaves WHERE chave = %s
                """, (chave,))
                dados_chave = cursor.fetchone()

                if not dados_chave:
                    messagebox.showerror("Erro", "Chave inválida.")
                elif not dados_chave['ativa']:
                    messagebox.showwarning("Aviso", "Esta chave já foi usada.")
                elif dados_chave['usada_por'] is not None:
                    messagebox.showwarning("Aviso", "Esta chave já foi ativada por outro usuário.")
                else:
                    tipo_licenca = dados_chave['tipo_licenca']
                    data_expiracao = dados_chave['data_expiracao']
                    data_expiracao_formatada = data_expiracao.strftime('%d/%m/%Y') if data_expiracao else "Sem data de expiração"
                    ultimos_digitos = dados_chave['chave'][-4:]

                    cursor.execute("""
                        UPDATE chaves 
                        SET usada = TRUE, ativa = FALSE, usada_por = %s, email_usuario = %s, data_ativacao = NOW() 
                        WHERE id = %s
                    """, (usuario_id, email, dados_chave['id']))
                    conn.commit()

                    cursor.execute("""
                        UPDATE usuarios 
                        SET tipo_usuario = 'premium', data_expiracao = %s 
                        WHERE id = %s
                    """, (data_expiracao, usuario_id))
                    conn.commit()

                    messagebox.showinfo("Sucesso", f"Chave ativada com sucesso! Últimos 4 dígitos: {ultimos_digitos}. Licença: {tipo_licenca}. Expiração: {data_expiracao_formatada}.")
                    root.destroy()
                    licenca_nova = verificar_licenca(usuario_id)
                    abrir_cleanning_master(nome_usuario, "💎 Premium", usuario_id, email, True, licenca_nova)
                
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ativar chave: {e}")

        chave_label = ctk.CTkLabel(frame, text="Ativar Chave:", font=("Arial", 14))
        chave_label.pack(pady=5)
        chave_entry = ctk.CTkEntry(frame, width=250, corner_radius=8)
        chave_entry.pack(pady=5)
        ativar_btn = ctk.CTkButton(frame, text="Ativar 🔑", command=ativar_chave, corner_radius=8)
        ativar_btn.pack(pady=10)
        ativar_btn.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
        ativar_btn.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))

        btn_voltar = ctk.CTkButton(frame, text="Voltar ⬅️", command=lambda: atualizar_conteudo(mostrar_inicio), corner_radius=8)
        btn_voltar.pack(pady=20)
        btn_voltar.bind("<Enter>", lambda e: e.widget.configure(fg_color="#1f6aa5"))
        btn_voltar.bind("<Leave>", lambda e: e.widget.configure(fg_color="#14375e"))
        
        animate_slide_with_fade(frame, -900, 0, axis='x', delay=0, layout_args={'fill': 'both', 'expand': True})

    def mostrar_inicio():
        for widget in content_frame.winfo_children():
            widget.destroy()
        frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="🖥️ CleanningMaster", font=("Arial", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text="Bem-vindo ao seu gerenciador de sistema", font=("Arial", 16)).pack(pady=10)
        
        stats_frame = ctk.CTkFrame(frame, corner_radius=10)
        stats_frame.pack(pady=20, padx=20, fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        cpu_frame = ctk.CTkFrame(stats_frame, corner_radius=8)
        cpu_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        ctk.CTkLabel(cpu_frame, text="CPU Usage", font=("Arial", 14)).pack(pady=5)
        cpu_bar = ctk.CTkProgressBar(cpu_frame, width=150)
        cpu_bar.pack(pady=5)
        cpu_label = ctk.CTkLabel(cpu_frame, text="0%", font=("Arial", 12))
        cpu_label.pack()
        
        mem_frame = ctk.CTkFrame(stats_frame, corner_radius=8)
        mem_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        ctk.CTkLabel(mem_frame, text="Memory Usage", font=("Arial", 14)).pack(pady=5)
        mem_bar = ctk.CTkProgressBar(mem_frame, width=150)
        mem_bar.pack(pady=5)
        mem_label = ctk.CTkLabel(mem_frame, text="0%", font=("Arial", 12))
        mem_label.pack()
        
        disk_frame = ctk.CTkFrame(stats_frame, corner_radius=8)
        disk_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        ctk.CTkLabel(disk_frame, text="Disk Usage", font=("Arial", 14)).pack(pady=5)
        disk_bar = ctk.CTkProgressBar(disk_frame, width=150)
        disk_bar.pack(pady=5)
        disk_label = ctk.CTkLabel(disk_frame, text="0%", font=("Arial", 12))
        disk_label.pack()
        
        proc_frame = ctk.CTkFrame(stats_frame, corner_radius=8)
        proc_frame.grid(row=0, column=3, padx=10, pady=5, sticky="nsew")
        ctk.CTkLabel(proc_frame, text="Running Processes", font=("Arial", 14)).pack(pady=5)
        proc_label = ctk.CTkLabel(proc_frame, text="0", font=("Arial", 12))
        proc_label.pack(pady=5)
        
        def update_stats():
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                mem_usage = psutil.virtual_memory().percent
                disk_usage = psutil.disk_usage('/').percent
                proc_count = len(list(psutil.process_iter()))
                
                cpu_bar.set(cpu_usage / 100)
                cpu_label.configure(text=f"{cpu_usage:.1f}%")
                mem_bar.set(mem_usage / 100)
                mem_label.configure(text=f"{mem_usage:.1f}%")
                disk_bar.set(disk_usage / 100)
                disk_label.configure(text=f"{disk_usage:.1f}%")
                proc_label.configure(text=str(proc_count))
                
                frame.after(5000, update_stats)
            except Exception as e:
                print(f"Erro ao atualizar estatísticas: {e}")
        
        update_stats()
        animate_slide_with_fade(frame, -900, 0, axis='x', delay=0, layout_args={'fill': 'both', 'expand': True})

    perfil_label.bind("<Button-1>", lambda e: mostrar_perfil())
    animate_slide_with_fade(content_frame, -900, 0, axis='x', delay=0, layout_manager='grid', layout_args={'row': 0, 'column': 1, 'sticky': 'nsew', 'padx': 10, 'pady': 10})
    mostrar_inicio()

    root.mainloop()

def abrir_login():
    login_window = ctk.CTk()
    login_window.title("Login - CleanningMaster")
    login_window.geometry("400x500")

    def fazer_login():
        email_ou_nome = email_entry.get()
        senha = senha_entry.get()

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s OR nome = %s", (email_ou_nome, email_ou_nome))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario['senha'], senha):
                licenca = verificar_licenca(usuario['id'])
                status = "⚙️ Free"
                is_premium = False

                if usuario['permissao'] == 1:
                    status = "👑 Admin"
                elif usuario['tipo_usuario'] == 'premium' and (not usuario['data_expiracao'] or usuario['data_expiracao'] >= date.today()):
                    status = "💎 Premium"
                    is_premium = True
                elif licenca:
                    status = "💎 Premium"
                    is_premium = True

                login_window.destroy()
                abrir_cleanning_master(usuario['nome'], status, usuario['id'], usuario['email'], is_premium, licenca)
            else:
                messagebox.showerror("Erro de login", "Nome/email ou senha incorretos.")

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar: {e}")

    def ir_para_registro():
        login_window.destroy()
        abrir_registro()

    frame = ctk.CTkFrame(login_window, corner_radius=10)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    titulo = ctk.CTkLabel(frame, text="💻 CleanningMaster", font=("Arial", 24, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 40})

    email_entry = ctk.CTkEntry(frame, placeholder_text="Nome ou Email", width=250, corner_radius=8)
    animate_slide_with_fade(email_entry, -300, 0, axis='x', delay=200, layout_args={'pady': 10})

    senha_entry = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", width=250, corner_radius=8)
    animate_slide_with_fade(senha_entry, -300, 0, axis='x', delay=250, layout_args={'pady': 10})

    login_btn = ctk.CTkButton(frame, text="Entrar 🚀", command=fazer_login, width=250, corner_radius=8)
    animate_slide_with_fade(login_btn, -300, 0, axis='x', delay=300, layout_args={'pady': 20})

    def on_enter(e):
        e.widget.configure(fg_color="#1f6aa5")
    
    def on_leave(e):
        e.widget.configure(fg_color="#14375e")

    login_btn.bind("<Enter>", on_enter)
    login_btn.bind("<Leave>", on_leave)

    registro_btn = ctk.CTkButton(frame, text="Registrar ✍️", command=ir_para_registro, width=250, corner_radius=8)
    animate_slide_with_fade(registro_btn, -300, 0, axis='x', delay=350, layout_args={'pady': 10})

    registro_btn.bind("<Enter>", on_enter)
    registro_btn.bind("<Leave>", on_leave)

    login_window.mainloop()

def abrir_registro():
    registro_window = ctk.CTk()
    registro_window.title("Registro - CleanningMaster")
    registro_window.geometry("400x550")

    def registrar():
        nome = nome_entry.get()
        email = email_entry.get()
        senha = senha_entry.get()

        if not nome or not email or not senha:
            messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
            return

        senha_hash = generate_password_hash(senha)

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345678",
                database="cleannmaster"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nome = %s", (nome,))
            nome_existe = cursor.fetchone()[0]
            if nome_existe > 0:
                messagebox.showerror("Erro", "Nome de usuário já cadastrado. Escolha outro nome.")
                cursor.close()
                conn.close()
                return

            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, tipo_usuario, permissao)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, 'free', 0))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
            registro_window.destroy()
            abrir_login()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Email já cadastrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar: {e}")

    def voltar_login():
        registro_window.destroy()
        abrir_login()

    frame = ctk.CTkFrame(registro_window, corner_radius=10)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    titulo = ctk.CTkLabel(frame, text="🖊️ Registrar-se", font=("Arial", 24, "bold"))
    animate_slide_with_fade(titulo, -200, 0, axis='y', delay=100, layout_args={'pady': 30})

    nome_entry = ctk.CTkEntry(frame, placeholder_text="Nome completo", width=250, corner_radius=8)
    animate_slide_with_fade(nome_entry, -300, 0, axis='x', delay=150, layout_args={'pady': 10})

    email_entry = ctk.CTkEntry(frame, placeholder_text="Email", width=250, corner_radius=8)
    animate_slide_with_fade(email_entry, -300, 0, axis='x', delay=200, layout_args={'pady': 10})

    senha_entry = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", width=250, corner_radius=8)
    animate_slide_with_fade(senha_entry, -300, 0, axis='x', delay=250, layout_args={'pady': 10})

    registrar_btn = ctk.CTkButton(frame, text="Registrar ✔️", command=registrar, width=250, corner_radius=8)
    animate_slide_with_fade(registrar_btn, -300, 0, axis='x', delay=300, layout_args={'pady': 20})

    def on_enter(e):
        e.widget.configure(fg_color="#1f6aa5")
    
    def on_leave(e):
        e.widget.configure(fg_color="#14375e")

    registrar_btn.bind("<Enter>", on_enter)
    registrar_btn.bind("<Leave>", on_leave)

    voltar_btn = ctk.CTkButton(frame, text="Voltar ⬅️", command=voltar_login, width=250, corner_radius=8)
    animate_slide_with_fade(voltar_btn, -300, 0, axis='x', delay=350, layout_args={'pady': 10})

    voltar_btn.bind("<Enter>", on_enter)
    voltar_btn.bind("<Leave>", on_leave)

    registro_window.mainloop()

if __name__ == "__main__":
    abrir_login()
    criar_banco_e_tabelas()
