# 🎫 Sistema HelpDesk - Azuma

Bem-vindo ao repositório do **Azuma**, um sistema moderno e responsivo de HelpDesk para abertura e gestão de chamados de suporte técnico. 

Este projeto foi desenvolvido como entrega da **AC1**, focando na integração completa entre Front-end, Back-end e um Banco de Dados Relacional hospedado em nuvem.

## Funcionalidades Principais (Entrega AC1)

* **Abertura de Tickets:** Formulário dinâmico para criação de chamados com categorias, prioridades e mesas.
* **Leitura e Listagem:** Dashboard inicial que consome os dados do banco na nuvem e lista os chamados abertos.
* **Gestão de Status e Encerramento:** Controle de fluxo do chamado permitindo a atualização do status para "Concluído".
* **Filtros Dinâmicos:** Busca por empresa e organização por status.

## Novas Funcionalidades (Entrega AC2)

* **Edição e Atualização (Update):** Modal interativo que permite aos operadores alterar dados de chamados já existentes (como prioridade, categoria e mesa) com reflexo imediato no banco de dados.
* **Cronômetro de Atendimento:** Lógica de "Play/Pause" integrada ao back-end para registrar o tempo exato trabalhado no ticket, alterando o status automaticamente para "Em Andamento".
* **Dashboard de Indicadores:** Painel superior com contadores em tempo real, realizando consultas no banco para exibir o volume de chamados Abertos, Em Andamento e Concluídos.
* **Métricas de SLA:** Cálculo e exibição do Tempo Médio de Resolução da equipe com base no histórico de chamados finalizados.


## Tecnologias Utilizadas

**Front-end:**
* HTML5, CSS3 e JavaScript
* [Bootstrap](https://getbootstrap.com/) (Para modais, cards e responsividade)

**Back-end:**
* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) (Micro-framework web)
* Flask-SQLAlchemy (ORM para modelagem e comunicação com o banco de dados)
* Dotenv (Gerenciamento seguro de variáveis de ambiente)

**Banco de Dados:**
* **PostgreSQL** (Hospedado na nuvem via [Neon.tech](https://neon.tech/))

## Como executar o projeto localmente

Para rodar este projeto na sua máquina, siga os passos abaixo:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/juliocoelho-imp/Projeto-Azuma.git](https://github.com/juliocoelho-imp/Projeto-Azuma.git)
