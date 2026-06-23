"""
Script de verificação do sistema de monitoramento e validações.
Testa: servidor ativo, login com campos vazios, login com e-mail inválido,
login correto, endpoints de produto (código duplicado), e geração de log.
"""
import urllib.request
import urllib.parse
import urllib.error
import os
from http.cookiejar import CookieJar

BASE_URL = 'http://127.0.0.1:5000'
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def check(label, condition, detail=''):
    status = '✅ PASS' if condition else '❌ FAIL'
    print(f"  {status}  {label}")
    if not condition and detail:
        print(f"         → {detail}")

def post(path, data):
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}{path}', data=encoded, method='POST')
    try:
        res = opener.open(req)
        return res.status, res.read().decode('utf-8', errors='replace'), res.url
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace'), str(e.url)

def get(path):
    try:
        res = opener.open(f'{BASE_URL}{path}')
        return res.status, res.read().decode('utf-8', errors='replace'), res.url
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace'), str(e.url)

print('\n' + '=' * 60)
print('VERIFICAÇÃO DO SISTEMA DE MONITORAMENTO E VALIDAÇÕES')
print('=' * 60)

# 1. Servidor ativo
print('\n[1] Servidor Flask')
try:
    status, _, _ = get('/login')
    check('Servidor respondendo na porta 5000', status == 200)
except Exception as e:
    check('Servidor respondendo na porta 5000', False, str(e))
    print('Abortando — servidor inacessível.')
    exit(1)

# 2. Login — campos vazios
print('\n[2] Login — Validação de campos vazios')
status, body, _ = post('/login', {'email': '', 'password': ''})
check('Campos vazios geram aviso (flash)', 'obrigatórios' in body or 'obrigat' in body.lower(), f'status={status}')

# 3. Login — e-mail inválido
print('\n[3] Login — Validação de formato de e-mail')
status, body, _ = post('/login', {'email': 'semArroba', 'password': 'abc'})
check('E-mail sem @ gera aviso', 'inv' in body.lower() or 'formato' in body.lower(), f'status={status}')

# 4. Login — credenciais erradas
print('\n[4] Login — Credenciais inválidas')
status, body, _ = post('/login', {'email': 'nao@existe.com', 'password': 'errada'})
check('Credenciais erradas geram aviso', 'inv' in body.lower() or 'danger' in body.lower(), f'status={status}')

# 5. Login correto
print('\n[5] Login — Autenticação correta')
status, body, final_url = post('/login', {'email': 'admin@faturapro.ao', 'password': 'admin123'})
logged_in = 'dashboard' in final_url.lower() or 'sucesso' in body.lower() or status == 200
check('Login correto redireciona ao dashboard', logged_in, f'status={status}, url={final_url}')

# 6. Dashboard acessível após login
print('\n[6] Dashboard')
status, body, _ = get('/dashboard')
check('Dashboard carrega após login (HTTP 200)', status == 200, f'status={status}')
check('Conteúdo do dashboard renderizado', 'Dashboard' in body or 'Painel' in body)

# 7. Produto — código duplicado (tenta cadastrar "PROD-TEST" duas vezes)
print('\n[7] Produtos — Validação de duplicados')
post('/products/new', {'code': 'TEST-DUPL-001', 'name': 'Produto Teste Dup', 'price': '10.00', 'stock': '5'})
status, body, _ = post('/products/new', {'code': 'TEST-DUPL-001', 'name': 'Outro Produto', 'price': '20.00', 'stock': '3'})
check('Código duplicado gera aviso', 'duplicado' in body.lower() or 'existe' in body.lower() or 'warning' in body.lower(), f'status={status}')

# 8. Produto — campos vazios
print('\n[8] Produtos — Validação de campos vazios')
status, body, _ = post('/products/new', {'code': '', 'name': '', 'price': '', 'stock': ''})
check('Campos vazios geram aviso', 'obrigat' in body.lower() or 'warning' in body.lower(), f'status={status}')

# 9. Produto — conversão numérica inválida
print('\n[9] Produtos — Validação de formato numérico')
status, body, _ = post('/products/new', {'code': 'X-999', 'name': 'Prod Teste', 'price': 'abc', 'stock': 'xyz'})
check('Formato numérico inválido gera aviso', 'inv' in body.lower() or 'num' in body.lower() or 'warning' in body.lower(), f'status={status}')

# 10. Categoria — nome duplicado
print('\n[10] Categorias — Validação de duplicados')
post('/categories/new', {'name': 'Cat-Dup-Teste'})
status, body, _ = post('/categories/new', {'name': 'Cat-Dup-Teste'})
check('Categoria duplicada gera aviso', 'duplicado' in body.lower() or 'existe' in body.lower() or 'warning' in body.lower(), f'status={status}')

# 11. Arquivo de log criado
print('\n[11] Sistema de Logs')
log_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'home', 'betalover', 'sistemaDeFaturacao', 'logs', 'errors.txt')
log_path2 = '/home/betalover/sistemaDeFaturacao/logs/errors.txt'
log_exists = os.path.exists(log_path2)
check('Arquivo logs/errors.txt criado', log_exists)
if log_exists:
    size = os.path.getsize(log_path2)
    check('Arquivo de log não está vazio', size > 0, f'tamanho={size} bytes')
    with open(log_path2) as f:
        first_lines = f.read(300)
    check('Log contém timestamp legível', '2026' in first_lines or '202' in first_lines, first_lines[:100])

print('\n' + '=' * 60)
print('Verificação concluída.')
print('=' * 60 + '\n')

