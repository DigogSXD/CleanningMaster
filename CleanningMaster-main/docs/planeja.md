<div align="center">
  <img src="" height="auto" width="100%"/>
</div>

# Diário de Desenvolvimento - Software de Otimização de PC

## Data: 19/02/2025

### Escolha das Tecnologias e Bibliotecas

**Objetivo:**  
<p>Desenvolver um software que otimize PCs limpando arquivos desnecessários, removendo duplicatas e, possivelmente, gerenciando programas instalados.</p>

#### Linguagem de Programação:
- **Python**: Escolhido por sua robustez em manipulação de sistemas e scripts, além de ter uma vasta coleção de bibliotecas para tarefas de sistema.

#### Frontend:
- **HTML, CSS, JavaScript**: Para criar uma interface de usuário intuitiva e responsiva, mostrando o que o usuário pode fazer no software.

#### Backend:

**Bibliotecas Python Utilizadas:**

  - **os**: Para operações de sistema de arquivos básicas.
  - **shutil**: Para operações avançadas de arquivos como mover, copiar e remover.
  - **pathlib**: Para manipulação de caminhos de arquivo de maneira mais moderna.
  - **psutil**: Para monitoramento de recursos do sistema, especialmente uso de disco.
  - **hashlib**: Para calcular hashes de arquivos na detecção de duplicatas.
  - **winreg** (somente Windows): Para manipulação do registro do Windows (uso com cautela).
  - **filecmp**: Para comparação de arquivos.
  - **win32com** (via `pywin32`): Para interações com o Windows COM, como desinstalação de software.
  - **tkinter** (ou **PyQt**): Para a interface gráfica, com preferência por PyQt para uma interface mais moderna e complexa.
  - **logging**: Para registrar atividades e erros.
  - **configparser**: Para gerenciar configurações do software.


**Considerações de Interface:**

- **Paleta de Cores:** Optamos por uma paleta de cores que transmita eficiência e tranquilidade, com tons de azul escuro (#003366) e branco para o texto e elementos interativos. 
- **Justificativa:** Azul escuro foi escolhido para simbolizar confiabilidade e segurança, enquanto o branco para garantir boa legibilidade e um visual limpo.

**Próximos Passos:**

- Configurar o ambiente de desenvolvimento.
- Criar a estrutura básica do projeto.
- Implementar a primeira funcionalidade de limpeza de arquivos temporários para testar a integração entre backend e frontend.

## Histórico de Versões

| Versão |    Data    | Descrição           | Autor(es)                                          |
|--------|:----------:|---------------------|----------------------------------------------------|
| 1.0    | 19/02/2026 | Primeiros passos    | [Diogo Borges de Moura](https://github.com/DigogSXD) |