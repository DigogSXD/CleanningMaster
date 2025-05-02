# Documentação da Página de Login

## Visão Geral

O arquivo `login.html` faz parte do projeto CleanningMaster e serve como a página de login para os usuários. Ele fornece um formulário para que os usuários insiram seu e-mail e senha, além de uma opção para entrar usando o Google.

## Estrutura

- **Documento HTML5**: O arquivo é estruturado como um documento HTML5 padrão com a declaração `<!DOCTYPE html>`.
- **Idioma**: O documento está configurado para o português do Brasil (`lang="pt-br"`).

## Seção Head

- **Meta Tags**: Inclui configurações de conjunto de caracteres e viewport para design responsivo.
- **Título**: O título da página é "Login - CleanningMaster".
- **Folhas de Estilo**: 
  - O CSS do Bootstrap é incluído para estilização.
  - Uma folha de estilo personalizada `style.css` é vinculada para estilos adicionais.
- **Scripts**: Inclui o script do Google Sign-In para autenticação.

## Seção Body

- **Barra de Navegação**: 
  - Uma barra de navegação responsiva com links para as páginas inicial e de cadastro.
  - Inclui a marca do projeto e um botão para alternar a navegação em dispositivos móveis.

- **Formulário de Login**:
  - Contém campos para e-mail e senha, ambos obrigatórios.
  - Inclui um botão de envio para login tradicional e um botão para login com o Google.

## Scripts

- **Login com Google**: 
  - A página inclui um script para lidar com o login do Google, inicializando a API de contas do Google e renderizando um botão de login.
  - Um espaço reservado para o ID do Cliente do Google está presente, que deve ser substituído por um ID real.
  - A função `handleCredentialResponse` é usada para processar a resposta do Google.

## Uso

Esta página é projetada para autenticar usuários, seja através do login tradicional com e-mail/senha ou via login com o Google. Certifique-se de que o ID do Cliente do Google esteja configurado corretamente para que a funcionalidade de login funcione.

## Estilos Aplicados

- **Estilo do Formulário**: O formulário de login é estilizado com um fundo azul escuro, preenchimento, bordas arredondadas e sombra.
- **Título do Formulário**: O título "Login" é centralizado e estilizado com uma cor azul.

## Considerações de Segurança

- **Proteção de Dados**: Certifique-se de que as informações de login sejam transmitidas de forma segura e que o servidor esteja configurado para lidar com autenticação de forma segura.
- **Configuração do Google Sign-In**: Verifique se o ID do Cliente do Google está corretamente configurado e que o domínio está autorizado para usar o Google Sign-In. 