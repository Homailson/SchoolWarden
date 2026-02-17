# 🏫 SchoolWarden

Sistema web para gestão e análise de ocorrências escolares, com
dashboards interativos para gestores, professores e acompanhamento pelos
alunos.

------------------------------------------------------------------------

## 🎯 Objetivo

O **SchoolWarden** foi desenvolvido para resolver um problema real do
ambiente escolar:

-   Centralizar o registro de ocorrências disciplinares\
-   Permitir acompanhamento estruturado por turma, professor e
    disciplina\
-   Gerar dashboards estratégicos para apoio à gestão escolar\
-   Fornecer transparência aos alunos sobre seus registros

Projeto idealizado para aplicação prática em ambiente escolar,
conectando gestão e análise de dados.

------------------------------------------------------------------------

## 🏗️ Arquitetura

Aplicação fullstack desenvolvida em Python com integração entre backend,
banco de dados e camada analítica.

### Stack Principal

-   **Flask** → Backend, autenticação e controle de sessão\
-   **MongoDB** → Banco NoSQL para armazenamento das ocorrências\
-   **Dash + Plotly** → Dashboards interativos\
-   **Bootstrap** → Estilização\
-   **Gunicorn** → Servidor WSGI para deploy\
-   **Render.com** → Deploy em Cloud

------------------------------------------------------------------------

### 🔄 Fluxo da Aplicação

1.  Professores registram ocorrências\
2.  Dados são armazenados no MongoDB\
3.  Dash consome os dados via Aggregation Pipeline\
4.  Gestores visualizam dashboards atualizados automaticamente

------------------------------------------------------------------------

## 📊 Dashboards Implementados

✔ Total de ocorrências por tipo\
✔ Ocorrências por turma e classificação\
✔ Ocorrências por disciplina\
✔ Ocorrências por professor

Os dashboards utilizam:

-   MongoDB Aggregation Pipeline\
-   Agrupamentos com `$group`\
-   Relacionamentos com `$lookup`\
-   Expansões com `$unwind`\
-   Ordenações com `$sort`\
-   Limitação de resultados com `$limit`\
-   Atualização automática com `dcc.Interval`

------------------------------------------------------------------------

## 🧠 Conceitos Técnicos Aplicados

-   Modelagem de dados em MongoDB\
-   Uso de Aggregation Pipeline para análises\
-   Integração Flask + Dash no mesmo servidor\
-   Construção de gráficos dinâmicos com Plotly\
-   Organização modular da aplicação\
-   Controle de sessão com tempo configurável\
-   Deploy configurado via variáveis de ambiente\
-   Estrutura preparada para ambiente cloud

------------------------------------------------------------------------

## 🛠️ Tecnologias Utilizadas

-   Python\
-   Flask\
-   Flask-PyMongo\
-   Flask-WTF\
-   Dash\
-   Dash Bootstrap Components\
-   Plotly\
-   Pandas\
-   MongoDB\
-   Gunicorn\
-   ReportLab

------------------------------------------------------------------------

## 📂 Estrutura do Projeto

    SchoolWarden/
    │
    ├── config.py
    ├── dash_app.py
    ├── run.py
    ├── requirements.txt
    ├── .gitignore
    └── app/

------------------------------------------------------------------------

## 🔐 Variáveis de Ambiente

Para execução correta, é necessário configurar:

-   `MONGO_URI`\
-   `SECRET_KEY`\
-   `MAIL_USERNAME`\
-   `MAIL_PASSWORD`

------------------------------------------------------------------------

## 🚀 Executando Localmente

1.  Clone o repositório:
    -   `git clone <repo-url>`
    -   `cd SchoolWarden`
2.  Instale as dependências:
    -   `pip install -r requirements.txt`
3.  Rode a aplicação:
    -   `python run.py`

A aplicação inicia em: - `http://127.0.0.1:5000`

------------------------------------------------------------------------

## 🌎 Deploy

Projeto preparado para deploy no Render.com utilizando:

-   Gunicorn\
-   Variáveis de ambiente\
-   MongoDB remoto\
-   Configuração separada por ambiente

------------------------------------------------------------------------

## 📈 Diferenciais do Projeto

Este não é um projeto acadêmico.

Foi desenvolvido com foco em aplicação real em ambiente escolar,
integrando:

-   Gestão educacional\
-   Modelagem de dados\
-   Visualização analítica\
-   Impacto social\
-   Tomada de decisão baseada em dados

------------------------------------------------------------------------

## 🔮 Melhorias Futuras

-   Controle de acesso por perfil mais granular\
-   Otimização de consultas MongoDB com índices\
-   Cache para dashboards\
-   Exportação de relatórios analíticos\
-   Monitoramento e logging estruturado

------------------------------------------------------------------------

## 👨‍💻 Autor

**Homailson Lopes**\
Data Engineer \| Professor de Matemática\
AWS Certified\
Mestre em Ciências -- USP

Conectando Educação, Dados e Tecnologia.
