import inspect
from pathlib import Path
import os

def get_project_path():
    """
    Retorna o caminho do projeto Django ou do chamador
    """
    try:
        # Primeiro tenta usar o Django
        from django.conf import settings
        return Path(settings.BASE_DIR)
    except (ImportError, AttributeError):
        # Fallback: usa o caminho do chamador
        frame = inspect.currentframe()
        try:
            # Procura o frame que não é da biblioteca
            for depth in range(2, 10):  # Procura até 10 frames acima
                caller_frame = frame
                for _ in range(depth):
                    caller_frame = caller_frame.f_back
                    if caller_frame is None:
                        break
                
                if caller_frame and 'site-packages' not in caller_frame.f_code.co_filename:
                    caller_file = caller_frame.f_code.co_filename
                    caller_path = Path(caller_file).parent.absolute()
                    
                    # Tenta encontrar manage.py ou estrutura Django
                    for parent in [caller_path] + list(caller_path.parents):
                        if (parent / 'manage.py').exists():
                            return parent
                    
                    return caller_path
        finally:
            del frame
    
    # Último recurso: diretório atual
    return Path.cwd()