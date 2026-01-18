import React, { useCallback, useState } from 'react'
import { Upload, FileText } from 'lucide-react'

function DragDropZone({ onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    const pdfFile = files.find(file => file.name.endsWith('.pdf'))
    
    if (pdfFile) {
      onFileSelect(pdfFile)
    } else {
      alert('Пожалуйста, выберите PDF файл')
    }
  }, [onFileSelect])

  const handleFileInput = useCallback((e) => {
    const file = e.target.files[0]
    if (file) {
      onFileSelect(file)
    }
  }, [onFileSelect])

  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-12 transition-all ${
        isDragging
          ? 'border-deep-sea-400 bg-deep-sea-700/50 scale-105'
          : 'border-deep-sea-600 bg-deep-sea-800/30 hover:border-deep-sea-500 hover:bg-deep-sea-800/50'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="hidden"
        id="file-input"
      />
      <label
        htmlFor="file-input"
        className="flex flex-col items-center justify-center cursor-pointer"
      >
        <div className={`mb-4 transition-transform ${isDragging ? 'scale-110' : ''}`}>
          {isDragging ? (
            <Upload className="w-16 h-16 text-deep-sea-400" />
          ) : (
            <FileText className="w-16 h-16 text-deep-sea-500" />
          )}
        </div>
        <p className="text-xl font-semibold text-deep-sea-200 mb-2">
          {isDragging ? 'Отпустите файл здесь' : 'Перетащите PDF файл сюда'}
        </p>
        <p className="text-deep-sea-400 text-sm">
          или нажмите для выбора файла
        </p>
      </label>
    </div>
  )
}

export default DragDropZone
