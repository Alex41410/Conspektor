import React from 'react'

function ProgressBar({ progress }) {
  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-deep-sea-300">Прогресс</span>
        <span className="text-sm font-medium text-deep-sea-300">{progress}%</span>
      </div>
      <div className="w-full bg-deep-sea-700 rounded-full h-3 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-deep-sea-500 via-deep-sea-400 to-deep-sea-300 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
          style={{ width: `${progress}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
        </div>
      </div>
    </div>
  )
}

export default ProgressBar
