# Sistema de Faturação Profissional - FaturaPro

> Aplicação de faturação local construída com Flask, SQLite, HTML5, CSS3 e JavaScript.

---

## 📂 Estrutura do projeto

O projeto foi reestruturado de forma modular e segue a seguinte organização:

- `main.py` - Ponto de entrada do aplicativo Flask (com a fábrica de aplicação `create_app`).
- `pyproject.toml` / `uv.lock` - Configurações do projeto e de dependências gerenciadas via `uv`.
- `.env` / `.env.example` - Configurações de variáveis de ambiente.
- `src/` - Código-fonte principal da aplicação:
  - `database/` - Configuração e modelos de persistência de dados:
    - `config/database.py` - Configuração e inicialização do banco de dados SQLite/SQLAlchemy.
    - `data/` - Pasta contendo o banco de dados local (`app.db`).
    - `models/models.py` - Definições das entidades de banco de dados (User, Customer, Product, etc.).
    - `scripts/db_init.py` - Script executável para inicializar o banco de dados com dados fictícios de exemplo.
  - `routes/` - Controladores da aplicação modularizados com Flask Blueprints:
    - `__init__.py` - Arquivo agregador dos Blueprints das rotas.
    - `auth.py` - Rotas de autenticação (login, logout).
    - `dashboard.py` - Rotas do painel administrativo.
    - `products.py` - Rotas de gestão de produtos.
    - `category.py` - Rotas de gestão de categorias.
    - `customer.py` - Rotas de gestão de clientes.
    - `sales.py` - Rotas do PDV (nova venda, carrinho, finalização e histórico).
    - `reports.py` - Rotas de relatórios e estatísticas.
    - `api.py` - Endpoints de APIs internas (como busca rápida de produtos).
  - `services/` - Camada de regras de negócio:
    - `cart/cart.py` - Utilitários de carrinho e cálculos de venda.
  - `lib/` - Bibliotecas utilitárias e ajudantes compartilhados:
    - `env.py` - Leitor seguro das variáveis de ambiente.
    - `login_required.py` - Decorator de controle de acesso a rotas.
  - `templates/` - Páginas Jinja2 HTML.
  - `static/` - Arquivos estáticos estruturados (css, js, imagens).

--- 

## 🧰 Requisitos

- Python 3.10+

---

## 🔧 Instalação de dependências


#### Instalar o gerenciador de pacotes uv

```bash
 `curl -LsSf https://astral.sh/get-uv | bash` - Linux
```

#### Instalar as dependências
```bash
uv sync
```
---

## 🏁 Inicializar a base de dados

```bash
python -m src.database.scripts.db_init
```

---

## 🚀 Executar a aplicação

```bash
python main.py
```

Abra no navegador:

```bash
http://127.0.0.1:5000/
```

--- 

## 🔑 Login inicial

- E-mail: `admin@faturapro.ao`
- Senha: `admin123`

--- 

## ✨ Funcionalidades implementadas

- Login de usuários com senha criptografada.
- Dashboard com total de vendas, clientes, produtos, vendas do dia e estoque baixo.
- Cadastro, edição, exclusão e pesquisa de clientes.
- Cadastro, edição, exclusão e pesquisa de produtos.
- Gestão de categorias de produtos.
- Sistema de vendas com carrinho, alteração de quantidade e remoção de itens.
- Cálculo automático de subtotal, desconto, IVA e total em Kz.
- Vendas associadas a cliente, vendedor e forma de pagamento.
- Emissão de fatura com dados completos e impressão/salvamento em PDF via navegador.
- Histórico de vendas com filtro por número, cliente e data.
- Relatórios diários, mensais, produtos mais vendidos, clientes que mais compram e estoque baixo.

---

## 📌 Como testar todas as funcionalidades

1. Inicie a aplicação e acesse `http://127.0.0.1:5000/`.
2. Entre com o usuário administrador.
3. Acesse o dashboard para ver métricas e últimas vendas.
4. Vá para **Produtos** para criar, editar e excluir itens.
5. Vá para **Clientes** para cadastrar, pesquisar e editar clientes.
6. Crie categorias em **Categorias**.
7. Abra **Nova Venda**, adicione produtos ao carrinho, escolha cliente e forma de pagamento e finalize.
8. Em **Histórico de Vendas** veja as faturas geradas e abra cada fatura.
9. Em **Relatórios** confira os principais indicadores do sistema.~

--- 

## Observações

- A aplicação usa SQLite em `database/app.db`.
- Todo dado é persistido localmente e o sistema é adequado para projetos acadêmicos.
- Caso queira suportar exportação de PDF no servidor, é possível adicionar bibliotecas como WeasyPrint.
