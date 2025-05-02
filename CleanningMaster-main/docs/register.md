# Documentação da Página de Cadastro

## Visão Geral

O arquivo `register.html` faz parte do projeto CleanningMaster e serve como a página de cadastro para novos usuários. Ele fornece um formulário para que os usuários insiram seu nome, e-mail e senha, além de uma opção para se cadastrar usando o Google.

## Estrutura

- **Documento HTML5**: O arquivo é estruturado como um documento HTML5 padrão com a declaração `<!DOCTYPE html>`.
- **Idioma**: O documento está configurado para o português do Brasil (`lang="pt-br"`).

## Seção Head

- **Meta Tags**: Inclui configurações de conjunto de caracteres e viewport para design responsivo.
- **Título**: O título da página é "Cadastro - CleanningMaster".
- **Folhas de Estilo**: 
  - O CSS do Bootstrap é incluído para estilização.
  - Uma folha de estilo personalizada `style.css` é vinculada para estilos adicionais.

## Seção Body

- **Barra de Navegação**: 
  - Uma barra de navegação responsiva com links para as páginas inicial e de login.
- **Formulário de Cadastro**:
  - Contém campos para nome, e-mail e senha.
  - Inclui um botão de envio e um botão de cadastro com o Google.

## Scripts

- **Cadastro com Google**: 
  - A página inclui um script para lidar com o cadastro do Google, inicializando a API de contas do Google e renderizando um botão de cadastro.
  - Um espaço reservado para o ID do Cliente do Google está presente, que deve ser substituído por um ID real.

## Uso

Esta página é projetada para registrar novos usuários, seja através do cadastro tradicional com nome/e-mail/senha ou via cadastro com o Google. Certifique-se de que o ID do Cliente do Google esteja configurado corretamente para que a funcionalidade de cadastro funcione. 