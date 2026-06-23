# Sistema de Faturação Profissional - FaturaPro

> Aplicação de faturação local construída com Flask, SQLite, HTML5, CSS3 e JavaScript.

---

## 📂 Estrutura do projeto

- `app.py` - Configuração da aplicação Flask e rotas.
- `database.py` - Inicialização do SQLite/SQLAlchemy.
- `models.py` - Definição dos modelos de dados (usuários, produtos, clientes, vendas, itens, categorias, pagamento).
- `db_init.py` - Cria o banco e insere dados iniciais.
- `requirements.txt` - Dependências Python.
- `README.md` - Instruções para executar o projeto.
- `templates/` - Páginas HTML Jinja2.
- `static/css/` - Estilos personalizados.
- `static/js/` - JavaScript do frontend.
- `static/img/` - Imagem/logo do sistema.
- `database/` - Arquivo SQLite `app.db`.
- `backup/` - Pasta para futuros backups.

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
python db_init.py
```

---

## 🚀 Executar a aplicação

```bash
python app.py
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
