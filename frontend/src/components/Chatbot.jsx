import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Mic, Volume2, VolumeX, Download, FileText } from 'lucide-react'
import { useScribe } from '@elevenlabs/react'
import './Chatbot.css'

const API_BASE_URL = 'http://localhost:8000'

function Chatbot({ messages, onMessage, sessionId, onAddMessage, isLoading }) {
  const [input, setInput] = useState('')
  const [isExplaining, setIsExplaining] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [hiddenSuggestionIds, setHiddenSuggestionIds] = useState(new Set())
  const messagesEndRef = useRef(null)
  const lastSpokenMessageId = useRef(null)
  const hasUserInteracted = useRef(false)
  
  // Initialize ElevenLabs Scribe for STT
  const scribe = useScribe({
    modelId: "scribe_v2_realtime",
    onPartialTranscript: (data) => {
      // Update input with partial transcript as user speaks (live transcription)
      if (data.text) {
        setInput(data.text)
      }
    },
    onCommittedTranscript: (data) => {
      // Final transcript when speech segment is complete
      if (data.text) {
        setInput(data.text)
      }
    },
    onCommittedTranscriptWithTimestamps: (data) => {
      // Optional: Handle timestamps if needed
      console.log("Timestamps:", data.words)
    },
  })
  
  // Get the current input value (prioritize manual input, then partial transcript)
  const currentInputValue = input || scribe.partialTranscript || ''

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // TTS function to speak text
  const speak = async (text) => {
    if (isMuted) return // Don't speak if muted
    
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
        // Silently handle autoplay restrictions - user can click the audio button to play manually
        console.log('Audio autoplay blocked (requires user interaction):', error.message)
        // Don't show alert - this is expected behavior for autoplay
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

  // Handle starting/stopping ElevenLabs STT
  const handleStartListening = async () => {
    try {
      // Fetch token from backend
      const response = await fetch(`${API_BASE_URL}/api/scribe-token`)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || 'Failed to get token')
      }
      const { token } = await response.json()

      // Connect with microphone
      await scribe.connect({
        token,
        microphone: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
    } catch (error) {
      console.error('Error starting STT:', error)
      alert(`Error: ${error.message}. Make sure the backend is running and your ElevenLabs API key is configured.`)
    }
  }

  const handleStopListening = () => {
    scribe.disconnect()
  }

  // Track user interaction to enable autoplay
  useEffect(() => {
    const handleUserInteraction = () => {
      hasUserInteracted.current = true
    }

    // Listen for any user interaction
    window.addEventListener('click', handleUserInteraction, { once: true })
    window.addEventListener('keydown', handleUserInteraction, { once: true })
    window.addEventListener('touchstart', handleUserInteraction, { once: true })

    return () => {
      window.removeEventListener('click', handleUserInteraction)
      window.removeEventListener('keydown', handleUserInteraction)
      window.removeEventListener('touchstart', handleUserInteraction)
    }
  }, [])

  // Auto-play whenever Pibble sends a message (only after user interaction)
  useEffect(() => {
    if (messages.length === 0) return

    const last = messages[messages.length - 1]

    // Only speak if:
    // 1. It's from Pibble (not a user message)
    // 2. We haven't spoken this message yet
    // 3. The message has text
    // 4. User has interacted with the page (to allow autoplay)
    // 5. Not muted
    if (
      last.type !== 'user' && 
      last.id !== lastSpokenMessageId.current &&
      last.text &&
      hasUserInteracted.current &&
      !isMuted
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
    const textToSend = currentInputValue.trim()
    if (textToSend) {
      // Mark that user has interacted (enables autoplay for future messages)
      hasUserInteracted.current = true
      
      onMessage({
        id: Date.now(),
        type: 'user',
        text: textToSend,
      })
      setInput('')
      // Disconnect STT if connected
      if (scribe.isConnected) {
        scribe.disconnect()
      }
    }
  }

  const handleSuggestion = (suggestion, messageId) => {
    // Mark that user has interacted (enables autoplay for future messages)
    hasUserInteracted.current = true
    
    // Hide suggestions for this message
    setHiddenSuggestionIds(prev => new Set([...prev, messageId]))
    
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
            src="/assets/images/logos/pibble2.png" 
            alt="Pibble" 
            className="pibble-avatar"
          />
          <div className="chatbot-title-text">
            <h2>I am Pibble.</h2>
            <p className="chatbot-caption">wash my belly.</p>
          </div>
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
              <div className="message-content">
                <div className="message-text-wrapper">
                <p>{message.text}</p>
                  {message.type !== 'user' && message.text && (
                    <motion.button
                      className="audio-button"
                      onClick={() => {
                        if (isMuted) {
                          setIsMuted(false)
                          // Small delay to ensure state updates before speaking
                          setTimeout(() => speak(message.text), 50)
                        } else {
                          setIsMuted(true)
                        }
                      }}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title={isMuted ? "Unmute and play audio" : "Mute Pibble"}
                    >
                      {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </motion.button>
                  )}
                </div>
                {message.suggestions && (
                  <AnimatePresence>
                    {!hiddenSuggestionIds.has(message.id) && (
                      <motion.div 
                        key={`suggestions-${message.id}`}
                        className="suggestions"
                        initial={{ opacity: 1 }}
                        exit={{ opacity: 0, transition: { duration: 0.3 } }}
                      >
                        {message.suggestions.map((suggestion, idx) => (
                          <motion.button
                            key={idx}
                            className="suggestion-button"
                            onClick={() => handleSuggestion(suggestion, message.id)}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20, transition: { duration: 0.2 } }}
                            transition={{ delay: idx * 0.1 }}
                          >
                            {suggestion}
                          </motion.button>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
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

      <AnimatePresence>
        {isLoading && (
          <motion.div
            key="thinking"
            className="thinking-indicator"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <p className="thinking-text">
              Pibble is thinking
              <span className="thinking-dots">
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
              </span>
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="chatbot-input">
        <div className="chat-input-wrapper">
          <motion.button
            className="mic-button"
            onClick={() => {
              if (scribe.isConnected) {
                handleStopListening()
              } else {
                handleStartListening()
              }
            }}
            whileTap={{ scale: 0.95 }}
            style={{
              background: scribe.isConnected ? 'rgba(255, 77, 77, 0.2)' : 'var(--bg-secondary)',
              color: scribe.isConnected ? '#ff6b6b' : 'var(--text-muted)'
            }}
          >
            <Mic size={18} />
          </motion.button>
        <input
          type="text"
          value={currentInputValue}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={scribe.isConnected ? "Listening..." : "Ask Pibble for help..."}
          className="chat-input"
        />
        <motion.button
          className="send-button"
          onClick={handleSend}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          disabled={!currentInputValue.trim()}
        >
          <Send size={18} />
        </motion.button>
        </div>
      </div>
    </div>
  )
}

export default Chatbot

