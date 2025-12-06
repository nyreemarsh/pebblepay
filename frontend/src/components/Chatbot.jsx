import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, User, Mic, Download, FileText } from 'lucide-react'
import './Chatbot.css'

const API_BASE_URL = 'http://localhost:8000'

function Chatbot({ messages, onMessage, sessionId, onAddMessage }) {
  const [input, setInput] = useState('')
  const [isExplaining, setIsExplaining] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (input.trim()) {
      onMessage({
        id: Date.now(),
        type: 'user',
        text: input,
      })
      setInput('')
    }
  }

  const handleSuggestion = (suggestion) => {
    onMessage({
      id: Date.now(),
      type: 'user',
      text: suggestion,
    })
  }

  const handleDownloadPdf = async () => {
    if (!sessionId) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/download-contract`)
      if (!response.ok) throw new Error('Failed to download')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'contract.pdf'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download error:', error)
    }
  }

  const handleExplainContract = async () => {
    if (!sessionId || isExplaining) return
    
    setIsExplaining(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/explain-contract`)
      if (!response.ok) throw new Error('Failed to get explanation')
      
      const data = await response.json()
      
      // Add the explanation as a new message
      if (onAddMessage && data.explanation) {
        onAddMessage({
          id: Date.now(),
          type: 'suggestion',
          text: `📋 **Here's your contract explained:**\n\n${data.explanation}`,
        })
      }
    } catch (error) {
      console.error('Explain error:', error)
    } finally {
      setIsExplaining(false)
    }
  }

  return (
    <div className="chatbot">
      <div className="chatbot-header">
        <div className="chatbot-title">
          <img 
            src="/assets/images/logos/i_am_big_pibble.png" 
            alt="Pibble" 
            className="pibble-avatar"
          />
          <h2>I am Pibble.</h2>
        </div>
      </div>

      <div className="chatbot-messages">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              className={`message ${message.type}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {message.type === 'suggestion' && (
                <div className="message-icon">
                  <img 
                    src="/assets/images/logos/i_am_big_pibble.png" 
                    alt="Pibble" 
                    className="message-pibble-icon"
                  />
                </div>
              )}
              {message.type === 'user' && (
                <div className="message-icon user-icon">
                  <User size={16} />
                </div>
              )}
              <div className="message-content">
                <p>{message.text}</p>
                {message.suggestions && (
                  <div className="suggestions">
                    {message.suggestions.map((suggestion, idx) => (
                      <motion.button
                        key={idx}
                        className="suggestion-button"
                        onClick={() => handleSuggestion(suggestion)}
                        whileTap={{ scale: 0.95 }}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                      >
                        {suggestion}
                      </motion.button>
                    ))}
                  </div>
                )}
                {message.contractReady && (
                  <div className="contract-actions">
                    <motion.button
                      className="action-button download-btn"
                      onClick={handleDownloadPdf}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      <Download size={18} />
                      Download PDF
                    </motion.button>
                    <motion.button
                      className="action-button explain-btn"
                      onClick={handleExplainContract}
                      disabled={isExplaining}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      <FileText size={18} />
                      {isExplaining ? 'Loading...' : 'Explain Contract'}
                    </motion.button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbot-input">
        <div className="chat-input-wrapper">
          <motion.button
            className="mic-button"
            onClick={() => {
              // Voice input handler - to be implemented
              console.log('Voice input clicked')
            }}
            whileTap={{ scale: 0.95 }}
          >
            <Mic size={18} />
          </motion.button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Pibble for help..."
            className="chat-input"
          />
          <motion.button
            className="send-button"
            onClick={handleSend}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!input.trim()}
          >
            <Send size={18} />
          </motion.button>
        </div>
      </div>
    </div>
  )
}

export default Chatbot

