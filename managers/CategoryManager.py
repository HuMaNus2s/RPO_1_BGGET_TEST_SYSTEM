from pathlib import Path
from typing import List, Dict
import json

from config.config import DATA_PATH
from config.log_config import logger
from classes.Category import Category

class CategoryManager:
    def __init__(self, data_path: str = DATA_PATH):
        self.data_path = Path(data_path)
        self.categories: List[Category] = []

    def get_all_category_files(self) -> List[str]:
        if not self.data_path.exists():
            logger.warning(f"Директория {self.data_path} не существует")
            return []
        
        files = [f.name for f in self.data_path.iterdir() 
                 if f.is_file() and f.suffix == '.json']
        return files

    def load_all_categories(self) -> List[Category]:
        self.categories = []
        files = self.get_all_category_files()
        
        for filename in files:
            category_name = filename.replace('.json', '').replace('_', ' ')

            temp_category = Category(name=category_name)
            category = temp_category.loadFromFile()
            
            if category:
                self.categories.append(category)
                logger.info(f"Загружена категория: {category.name}")
            else:
                logger.warning(f"Не удалось загрузить категорию из {filename}")
        
        return self.categories

    def get_all_categories_data(self) -> Dict:
        if not self.categories:
            self.load_all_categories()
        
        categories_data = []
        total_points = 0
        
        for category in self.categories:
            cat_data = category.toJSON
            categories_data.append(cat_data)
            total_points += cat_data.get('points', 0)
        
        return {
            'categories': categories_data,
            'total_categories': len(categories_data),
            'total_points': total_points
        }

    def get_categories_list(self) -> List[str]:
        files = self.get_all_category_files()
        return [f.replace('.json', '').replace('_', ' ') for f in files]