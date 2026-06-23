import os

# Carrega o arquivo .env manualmente
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
if os.path.exists(dotenv_path):
    with open(dotenv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('\'"')
                os.environ.setdefault(key.strip(), val)

TAX_RATE = float(os.environ.get('TAX_IVA'))
SECRET_KEY = os.environ.get('SECRET_KEY')