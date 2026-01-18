import pdfplumber
import re
from pathlib import Path
from typing import List
import json

class PDFProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path(config["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Стоп-слова для определения мусорных фрагментов
        self.stop_words = [
            "оглавление", "содержание", "contents", "table of contents",
            "введение", "предисловие", "preface", "introduction"
        ]
        
        # Регулярное выражение для нарезки на главы
        # Используем ключевые слова из конфига, если они есть
        keywords = config.get("split_keywords", [
            "Вариант", "Глава", "Раздел", "Итог", "Тема", "Введение", "Эпилог"
        ])
        keywords_pattern = "|".join(keywords)
        self.chapter_pattern = re.compile(
            rf'\n\s*(?=(?:\d+[\.\s-]*)?(?:{keywords_pattern}|#{1,3}\s))',
            re.IGNORECASE | re.MULTILINE
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Извлечение текста из PDF"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Ошибка извлечения текста из PDF: {e}")
        
        return text
    
    def is_junk_fragment(self, text: str) -> bool:
        """Проверка, является ли фрагмент мусорным (оглавление и т.д.)"""
        text_lower = text.lower()
        
        # Проверка на стоп-слова
        for stop_word in self.stop_words:
            if stop_word in text_lower[:200]:  # Проверяем начало текста
                return True
        
        # Проверка на высокую плотность точек (эффект оглавления)
        if len(text) > 100:
            dot_density = text.count('.') / len(text)
            if dot_density > 0.1:  # Более 10% точек - вероятно оглавление
                # Но проверяем, что это не обычный текст с аббревиатурами
                lines = text.split('\n')
                if len(lines) > 5:
                    avg_line_length = sum(len(line.strip()) for line in lines[:10]) / min(10, len(lines))
                    if avg_line_length < 50:  # Короткие строки - вероятно оглавление
                        return True
        
        return False
    
    def split_into_chapters(self, text: str) -> List[str]:
        """Умная нарезка текста на главы"""
        # Разделение по паттерну
        chapters = self.chapter_pattern.split(text)
        
        # Фильтрация пустых и мусорных фрагментов
        filtered_chapters = []
        for chapter in chapters:
            chapter = chapter.strip()
            if len(chapter) < 100:  # Игнорируем слишком короткие фрагменты
                continue
            
            if self.is_junk_fragment(chapter):
                continue
            
            filtered_chapters.append(chapter)
        
        # Если не найдено глав по паттерну, разбиваем на равные части
        if not filtered_chapters:
            # Разбиваем на части по ~15000 символов
            chunk_size = self.config.get("max_chunk_size", 15000)
            filtered_chapters = [
                text[i:i + chunk_size] 
                for i in range(0, len(text), chunk_size)
                if len(text[i:i + chunk_size].strip()) > 100
            ]
        
        return filtered_chapters
    
    def process_pdf(self, pdf_path: str) -> List[str]:
        """Основной метод обработки PDF"""
        # Извлечение текста
        print(f"Извлечение текста из {pdf_path}...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            raise Exception("Не удалось извлечь текст из PDF или текст слишком короткий")
        
        # Сохранение исходного текста
        source_text_path = self.output_dir / "source_text.txt"
        source_text_path.write_text(text, encoding="utf-8")
        print(f"Исходный текст сохранен в {source_text_path}")
        
        # Нарезка на главы
        print("Нарезка текста на главы...")
        chapters = self.split_into_chapters(text)
        
        print(f"Найдено глав: {len(chapters)}")
        
        # Сохранение информации о главах
        chapters_info = {
            "total_chapters": len(chapters),
            "chapters_lengths": [len(ch) for ch in chapters]
        }
        info_path = self.output_dir / "chapters_info.json"
        info_path.write_text(json.dumps(chapters_info, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return chapters
