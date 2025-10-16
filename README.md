# Flask CleanMaster - Sistema de Gerenciamento de Licenças

Este é um projeto web desenvolvido com **Flask** que funciona como um sistema completo para gerenciamento de usuários e ativação de licenças de software. Ele foi projetado para servir como backend para um produto que possui versões "free" e "premium".

O sistema inclui uma interface para usuários finais (cadastro, login, ativação de chaves) e um painel de administração para visualizar e gerenciar todos os usuários e licenças geradas.

![Imagem de um dashboard de software](https://images.ctfassets.net/s5uo95nf6njh/2f3yoyT419m1s52gPSf73C/30b9e8461ac7614d1872b217036394e3/product-tour-dashboard-1a.png)

## ✨ Funcionalidades

* **Sistema de Autenticação de Usuários**:
    * Cadastro, login (por nome de usuário ou e-mail) e logout.
    * Senhas armazenadas de forma segura com hash (`Werkzeug Security`).
    * Sessões de usuário persistentes (login dura 7 dias).
* **Gerenciamento de Licenças (Chaves)**:
    * Geração de chaves de licença no formato `XXXX-XXXX-XXXX`.
    * Página para usuários ativarem suas chaves.
    * Upgrade automático do tipo de usuário de `free` para `premium` após a ativação.
    * Visualização de licenças ativas e seu tempo de expiração.
* **Painel do Usuário**:
    * Dashboard principal para usuários logados.
    * Página de perfil para visualizar e atualizar informações (nome e senha).
    * Visualização e gerenciamento das licenças vinculadas à conta.
* **Painel de Administração**:
    * Acesso restrito a usuários com permissão de administrador.
    * Visualização completa de todos os usuários cadastrados no sistema.
    * Visualização de todas as chaves de licença, seu status (ativa/usada), e a qual usuário estão vinculadas.

***

## 🛠️ Tecnologias Utilizadas

* **Backend**: Python 3, Flask
* **Banco de Dados**: MySQL (com a biblioteca `Flask-MySQLdb`)
* **Gerenciamento de Sessão**: `Flask-Session`
* **Segurança**: `Werkzeug` para hashing de senhas

***

## 🚀 Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente.

### 1. Pré-requisitos

* Python 3.8+
* Um servidor de banco de dados MySQL ativo.

### 2. Clone o Repositório

```bash
git clone <url-do-seu-repositorio>
cd <nome-da-pasta>
```

## Equipe do Projeto
| nome | foto |
| -------- | -------- |
| Diogo Borges |<img src="https://github.com/digogsxd.png" height="75" width="75"> |
| Lucas Coutinho |<img src="https://github.com/uscascus.png" height="75" width="75"> |
| Kaio Lucas |<img src="https://github.com/kaiolucas01.png" height="75" width="75"> |
