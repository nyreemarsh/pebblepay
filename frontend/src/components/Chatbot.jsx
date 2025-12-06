import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, User, Mic, Volume2 } from 'lucide-react'
import './Chatbot.css'

function Chatbot({ messages, onMessage }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const lastSpokenMessageId = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // TTS function to speak text
  const speak = async (text) => {
    try {
      console.log('Sending TTS request for:', text)
      const response = await fetch("http://localhost:8000/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        console.error('TTS request failed:', response.status, errorData.detail || response.statusText)
        alert(`TTS Error: ${errorData.detail || response.statusText}`)
        return
      }

      const audioData = await response.arrayBuffer()
      const audioBlob = new Blob([audioData], { type: "audio/mpeg" })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      console.log('Playing audio...')
      audio.play().catch((error) => {
        console.error('Error playing audio:', error)
        alert(`Audio playback error: ${error.message}. Make sure your browser allows audio autoplay.`)
      })

      // Clean up the URL after playback
      audio.addEventListener('ended', () => {
        URL.revokeObjectURL(audioUrl)
        console.log('Audio playback finished')
      })
    } catch (error) {
      console.error('Error with TTS:', error)
      alert(`TTS Error: ${error.message}. Make sure the backend is running on http://localhost:8000`)
    }
  }

  // Auto-play whenever Pibble sends a message (including initial message on mount)
  useEffect(() => {
    if (messages.length === 0) return

    const last = messages[messages.length - 1]

    // Only speak if:
    // 1. It's from Pibble (not a user message)
    // 2. We haven't spoken this message yet
    // 3. The message has text
    if (
      last.type !== 'user' && 
      last.id !== lastSpokenMessageId.current &&
      last.text
    ) {
      lastSpokenMessageId.current = last.id
      // Small delay to ensure component is fully mounted
      setTimeout(() => {
        speak(last.text)
      }, 100)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
                <div className="message-text-wrapper">
                <p>{message.text}</p>
                  {message.type !== 'user' && message.text && (
                    <motion.button
                      className="audio-button"
                      onClick={() => speak(message.text)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title="Play audio"
                    >
                      <Volume2 size={16} />
                    </motion.button>
                  )}
                </div>
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

