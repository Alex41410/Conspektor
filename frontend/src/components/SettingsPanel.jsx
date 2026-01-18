import React, { useState, useEffect } from 'react'
import { X } from 'lucide-react'

function SettingsPanel({ config, onClose, onSave }) {
  const [localConfig, setLocalConfig] = useState(config || {})

  useEffect(() => {
    setLocalConfig(config || {})
  }, [config])

  const handleChange = (key, value) => {
    setLocalConfig(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = () => {
    onSave(localConfig)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-deep-sea-800 rounded-xl border border-deep-sea-700 w-full max-w-2xl max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between p-6 border-b border-deep-sea-700">
          <h2 className="text-2xl font-semibold text-deep-sea-100">Настройки</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-deep-sea-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2">
              Директория для сохранения
            </label>
            <input
              type="text"
              value={localConfig.output_dir || ''}
              onChange={(e) => handleChange('output_dir', e.target.value)}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2">
              Порт LM Studio
            </label>
            <input
              type="number"
              value={localConfig.lm_studio_port || 1234}
              onChange={(e) => handleChange('lm_studio_port', parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2">
              URL LM Studio
            </label>
            <input
              type="text"
              value={localConfig.lm_studio_url || 'http://localhost:1234'}
              onChange={(e) => handleChange('lm_studio_url', e.target.value)}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2">
              Имя модели LM Studio
            </label>
            <input
              type="text"
              value={localConfig.lm_studio_model || 'local-model'}
              onChange={(e) => handleChange('lm_studio_model', e.target.value)}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2">
              Максимальный размер чанка (символов)
            </label>
            <input
              type="number"
              value={localConfig.max_chunk_size || 15000}
              onChange={(e) => handleChange('max_chunk_size', parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-deep-sea-300 mb-2 mb-4">
              Ключевые слова для нарезки (через запятую)
            </label>
            <input
              type="text"
              value={localConfig.split_keywords?.join(', ') || ''}
              onChange={(e) => handleChange('split_keywords', e.target.value.split(',').map(s => s.trim()))}
              className="w-full px-4 py-2 bg-deep-sea-900 border border-deep-sea-600 rounded-lg text-deep-sea-100 focus:outline-none focus:border-deep-sea-400"
              placeholder="Глава, Раздел, Тема"
            />
          </div>
        </div>

        <div className="flex justify-end gap-4 p-6 border-t border-deep-sea-700">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-deep-sea-700 hover:bg-deep-sea-600 rounded-lg transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-deep-sea-600 hover:bg-deep-sea-500 rounded-lg transition-colors font-medium"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsPanel
