import inspect
from pathlib import Path
import os

def get_caller_directory():
    """
    Retorna o diretório do arquivo que chamou a função
    """
    frame = inspect.currentframe()
    try:
        # Volta 2 frames: 1 para esta função, 1 para a função chamadora
        caller_frame = frame.f_back.f_back
        caller_file = caller_frame.f_code.co_filename
        return Path(caller_file).parent.absolute()
    finally:
        del frame  # Importante para evitar vazamentos de memória

# Na sua biblioteca
base_dir = get_caller_directory()