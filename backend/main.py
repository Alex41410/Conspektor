from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import subprocess
import os
import json
import asyncio
from pathlib import Path
from typing import Optional
import uvicorn
from processor import PDFProcessor
from lm_studio_client import LMStudioClient
import time

app = FastAPI(title="AI Summarizer Pro API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка конфигурации
CONFIG_PATH = Path("config.json")
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
        "output_dir": r"C:\Users\Alexey\Documents\conspect",
        "lm_studio_port": 1234,
        "lm_studio_url": "http://localhost:1234",
        "lm_studio_model": "local-model",
        "max_chunk_size": 15000,
        "split_keywords": [
            "Глава", "Раздел", "Тема", "Вариант", "Итог", "Введение", "Эпилог"
        ]
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Глобальное состояние
processing_state = {
    "status": "idle",  # idle, processing, completed, error
    "progress": 0,
    "current_chapter": 0,
    "total_chapters": 0,
    "preview_text": "",
    "error_message": None
}

def check_port(port: int) -> bool:
    """Проверка доступности порта"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

@app.on_event("startup")
async def startup_event():
    """Проверка доступности сервисов при старте"""
    print("Проверка доступности сервисов...")
    
    lm_available = check_port(config.get("lm_studio_port", 1234))
    
    if not lm_available:
        print(f"⚠️  LM Studio не доступен на порту {config.get('lm_studio_port', 1234)}")
        print("   Убедитесь, что LM Studio запущен и локальный сервер активен")
    else:
        print(f"✓ LM Studio доступен на порту {config.get('lm_studio_port', 1234)}")

@app.get("/")
async def root():
    return {"message": "AI Summarizer Pro API", "status": "running"}

@app.get("/status")
async def get_status():
    """Получение текущего статуса обработки"""
    return processing_state

@app.post("/check-services")
async def check_services():
    """Проверка доступности сервисов"""
    lm_available = check_port(config.get("lm_studio_port", 1234))
    
    return {
        "lm_studio": lm_available,
        "ready": lm_available
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Загрузка и обработка PDF файла"""
    global processing_state
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате PDF")
    
    try:
        # Сброс состояния
        processing_state = {
            "status": "processing",
            "progress": 0,
            "current_chapter": 0,
            "total_chapters": 0,
            "preview_text": "",
            "error_message": None
        }
        
        # Проверка сервисов
        lm_available = check_port(config.get("lm_studio_port", 1234))
        
        if not lm_available:
            processing_state["status"] = "error"
            processing_state["error_message"] = f"LM Studio не доступен на порту {config.get('lm_studio_port', 1234)}. Убедитесь, что LM Studio запущен и локальный сервер активен."
            return JSONResponse(status_code=503, content=processing_state)
        
        # Сохранение временного файла
        output_dir = Path(config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        temp_pdf_path = output_dir / file.filename
        with open(temp_pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Обработка PDF
        processor = PDFProcessor(config)
        chapters = processor.process_pdf(str(temp_pdf_path))
        
        if not chapters:
            processing_state["status"] = "error"
            processing_state["error_message"] = "Не удалось извлечь текст из PDF"
            return JSONResponse(status_code=500, content=processing_state)
        
        processing_state["total_chapters"] = len(chapters)
        
        # Запуск асинхронной обработки
        asyncio.create_task(process_chapters(chapters))
        
        return {
            "success": True,
            "message": f"Обработка начата. Найдено глав: {len(chapters)}",
            "chapters_count": len(chapters)
        }
        
    except Exception as e:
        processing_state["status"] = "error"
        processing_state["error_message"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

async def process_chapters(chapters: list):
    """Асинхронная обработка глав через LM Studio с очередью для оптимизации VRAM"""
    global processing_state
    
    output_dir = Path(config["output_dir"])
    log_file = output_dir / "generation_log.md"
    
    # Очистка лог-файла
    if log_file.exists():
        log_file.write_text("", encoding="utf-8")
    
    # Инициализация клиента LM Studio
    lm_client = LMStudioClient(
        base_url=config.get("lm_studio_url", "http://localhost:1234"),
        model_name=config.get("lm_studio_model", "local-model")
    )
    
    summaries = []
    max_chunk_size = config.get("max_chunk_size", 15000)
    
    # Очередь запросов - обрабатываем по одному для экономии VRAM
    for idx, chapter in enumerate(chapters):
        try:
            processing_state["current_chapter"] = idx + 1
            processing_state["progress"] = int((idx / len(chapters)) * 100)
            
            # Обработка главы через LM Studio
            summary = await lm_client.process_chapter(chapter, max_chunk_size)
            
            summaries.append(f"## Глава {idx + 1}\n\n{summary}\n\n")
            
            # Обновление preview
            processing_state["preview_text"] = "\n".join(summaries)
            
            # Запись в лог
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"## Глава {idx + 1}\n\n{summary}\n\n")
            
            # Задержка между запросами для снижения нагрузки на GPU
            await asyncio.sleep(0.5)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Ошибка обработки главы {idx + 1}: {error_msg}")
            summaries.append(f"## Глава {idx + 1}\n\nОшибка обработки: {error_msg}\n\n")
            
            # Запись ошибки в лог
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"## Глава {idx + 1}\n\nОшибка обработки: {error_msg}\n\n")
    
    # Сохранение финального результата
    final_text = "\n".join(summaries)
    output_file = output_dir / "summary.md"
    output_file.write_text(final_text, encoding="utf-8")
    
    processing_state["status"] = "completed"
    processing_state["progress"] = 100
    processing_state["current_chapter"] = processing_state["total_chapters"]
    processing_state["preview_text"] = final_text

@app.get("/download-docx")
async def download_docx():
    """Конвертация Markdown в DOCX через Pandoc"""
    output_dir = Path(config["output_dir"])
    md_file = output_dir / "summary.md"
    docx_file = output_dir / "summary.docx"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Файл summary.md не найден")
    
    try:
        # Конвертация через Pandoc
        result = subprocess.run(
            ["pandoc", str(md_file), "-o", str(docx_file)],
            check=True,
            capture_output=True,
            text=True
        )
        
        if docx_file.exists():
            return FileResponse(
                path=str(docx_file),
                filename="summary.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            raise HTTPException(status_code=500, detail="Ошибка конвертации")
            
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Pandoc: {e.stderr}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Pandoc не установлен")

@app.get("/config")
async def get_config():
    """Получение конфигурации"""
    return config

@app.post("/config")
async def update_config(new_config: dict):
    """Обновление конфигурации"""
    global config
    config.update(new_config)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return {"success": True, "config": config}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
