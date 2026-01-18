import React from 'react'
import { Eye } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

function LivePreview({ content }) {
  return (
    <div className="bg-deep-sea-800/50 backdrop-blur-sm rounded-xl border border-deep-sea-700 h-full flex flex-col">
      <div className="flex items-center gap-2 px-6 py-4 border-b border-deep-sea-700">
        <Eye className="w-5 h-5 text-deep-sea-400" />
        <h2 className="text-xl font-semibold text-deep-sea-100">Live Preview</h2>
      </div>
      <div className="flex-1 overflow-auto p-6">
        {content ? (
          <div className="prose prose-invert prose-headings:text-deep-sea-100 prose-p:text-deep-sea-200 prose-strong:text-deep-sea-100 prose-code:text-deep-sea-300 max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-deep-sea-500">
            <p>Конспект появится здесь после начала обработки...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LivePreview
