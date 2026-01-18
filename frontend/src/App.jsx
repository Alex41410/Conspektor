import React, { useState, useEffect, useCallback } from 'react'
import { Upload, Settings, Download, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import DragDropZone from './components/DragDropZone'
import ProgressBar from './components/ProgressBar'
import SettingsPanel from './components/SettingsPanel'
import LivePreview from './components/LivePreview'

const API_URL = 'http://localhost:8000'

function App() {
  const [status, setStatus] = useState('idle') // idle, processing, completed, error
  const [progress, setProgress] = useState(0)
  const [currentChapter, setCurrentChapter] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [previewText, setPreviewText] = useState('')
  const [errorMessage, setErrorMessage] = useState(null)
  const [servicesReady, setServicesReady] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [config, setConfig] = useState(null)

  // Проверка статуса каждую секунду
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/status`)
        const data = response.data
        
        setStatus(data.status)
        setProgress(data.progress || 0)
        setCurrentChapter(data.current_chapter || 0)
        setTotalChapters(data.total_chapters || 0)
        setPreviewText(data.preview_text || '')
        setErrorMessage(data.error_message)
      } catch (error) {
        console.error('Ошибка получения статуса:', error)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  // Проверка сервисов при загрузке
  useEffect(() => {
    checkServices()
    loadConfig()
  }, [])

  const checkServices = async () => {
    try {
      const response = await axios.post(`${API_URL}/check-services`)
      setServicesReady(response.data.ready)
    } catch (error) {
      console.error('Ошибка проверки сервисов:', error)
      setServicesReady(false)
    }
  }

  const loadConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/config`)
      setConfig(response.data)
    } catch (error) {
      console.error('Ошибка загрузки конфигурации:', error)
    }
  }

  const handleFileUpload = async (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Пожалуйста, выберите PDF файл')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      setStatus('processing')
      setProgress(0)
      setErrorMessage(null)
      
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        setTotalChapters(response.data.chapters_count)
      }
    } catch (error) {
      setStatus('error')
      setErrorMessage(error.response?.data?.detail || error.message)
    }
  }

  const handleDownloadDocx = async () => {
    try {
      const response = await axios.get(`${API_URL}/download-docx`, {
        responseType: 'blob'
      })
      
      // Создание ссылки для скачивания
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'summary.docx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Ошибка скачивания файла: ' + (error.response?.data?.detail || error.message))
    }
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-deep-sea-900 via-deep-sea-800 to-deep-sea-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-deep-sea-100 mb-2">
                AI Summarizer Pro
              </h1>
              <p className="text-deep-sea-300">
                Автоматизация конспектирования книг из PDF
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-3 bg-deep-sea-700 hover:bg-deep-sea-600 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Status Indicator */}
        <div className="mb-6 flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            servicesReady ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
          }`}>
            {servicesReady ? (
              <>
                <CheckCircle2 className="w-5 h-5" />
                <span>Сервисы готовы</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5" />
                <span>Сервисы не готовы</span>
              </>
            )}
          </div>
          {status === 'processing' && (
            <div className="flex items-center gap-2 text-deep-sea-300">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Обработка главы {currentChapter} из {totalChapters}</span>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Drag & Drop Zone */}
            {status === 'idle' && (
              <DragDropZone onFileSelect={handleFileUpload} />
            )}

            {/* Progress Bar */}
            {status === 'processing' && (
              <div className="bg-deep-sea-800/50 backdrop-blur-sm rounded-xl p-6 border border-deep-sea-700">
                <ProgressBar progress={progress} />
                <div className="mt-4 text-center text-deep-sea-300">
                  Глава {currentChapter} из {totalChapters}
                </div>
              </div>
            )}

            {/* Completed State */}
            {status === 'completed' && (
              <div className="bg-deep-sea-800/50 backdrop-blur-sm rounded-xl p-6 border border-deep-sea-700">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <CheckCircle2 className="w-8 h-8 text-green-400" />
                  <h2 className="text-2xl font-semibold text-deep-sea-100">
                    Обработка завершена!
                  </h2>
                </div>
                <button
                  onClick={handleDownloadDocx}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-deep-sea-600 hover:bg-deep-sea-500 rounded-lg transition-colors font-medium"
                >
                  <Download className="w-5 h-5" />
                  Скачать .docx
                </button>
              </div>
            )}

            {/* Error State */}
            {status === 'error' && (
              <div className="bg-red-900/20 backdrop-blur-sm rounded-xl p-6 border border-red-700">
                <div className="flex items-center gap-3 mb-2">
                  <AlertCircle className="w-6 h-6 text-red-400" />
                  <h3 className="text-xl font-semibold text-red-300">Ошибка</h3>
                </div>
                <p className="text-red-200">{errorMessage}</p>
              </div>
            )}
          </div>

          {/* Right Column - Live Preview */}
          <div>
            <LivePreview content={previewText} />
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <SettingsPanel
            config={config}
            onClose={() => setShowSettings(false)}
            onSave={async (newConfig) => {
              try {
                await axios.post(`${API_URL}/config`, newConfig)
                setConfig(newConfig)
                setShowSettings(false)
              } catch (error) {
                alert('Ошибка сохранения настроек: ' + error.message)
              }
            }}
          />
        )}
      </div>
    </div>
  )
}

export default App
