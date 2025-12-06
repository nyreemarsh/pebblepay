import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, User, Mic } from 'lucide-react'
import './Chatbot.css'

function Chatbot({ messages, onMessage }) {
  const [input, setInput] = useState('')
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

