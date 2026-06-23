import os
import sys
import traceback
from datetime import datetime

# Caminho para a pasta de logs no diretório raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'errors.txt')

def log_error(message, exception=None):
    """
    Grava um log de erro no arquivo logs/errors.txt com data, rota ativa e detalhes.
    Se ocorrer um erro de escrita (erro de ficheiro/permissão), fallback para stderr.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    request_info = ""
    
    try:
        from flask import request, has_request_context
        if has_request_context():
            request_info = f" | Rota: {request.method} {request.url} | IP: {request.remote_addr}"
    except ImportError:
        pass
        
    log_entry = f"[{timestamp}]{request_info}\nErro: {message}\n"
    
    if exception:
        tb_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        log_entry += f"Pilha de Rastreamento (Traceback):\n{tb_str}"
        
    log_entry += "-" * 80 + "\n"
    
    try:
        # Garante a criação da pasta logs/
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR, exist_ok=True)
            
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        # Em caso de erro de ficheiro na gravação do log, direciona ao stderr do sistema
        sys.stderr.write(f"[{timestamp}] ERRO DE FICHEIRO: Não foi possível gravar o log em disco: {e}\n")
        sys.stderr.write(log_entry)
        sys.stderr.flush()
