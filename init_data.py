import os
import shutil
from pathlib import Path

def init_data():
    """Копирует данные из репозитория в рабочую директорию"""
    
    # Источник (репозиторий)
    repo_data = Path(__file__).parent / 'data'
    
    # Назначение (рабочая директория)
    if os.environ.get('RENDER') == 'true':
        work_data = Path('/data')
    else:
        work_data = Path(__file__).parent / 'data'
    
    work_data.mkdir(parents=True, exist_ok=True)
    
    # Копируем файлы
    if repo_data.exists():
        # Копируем users
        users_src = repo_data / 'users'
        users_dst = work_data / 'users'
        if users_src.exists():
            shutil.copytree(users_src, users_dst, dirs_exist_ok=True)
            print(f"✅ Скопированы пользователи: {users_dst}")
        
        # Копируем JSON категории
        for json_file in repo_data.glob('*.json'):
            if json_file.name != '.gitkeep':  # пропускаем служебные файлы
                shutil.copy2(json_file, work_data / json_file.name)
                print(f"✅ Скопирован файл: {json_file.name}")
    else:
        print(f"⚠️ Папка data не найдена: {repo_data}")

if __name__ == '__main__':
    init_data()