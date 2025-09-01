from pathlib import Path
from typing import TypedDict, Optional
import json

app_config_file = "django.config.json"

class DjangoConfig(TypedDict):
    name: str
    dir: str

def get_package_dir():
    return Path.cwd()

def configure_app(config: DjangoConfig | None = None):
    if not config:
        return

    # Atualiza ou cria um arquivo (app_config_file) para guardar as informações do app
    config_path = Path(app_config_file)
    
    # Se o arquivo já existe, carrega as configurações existentes
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            existing_config = {}
    
    # Atualiza com as novas configurações
    existing_config.update(config)
    
    # Salva o arquivo atualizado
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(existing_config, f, indent=2, ensure_ascii=False)

def get_config() -> Optional[DjangoConfig]:
    # Retornar a configuração do app
    config_path = Path(app_config_file)
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Valida se os campos obrigatórios estão presentes
            if 'name' in config_data and 'dir' in config_data:
                return DjangoConfig(name=config_data['name'], dir=config_data['dir'])
            else:
                return None
    except (json.JSONDecodeError, FileNotFoundError):
        return None