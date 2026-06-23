import os
from src.lib.logger import log_error  # pyrefly: ignore [missing-import]

# Carrega o arquivo .env manualmente
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

if os.path.exists(dotenv_path):
    try:
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    val = val.strip().strip('\'"')
                    os.environ.setdefault(key.strip(), val)
    except Exception as e:
        # Registra erros de ficheiro no log
        log_error(f"Erro de ficheiro ao ler o arquivo .env em {dotenv_path}", e)

# Validação e Conversão de TAX_IVA (Erro de Conversão / Campo Vazio)
tax_iva_env = os.environ.get('TAX_IVA')
if tax_iva_env is None:
    log_error("Variável de ambiente TAX_IVA ausente. Usando valor padrão 0.14 (14%).")
    TAX_RATE = 0.14
else:
    try:
        TAX_RATE = float(tax_iva_env.replace(',', '.'))
    except ValueError as e:
        log_error(f"Erro de conversão na variável TAX_IVA ('{tax_iva_env}'). Definindo valor padrão 0.14 (14%).", e)
        TAX_RATE = 0.14

# Validação de SECRET_KEY (Campo Vazio)
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    log_error("Variável de ambiente SECRET_KEY ausente. Usando chave de segurança padrão temporária.")
    SECRET_KEY = "chave-secreta-padrao-temporaria"