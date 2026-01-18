"""
Клиент для работы с LM Studio API
"""
import requests
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor


class LMStudioClient:
    """Клиент для взаимодействия с LM Studio API"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = "local-model"):
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/v1/chat/completions"
        self.executor = ThreadPoolExecutor(max_workers=1)  # Один поток для экономии VRAM
    
    def generate_summary(self, text: str, system_prompt: Optional[str] = None) -> str:
        """
        Генерация конспекта для текста
        
        Args:
            text: Текст для обработки
            system_prompt: Системный промпт (опционально)
        
        Returns:
            Сгенерированный конспект
        """
        if system_prompt is None:
            system_prompt = (
                "Ты помощник для создания конспектов. "
                "Создай краткий, структурированный конспект предоставленного текста, "
                "выделяя основные идеи и ключевые моменты. "
                "Используй маркированные списки и четкую структуру."
            )
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=300,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception("Неожиданный формат ответа от LM Studio")
            else:
                raise Exception(f"Ошибка LM Studio API: {response.status_code} - {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            raise Exception("Превышено время ожидания ответа от LM Studio")
        except requests.exceptions.ConnectionError:
            raise Exception("Не удалось подключиться к LM Studio. Убедитесь, что сервер запущен.")
        except Exception as e:
            raise Exception(f"Ошибка при запросе к LM Studio: {str(e)}")
    
    async def generate_summary_async(self, text: str, system_prompt: Optional[str] = None) -> str:
        """
        Асинхронная генерация конспекта
        
        Args:
            text: Текст для обработки
            system_prompt: Системный промпт (опционально)
        
        Returns:
            Сгенерированный конспект
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.generate_summary,
            text,
            system_prompt
        )
    
    def split_into_chunks(self, text: str, max_chunk_size: int = 15000) -> List[str]:
        """
        Разбиение текста на чанки для обработки
        
        Args:
            text: Исходный текст
            max_chunk_size: Максимальный размер чанка в символах
        
        Returns:
            Список чанков
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        i = 0
        
        while i < len(text):
            chunk_end = min(i + max_chunk_size, len(text))
            chunk = text[i:chunk_end]
            
            # Пытаемся разбить по предложениям, чтобы не обрезать текст посередине
            if chunk_end < len(text):
                # Ищем последнюю точку, восклицательный или вопросительный знак
                last_sentence_end = max(
                    chunk.rfind('.'),
                    chunk.rfind('!'),
                    chunk.rfind('?'),
                    chunk.rfind('\n')  # Также учитываем переносы строк
                )
                # Если нашли в последних 30% чанка, используем это место для разбиения
                if last_sentence_end > max_chunk_size * 0.7:
                    chunk = chunk[:last_sentence_end + 1]
                    i += last_sentence_end + 1
                else:
                    i = chunk_end
            else:
                i = chunk_end
            
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    async def process_chapter(self, chapter_text: str, max_chunk_size: int = 15000) -> str:
        """
        Обработка главы: разбиение на чанки и генерация конспекта
        
        Args:
            chapter_text: Текст главы
            max_chunk_size: Максимальный размер чанка
        
        Returns:
            Объединенный конспект главы
        """
        # Разбиваем на чанки если текст слишком большой
        if len(chapter_text) > max_chunk_size:
            chunks = self.split_into_chunks(chapter_text, max_chunk_size)
            summaries = []
            
            for idx, chunk in enumerate(chunks):
                try:
                    summary = await self.generate_summary_async(chunk)
                    summaries.append(summary)
                    # Небольшая задержка между чанками для экономии VRAM
                    await asyncio.sleep(0.5)
                except Exception as e:
                    summaries.append(f"[Ошибка обработки чанка {idx + 1}: {str(e)}]")
            
            # Объединяем все конспекты чанков
            return "\n\n".join(summaries)
        else:
            # Если текст помещается в один чанк, обрабатываем сразу
            return await self.generate_summary_async(chapter_text)
