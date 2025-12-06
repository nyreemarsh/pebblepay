import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import BlockPalette from './components/BlockPalette'
import Canvas from './components/Canvas'
import Chatbot from './components/Chatbot'
import GenerateButton from './components/GenerateButton'
import './App.css'

import NodeEditor from './components/NodeEditor'

// API base URL - adjust if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [blocks, setBlocks] = useState([])
  const [edges, setEdges] = useState([])
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [contractData, setContractData] = useState(null)
  
  // Resizable panel width for right sidebar
  const [rightWidth, setRightWidth] = useState(350)
  const [isResizingRight, setIsResizingRight] = useState(false)
  const resizeRightRef = useRef(null)

  // Fetch opening message on mount
  useEffect(() => {
    const fetchOpeningMessage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/opening-message`)
        const data = await response.json()
        
        setChatMessages([
          {
            id: Date.now(),
            type: 'suggestion',
            text: data.message,
            suggestions: [
              "I'm designing a logo for a client",
              "I'm doing freelance writing work",
              "I'm providing consulting services",
              "I'm building a website"
            ]
          }
        ])
      } catch (error) {
        console.error('Error fetching opening message:', error)
        // Fallback message
        setChatMessages([
          {
            id: Date.now(),
            type: 'suggestion',
            text: "Hi there! 👋 I'm Pibble, your friendly contract assistant.\n\nHere's how I work: I'll ask you a few simple questions about your project, and then I'll create a comprehensive contract that protects both you and your client. I'll cover everything from payment terms to what happens if things don't go as planned.\n\nLet's get started! Tell me a bit about what you're working on - who's your client and what will you be delivering?",            suggestions: [
              "I'm designing a logo for a client",
              "I'm doing freelance writing work",
              "I'm providing consulting services",
              "I'm building a website"
            ]
          }
        ])
      }
    }
    
    fetchOpeningMessage()
  }, [])

  const handleAddBlock = (blockType) => {
    const newBlock = {
      id: `block-${Date.now()}`,
      type: blockType,
      position: { x: Math.random() * 400 + 200, y: Math.random() * 300 + 100 },
      data: { label: blockType, content: '' }
    }
    setBlocks([...blocks, newBlock])
  }

  const handleBlocksChange = (updatedBlocks) => {
    setBlocks(updatedBlocks)
  }

  const handleDeleteBlock = (blockId) => {
    // Remove the block
    const updatedBlocks = blocks.filter((block) => block.id !== blockId)
    setBlocks(updatedBlocks)
    
    // Remove all edges connected to this block
    const updatedEdges = edges.filter(
      (edge) => edge.from !== blockId && edge.to !== blockId
    )
    setEdges(updatedEdges)
  }

  const handleNodeUpdate = (nodeId, updatedNode) => {
    const updatedBlocks = blocks.map((block) =>
      block.id === nodeId ? updatedNode : block
    )
    setBlocks(updatedBlocks)
  }

  const handleChatMessage = async (message) => {
    // Add user message to chat immediately
    const userMessage = {
      ...message,
      type: 'user',
    }
    setChatMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call the backend API
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.text,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Store session ID if this is a new session
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }

      // Store contract data if available
      if (data.contract_spec || data.contract_text) {
        setContractData({
          spec: data.contract_spec,
          text: data.contract_text,
          summary: data.summary,
        })
      }

      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now(),
        type: 'suggestion',
        text: data.response,
        suggestions: data.suggestions || undefined,
        contractReady: data.contract_ready || false,
      }
      setChatMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      // Show error message to user
      const errorMessage = {
        id: Date.now(),
        type: 'suggestion',
        text: "Sorry, I encountered an error. Please try again or check if the backend server is running.",
      }
      setChatMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerate = () => {
    console.log('Generating smart contract with blocks:', blocks)
    console.log('Edges:', edges)
    // This will be connected to backend later
  }

  // Resize handlers for right sidebar
  const handleMouseDownRight = useCallback((e) => {
    e.preventDefault()
    setIsResizingRight(true)
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!isResizingRight) return

    const containerWidth = window.innerWidth - 32 // Account for padding
    const minWidth = 250
    const maxRightWidth = containerWidth * 0.5

    if (isResizingRight) {
      const newWidth = containerWidth - e.clientX - 16 // Account for padding
      if (newWidth >= minWidth && newWidth <= maxRightWidth) {
        setRightWidth(newWidth)
      }
    }
  }, [isResizingRight])

  const handleMouseUp = useCallback(() => {
    setIsResizingRight(false)
  }, [])

  useEffect(() => {
    if (isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizingRight, handleMouseMove, handleMouseUp])

  // Handler to add messages directly (for explain contract)
  const handleAddMessage = (message) => {
    setChatMessages((prev) => [...prev, message])
  }

  return (
    <div className="app">
      <div className="app-content">
        {/* Left Sidebar - Block Palette */}
        <motion.div 
          className="sidebar-left"
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <BlockPalette onAddBlock={handleAddBlock} />
        </motion.div>

        {/* Center - Canvas */}
        <div className="canvas-container">
          <div className="canvas-area">
          <Canvas 
            blocks={blocks} 
            onBlocksChange={handleBlocksChange}
            onNodeSelect={setSelectedNodeId}
            selectedNodeId={selectedNodeId}
            edges={edges}
            onEdgesChange={setEdges}
            onDeleteBlock={handleDeleteBlock}
          />
          </div>
          {/* Generate Button - Separate from canvas, underneath */}
          <div className="generate-button-container-wrapper">
            <GenerateButton 
              onClick={handleGenerate}
              disabled={blocks.length === 0}
            />
          </div>
        </div>

        {/* Node Editor (slides in when node is selected) */}
        {selectedNodeId && (
          <NodeEditor
            node={blocks.find((b) => b.id === selectedNodeId)}
            onUpdate={handleNodeUpdate}
            onClose={() => setSelectedNodeId(null)}
          />
        )}

        {/* Right Resize Handle */}
        <div
          className="resize-handle resize-handle-right"
          onMouseDown={handleMouseDownRight}
          ref={resizeRightRef}
        />

        {/* Right Sidebar - Chatbot */}
        <motion.div 
          className="sidebar-right"
          style={{ width: `${rightWidth}px` }}
          initial={{ x: 300 }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 100 }}
        >
          <Chatbot 
            messages={chatMessages}
            onMessage={handleChatMessage}
            sessionId={sessionId}
            onAddMessage={handleAddMessage}
            isLoading={isLoading}
          />
        </motion.div>
      </div>
    </div>
  )
}

export default App

