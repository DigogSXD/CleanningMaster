# Documentação do Arquivo de Estilos CSS

## Visão Geral

O arquivo `styles.css` contém as definições de estilo personalizadas para o projeto CleanningMaster. Ele complementa o CSS do Bootstrap para fornecer uma aparência consistente e personalizada.

## Estilos Definidos

- **Texto Justificado**: 
  - Todos os parágrafos (`<p>`) são justificados para melhorar a legibilidade.
  - Elementos dentro de `.md-content__inner .md-typeset` são justificados, exceto onde especificamente centralizados.

- **Centralização de Elementos**: 
  - A classe `.centralizado` pode ser aplicada a elementos que precisam ser centralizados.

- **Ajuste de Títulos**: 
  - Os títulos (`<h1>` a `<h6>`) são alinhados à esquerda por padrão.

- **Imagens Centralizadas**: 
  - A classe `.center-image` é usada para centralizar imagens horizontalmente.

## Uso

Estes estilos são aplicados em conjunto com o Bootstrap para garantir que o design do site seja responsivo e esteticamente agradável. A personalização permite que o projeto mantenha uma identidade visual única.

## Documentação Linha por Linha do styles.css

1. **Linha 1-3**: Define que todos os parágrafos (`<p>`) terão o texto justificado.

2. **Linha 6-8**: Aplica justificação de texto a elementos dentro de `.md-content__inner .md-typeset`, exceto aqueles com a classe `.centralizado`.

3. **Linha 11-13**: Define a classe `.centralizado` para centralizar elementos específicos.

4. **Linha 16-24**: Ajusta o alinhamento dos títulos (`<h1>` a `<h6>`) para a esquerda dentro de `.md-content__inner .md-typeset`.

5. **Linha 27-30**: Define a classe `.center-image` para centralizar imagens horizontalmente, definindo `display: block` e ajustando as margens para `auto`.

6. **Linha 1-4**: Define o estilo do `body` com um fundo azul escuro, texto branco e fonte Arial.

7. **Linha 6-8**: Estiliza a `navbar` e o `footer` com um fundo azul escuro e texto branco.

8. **Linha 10-12**: Define a cor dos links de navegação e da marca da `navbar` como azul claro.

9. **Linha 14-17**: Altera a cor dos links de navegação e da marca da `navbar` ao passar o mouse, com uma transição suave.

10. **Linha 18-20**: Define o estilo específico para a `navbar-index` com fundo azul escuro e texto branco.

11. **Linha 22-25**: Estiliza o botão primário com um fundo vermelho e borda vermelha.

12. **Linha 27-30**: Altera a cor do botão primário ao passar o mouse para um vermelho mais escuro.

13. **Linha 32-33**: Define a cor dos títulos `h1` e `h2` como branco.

14. **Linha 35-36**: Adiciona margem superior ao `container`.

15. **Linha 38-41**: Estiliza o título de login com tamanho de fonte grande, cor azul e margem inferior.

16. **Linha 43-48**: Define o estilo do formulário de login com fundo azul escuro, preenchimento, bordas arredondadas e sombra. 